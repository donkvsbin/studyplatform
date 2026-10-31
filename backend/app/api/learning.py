import hashlib
import json
import math
import re

from flask import Blueprint, request
from flask_login import current_user
from sqlalchemy.orm import lazyload

from .common import ApiError, ok, payload, protected
from ..extensions import db
from ..models import LessonProgress, Quiz, QuizAttempt, QuizAttemptAnswer, utcnow
from ..services.catalog import integer_arg, language, public_course, translated
from ..services.learning import (
    course_lesson,
    enrolled_course,
    lock_writes,
    progress_data,
    serialize_attempt,
    summary,
)

bp = Blueprint("learning", __name__, url_prefix="/api/v1")


@bp.get("/courses/<int:course_id>/lessons/<int:lesson_id>")
@protected()
def lesson(course_id, lesson_id):
    course = enrolled_course(course_id, current_user.id)
    row = course_lesson(course, lesson_id)
    lang = language()
    progress = db.session.scalar(
        db.select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    return ok(
        {
            "lesson": {
                "id": row.id,
                "course_id": course_id,
                "chapter_id": row.chapter_id,
                "title": translated(row, "title", lang),
                "body": translated(row, "body", lang),
                "video_url": row.video_url,
                "duration_minutes": row.duration_minutes,
                "progress": progress_data(progress),
            },
            "course": public_course(course, lang, detail=True),
            "summary": summary(course, current_user.id),
        }
    )


@bp.put("/courses/<int:course_id>/lessons/<int:lesson_id>/progress")
@protected()
def update_progress(course_id, lesson_id):
    data = payload()
    if "completed" in data and type(data["completed"]) is not bool:
        raise ApiError("invalid_progress")
    position = data.get("video_position")
    if position is not None and (
        type(position) not in (int, float)
        or not math.isfinite(position)
        or not 0 <= position <= 86400
    ):
        raise ApiError("invalid_progress")
    lock_writes()
    course = enrolled_course(course_id, current_user.id)
    course_lesson(course, lesson_id)
    progress = db.session.scalar(
        db.select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    if progress is None:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(progress)
    if "completed" in data:
        progress.completed = data["completed"]
        progress.completed_at = (
            (progress.completed_at or utcnow()) if data["completed"] else None
        )
    if position is not None:
        progress.video_position = position
    progress.last_visited_at = utcnow()
    db.session.commit()
    return ok(
        {
            "progress": progress_data(progress),
            "summary": summary(course, current_user.id),
        }
    )


@bp.get("/courses/<int:course_id>/quiz")
@protected()
def get_quiz(course_id):
    course = enrolled_course(course_id, current_user.id)
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course_id))
    if quiz is None:
        raise ApiError("not_found", 404)
    lang = language()
    questions = [row for row in quiz.questions if not row.archived]
    return ok(
        {
            "id": quiz.id,
            "course_id": course_id,
            "course_title": translated(course, "title", lang),
            "title": translated(quiz, "title", lang),
            "version": quiz.version,
            "pass_threshold": quiz.pass_threshold,
            "questions": [
                {
                    "id": row.id,
                    "prompt": translated(row, "prompt", lang),
                    "options": [
                        {
                            "id": option["id"],
                            "text": option.get("text_en") or option["text_zh"]
                            if lang == "en"
                            else option["text_zh"],
                        }
                        for option in row.options
                    ],
                }
                for row in questions
            ],
            "summary": summary(course, current_user.id),
        }
    )


@bp.post("/courses/<int:course_id>/quiz/attempts")
@protected()
def submit_quiz(course_id):
    data = payload()
    submission_id, version, answers = (
        data.get("submission_id"),
        data.get("version"),
        data.get("answers"),
    )
    if (
        not isinstance(submission_id, str)
        or not re.fullmatch(r"[a-zA-Z0-9_-]{8,64}", submission_id)
        or type(version) is not int
        or not isinstance(answers, dict)
    ):
        raise ApiError("invalid_answers")
    request_hash = hashlib.sha256(
        json.dumps(
            {"version": version, "answers": answers}, sort_keys=True, ensure_ascii=True
        ).encode()
    ).hexdigest()
    lock_writes()
    course = enrolled_course(course_id, current_user.id)
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course_id))
    if quiz is None:
        raise ApiError("not_found", 404)
    existing = db.session.scalar(
        db.select(QuizAttempt).where(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.submission_id == submission_id,
        )
    )
    if existing:
        if existing.request_hash != request_hash:
            raise ApiError("submission_conflict", 409)
        return ok(serialize_attempt(existing, language(), True))
    if quiz.version != version:
        raise ApiError("quiz_changed", 409)
    questions = [row for row in quiz.questions if not row.archived]
    if not questions or set(answers) != {str(row.id) for row in questions}:
        raise ApiError("invalid_answers")
    for row in questions:
        if answers[str(row.id)] not in [option["id"] for option in row.options]:
            raise ApiError("invalid_answers")
    count = sum(answers[str(row.id)] == row.correct_option_id for row in questions)
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        version=version,
        submission_id=submission_id,
        request_hash=request_hash,
        correct_count=count,
        total_count=len(questions),
        score=round(count * 100 / len(questions), 2),
        passed=count * 100 >= len(questions) * quiz.pass_threshold,
        context_snapshot={
            "course_id": course_id,
            "course_title_zh": course.title_zh,
            "course_title_en": course.title_en,
            "quiz_title_zh": quiz.title_zh,
            "quiz_title_en": quiz.title_en,
        },
    )
    db.session.add(attempt)
    db.session.flush()
    for row in questions:
        db.session.add(
            QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=row.id,
                selected_option_id=answers[str(row.id)],
                is_correct=answers[str(row.id)] == row.correct_option_id,
                snapshot={
                    "prompt_zh": row.prompt_zh,
                    "prompt_en": row.prompt_en,
                    "options": row.options,
                    "correct_option_id": row.correct_option_id,
                    "explanation_zh": row.explanation_zh,
                    "explanation_en": row.explanation_en,
                },
            )
        )
    db.session.commit()
    return ok(serialize_attempt(attempt, language(), True), 201)


@bp.get("/me/quiz-attempts")
@protected()
def attempts():
    page, per_page = integer_arg("page", 1, 100000), integer_arg("per_page", 20, 24)
    query = (
        db.select(QuizAttempt)
        .options(lazyload(QuizAttempt.answers))
        .where(QuizAttempt.user_id == current_user.id)
    )
    if request.args.get("course_id"):
        query = query.join(Quiz).where(Quiz.course_id == integer_arg("course_id", 1))
    total = db.session.scalar(db.select(db.func.count()).select_from(query.subquery()))
    rows = db.session.scalars(
        query.order_by(QuizAttempt.submitted_at.desc(), QuizAttempt.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()
    return ok(
        [serialize_attempt(row, language()) for row in rows],
        pagination={
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": math.ceil(total / per_page),
        },
    )


@bp.get("/me/quiz-attempts/<int:attempt_id>")
@protected()
def attempt_detail(attempt_id):
    attempt = db.session.get(QuizAttempt, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise ApiError("not_found", 404)
    return ok(serialize_attempt(attempt, language(), True))

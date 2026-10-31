from ..api.common import ApiError
from ..extensions import db
from ..models import Enrollment, LessonProgress, Quiz, QuizAttempt
from .catalog import published_course


def iso(value):
    return value.isoformat() + ("Z" if value.tzinfo is None else "") if value else None


def effective_lessons(course):
    return [
        lesson
        for chapter in course.chapters
        if not chapter.archived
        for lesson in chapter.lessons
        if not lesson.archived
    ]


def enrolled_course(course_id, user_id):
    course = published_course(course_id)
    if not db.session.scalar(
        db.select(Enrollment.id).where(
            Enrollment.course_id == course_id, Enrollment.user_id == user_id
        )
    ):
        raise ApiError("enrollment_required", 403)
    return course


def course_lesson(course, lesson_id):
    lesson = next(
        (lesson for lesson in effective_lessons(course) if lesson.id == lesson_id), None
    )
    if lesson is None:
        raise ApiError("not_found", 404)
    return lesson


def progress_data(progress):
    return {
        "completed": bool(progress and progress.completed),
        "completed_at": iso(progress.completed_at) if progress else None,
        "video_position": progress.video_position if progress else 0,
        "last_visited_at": iso(progress.last_visited_at) if progress else None,
    }


def summary(course, user_id):
    lessons = effective_lessons(course)
    ids = [lesson.id for lesson in lessons]
    rows = (
        db.session.scalars(
            db.select(LessonProgress)
            .where(LessonProgress.user_id == user_id, LessonProgress.lesson_id.in_(ids))
            .order_by(LessonProgress.last_visited_at.desc(), LessonProgress.id.desc())
        ).all()
        if ids
        else []
    )
    completed_ids = [row.lesson_id for row in rows if row.completed]
    attempts = db.session.execute(
        db.select(QuizAttempt.score, QuizAttempt.passed)
        .join(Quiz)
        .where(Quiz.course_id == course.id, QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.submitted_at.desc(), QuizAttempt.id.desc())
    ).all()
    passed = any(attempt.passed for attempt in attempts)
    all_done = bool(ids) and len(completed_ids) == len(ids)
    state = (
        "completed"
        if all_done and passed
        else "quiz_required"
        if all_done
        else "in_progress"
        if rows
        else "not_started"
    )
    resume_id = rows[0].lesson_id if rows else (ids[0] if ids else None)
    return {
        "completed_count": len(completed_ids),
        "total_count": len(ids),
        "percent": round(len(completed_ids) * 100 / len(ids)) if ids else 0,
        "completed_lesson_ids": completed_ids,
        "resume_lesson_id": resume_id,
        "state": state,
        "quiz_passed": passed,
        "latest_score": attempts[0].score if attempts else None,
        "best_score": max((attempt.score for attempt in attempts), default=None),
    }


def serialize_attempt(attempt, lang, detail=False):
    context = attempt.context_snapshot

    def display(value, name):
        return value.get(name + ("_en" if lang == "en" else "_zh")) or value.get(
            name + "_zh", ""
        )

    result = {
        "id": attempt.id,
        "quiz_id": attempt.quiz_id,
        "course_id": context["course_id"],
        "title": display(context, "quiz_title"),
        "course_title": display(context, "course_title"),
        "version": attempt.version,
        "correct_count": attempt.correct_count,
        "total_count": attempt.total_count,
        "score": attempt.score,
        "passed": attempt.passed,
        "submitted_at": iso(attempt.submitted_at),
    }
    if detail:
        result["answers"] = [
            {
                "question_id": row.question_id,
                "prompt": display(row.snapshot, "prompt"),
                "options": [
                    {"id": option["id"], "text": display(option, "text")}
                    for option in row.snapshot["options"]
                ],
                "correct_option_id": row.snapshot["correct_option_id"],
                "selected_option_id": row.selected_option_id,
                "is_correct": row.is_correct,
                "explanation": display(row.snapshot, "explanation"),
            }
            for row in attempt.answers
        ]
    return result


def lock_writes():
    # Keep the quiz version, questions and grading snapshot consistent with concurrent edits.
    connection = db.session.connection()
    if (
        connection.dialect.name == "sqlite"
        and not connection.connection.driver_connection.in_transaction
    ):
        connection.exec_driver_sql("BEGIN IMMEDIATE")

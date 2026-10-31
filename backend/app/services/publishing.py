from pathlib import Path

from .learning import effective_lessons
from ..config import BACKEND
from ..extensions import db
from ..models import Quiz


def publication_errors(course):
    errors = []
    if course.archived or course.category.archived:
        errors.append("archived_content")
    for name in ("title", "description"):
        if not all(getattr(course, name + "_" + lang).strip() for lang in ("zh", "en")):
            errors.append("course_bilingual_required")
    if not course.objectives_zh or not course.objectives_en:
        errors.append("objectives_required")
    chapters = [chapter for chapter in course.chapters if not chapter.archived]
    if not chapters or not effective_lessons(course):
        errors.append("lessons_required")
    for chapter in chapters:
        if (
            not chapter.title_zh.strip()
            or not chapter.title_en.strip()
            or not any(not row.archived for row in chapter.lessons)
        ):
            errors.append("chapter_content_required")
        for lesson in chapter.lessons:
            if lesson.archived:
                continue
            if not all(
                getattr(lesson, name + "_" + lang).strip()
                for name in ("title", "body")
                for lang in ("zh", "en")
            ):
                errors.append("lesson_bilingual_required")
            if lesson.video_url:
                asset = (
                    BACKEND.parent / "frontend/public" / lesson.video_url.lstrip("/")
                ).resolve()
                root = (BACKEND.parent / "frontend/public/demo").resolve()
                if not asset.is_relative_to(root) or not asset.is_file():
                    errors.append("video_missing")
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course.id))
    if not quiz or not quiz.title_zh.strip() or not quiz.title_en.strip():
        errors.append("quiz_required")
    questions = [row for row in quiz.questions if not row.archived] if quiz else []
    if len(questions) < 3:
        errors.append("questions_required")
    for question in questions:
        if not all(
            getattr(question, name + "_" + lang).strip()
            for name in ("prompt", "explanation")
            for lang in ("zh", "en")
        ):
            errors.append("question_bilingual_required")
        if (
            len(question.options) < 2
            or question.correct_option_id
            not in [option["id"] for option in question.options]
            or any(
                not option.get("text_" + lang, "").strip()
                for option in question.options
                for lang in ("zh", "en")
            )
        ):
            errors.append("question_options_required")
    return list(dict.fromkeys(errors))

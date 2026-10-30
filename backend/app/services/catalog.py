from flask import request
from .validation import locale
from ..api.common import ApiError
from ..extensions import db
from ..models import Course


def language():
    return locale(request.args.get("lang", "zh-CN"))


def translated(obj, field, lang):
    return getattr(obj, f"{field}_en" if lang == "en" else f"{field}_zh") or getattr(
        obj, f"{field}_zh"
    )


def available(course):
    return (
        course.status == "published"
        and not course.archived
        and not course.category.archived
    )


def published_course(course_id):
    course = db.session.get(Course, course_id)
    if not course or not available(course):
        raise ApiError("course_unavailable", 404)
    return course


def public_category(category, lang):
    return {
        "id": category.id,
        "slug": category.slug,
        "name": translated(category, "name", lang),
    }


def public_course(course, lang, detail=False):
    chapters = [c for c in course.chapters if not c.archived]
    lessons = [l for c in chapters for l in c.lessons if not l.archived]
    result = {
        "id": course.id,
        "slug": course.slug,
        "title": translated(course, "title", lang),
        "description": translated(course, "description", lang),
        "category": public_category(course.category, lang),
        "difficulty": course.difficulty,
        "cover_kind": course.cover_kind,
        "lesson_count": len(lessons),
        "chapter_count": len(chapters),
        "duration_minutes": sum(l.duration_minutes for l in lessons),
    }
    if detail:
        result["objectives"] = translated(course, "objectives", lang)
        result["chapters"] = [
            {
                "id": c.id,
                "title": translated(c, "title", lang),
                "lessons": [
                    {
                        "id": l.id,
                        "title": translated(l, "title", lang),
                        "duration_minutes": l.duration_minutes,
                    }
                    for l in c.lessons
                    if not l.archived
                ],
            }
            for c in chapters
        ]
    return result


def integer_arg(name, default, maximum=None):
    value = request.args.get(name, str(default))
    if (
        len(value) > 9
        or not value.isascii()
        or not value.isdecimal()
        or int(value) < 1
        or (maximum and int(value) > maximum)
    ):
        raise ApiError("invalid_query")
    return int(value)

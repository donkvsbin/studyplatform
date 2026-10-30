import re
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from .common import ApiError, ok, payload, protected
from ..extensions import db
from ..models import Category, Chapter, Course, Lesson
from ..services.validation import text_field

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def fetch(model, row_id, **parents):
    row = db.session.get(model, row_id)
    if not row or any(getattr(row, k) != v for k, v in parents.items()):
        raise ApiError("not_found", 404)
    return row


def serialize(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def commit(row, status=200):
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("invalid_content", 409)
    return ok(serialize(row), status)


def apply_fields(row, data, creating=False):
    # Publishing is deliberately unavailable until the validation workflow in batch 5.
    if "status" in data and data["status"] != "draft":
        raise ApiError("invalid_content")
    limits = {
        "slug": 80,
        "name_zh": 80,
        "name_en": 80,
        "title_zh": 160,
        "title_en": 160,
        "description_zh": 10000,
        "description_en": 10000,
        "body_zh": 50000,
        "body_en": 50000,
    }
    for key, maximum in limits.items():
        if hasattr(row, key) and (
            key in data or (creating and key.startswith(("slug", "name_", "title_")))
        ):
            value = text_field(data, key, maximum=maximum)
            if key == "slug" and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
                raise ApiError("invalid_content")
            setattr(row, key, value)
    for key in ("sort_order", "duration_minutes"):
        if hasattr(row, key) and key in data:
            value = data[key]
            if (
                type(value) is not int
                or not (0 if key == "sort_order" else 1) <= value <= 10000
            ):
                raise ApiError("invalid_content")
            setattr(row, key, value)
    if isinstance(row, Course):
        if creating or "category_id" in data:
            category_id = data.get("category_id")
            if type(category_id) is not int or fetch(Category, category_id).archived:
                raise ApiError("invalid_content")
            row.category_id = category_id
        for key in ("objectives_zh", "objectives_en"):
            if key in data:
                if (
                    not isinstance(data[key], list)
                    or len(data[key]) > 20
                    or any(
                        not isinstance(x, str) or not x.strip() or len(x) > 500
                        for x in data[key]
                    )
                ):
                    raise ApiError("invalid_content")
                setattr(row, key, data[key])
        for key, choices in [
            ("difficulty", ("beginner", "intermediate", "advanced")),
            ("cover_kind", ("web", "javascript", "python")),
        ]:
            if key in data:
                if data[key] not in choices:
                    raise ApiError("invalid_content")
                setattr(row, key, data[key])
    if isinstance(row, Lesson) and "video_url" in data:
        value = data["video_url"]
        if value is not None and (
            not isinstance(value, str)
            or not re.fullmatch(r"/demo/[a-zA-Z0-9_/-]+\.(mp4|webm)", value)
            or ".." in value
        ):
            raise ApiError("invalid_content")
        row.video_url = value


@bp.route("/categories", methods=["GET", "POST"])
@protected(admin=True)
def categories():
    if request.method == "GET":
        return ok(
            [
                serialize(row)
                for row in db.session.scalars(
                    db.select(Category).order_by(Category.sort_order, Category.id)
                ).all()
            ]
        )
    row = Category()
    apply_fields(row, payload(), True)
    db.session.add(row)
    return commit(row, 201)


@bp.patch("/categories/<int:row_id>")
@protected(admin=True)
def update_category(row_id):
    row = fetch(Category, row_id)
    apply_fields(row, payload())
    return commit(row)


@bp.route("/courses", methods=["GET", "POST"])
@protected(admin=True)
def courses():
    if request.method == "GET":
        return ok(
            [
                serialize(row)
                for row in db.session.scalars(
                    db.select(Course).order_by(Course.id)
                ).all()
            ]
        )
    row = Course()
    apply_fields(row, payload(), True)
    db.session.add(row)
    return commit(row, 201)


@bp.route("/courses/<int:course_id>", methods=["GET", "PATCH"])
@protected(admin=True)
def course(course_id):
    row = fetch(Course, course_id)
    if request.method == "PATCH":
        apply_fields(row, payload())
        return commit(row)
    result = serialize(row)
    result["chapters"] = [
        {**serialize(c), "lessons": [serialize(l) for l in c.lessons]}
        for c in row.chapters
    ]
    return ok(result)


@bp.post("/courses/<int:course_id>/chapters")
@protected(admin=True)
def add_chapter(course_id):
    fetch(Course, course_id)
    row = Chapter(course_id=course_id)
    apply_fields(row, payload(), True)
    db.session.add(row)
    return commit(row, 201)


@bp.patch("/courses/<int:course_id>/chapters/<int:chapter_id>")
@protected(admin=True)
def update_chapter(course_id, chapter_id):
    row = fetch(Chapter, chapter_id, course_id=course_id)
    apply_fields(row, payload())
    return commit(row)


@bp.post("/courses/<int:course_id>/chapters/<int:chapter_id>/lessons")
@protected(admin=True)
def add_lesson(course_id, chapter_id):
    fetch(Chapter, chapter_id, course_id=course_id)
    row = Lesson(chapter_id=chapter_id)
    apply_fields(row, payload(), True)
    db.session.add(row)
    return commit(row, 201)


@bp.patch("/courses/<int:course_id>/chapters/<int:chapter_id>/lessons/<int:lesson_id>")
@protected(admin=True)
def update_lesson(course_id, chapter_id, lesson_id):
    fetch(Chapter, chapter_id, course_id=course_id)
    row = fetch(Lesson, lesson_id, chapter_id=chapter_id)
    apply_fields(row, payload())
    return commit(row)


@bp.post("/<string:resource>/<int:row_id>/archive")
@protected(admin=True)
def archive(resource, row_id):
    model = {
        "categories": Category,
        "courses": Course,
        "chapters": Chapter,
        "lessons": Lesson,
    }.get(resource)
    if model is None:
        raise ApiError("not_found", 404)
    row = fetch(model, row_id)
    row.archived = True
    return commit(row)

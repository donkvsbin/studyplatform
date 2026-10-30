from flask import Blueprint, request
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .common import ApiError, ok, protected
from ..extensions import db
from ..models import Category, Course, Enrollment
from ..services.catalog import (
    available,
    integer_arg,
    language,
    public_category,
    public_course,
    published_course,
    translated,
)

bp = Blueprint("courses", __name__, url_prefix="/api/v1")


@bp.get("/categories")
def categories():
    lang = language()
    rows = db.session.scalars(
        db.select(Category)
        .where(Category.archived.is_(False))
        .order_by(Category.sort_order, Category.id)
    ).all()
    return ok([public_category(c, lang) for c in rows])


@bp.get("/courses")
def courses():
    lang = language()
    page, per_page = integer_arg("page", 1, 100000), integer_arg("per_page", 9, 24)
    query = (
        db.select(Course)
        .join(Category)
        .where(
            Course.status == "published",
            Course.archived.is_(False),
            Category.archived.is_(False),
        )
    )
    if request.args.get("category"):
        query = query.where(Course.category_id == integer_arg("category", 1))
    if request.args.get("difficulty"):
        difficulty = request.args["difficulty"]
        if difficulty not in ("beginner", "intermediate", "advanced"):
            raise ApiError("invalid_query")
        query = query.where(Course.difficulty == difficulty)
    keyword = request.args.get("q", "").strip()
    if len(keyword) > 100:
        raise ApiError("invalid_query")
    if keyword:
        title = Course.title_en if lang == "en" else Course.title_zh
        query = query.where(title.icontains(keyword, autoescape=True))
    count = db.session.scalar(db.select(db.func.count()).select_from(query.subquery()))
    rows = db.session.scalars(
        query.order_by(Course.id).offset((page - 1) * per_page).limit(per_page)
    ).all()
    return ok(
        [public_course(c, lang) for c in rows],
        pagination={
            "page": page,
            "per_page": per_page,
            "total": count,
            "pages": (count + per_page - 1) // per_page,
        },
    )


@bp.get("/courses/<int:course_id>")
def course_detail(course_id):
    course = published_course(course_id)
    data = public_course(course, language(), detail=True)
    data["enrolled"] = bool(
        current_user.is_authenticated
        and db.session.scalar(
            db.select(Enrollment.id).where(
                Enrollment.user_id == current_user.id, Enrollment.course_id == course_id
            )
        )
    )
    return ok(data)


@bp.post("/courses/<int:course_id>/enrollment")
@protected()
def enroll(course_id):
    published_course(course_id)
    query = db.select(Enrollment).where(
        Enrollment.user_id == current_user.id, Enrollment.course_id == course_id
    )
    record = db.session.scalar(query)
    created = record is None
    if created:
        record = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            record = db.session.scalar(query)
            if not record:
                raise
            created = False
    return ok(
        {
            "id": record.id,
            "course_id": record.course_id,
            "joined_at": record.joined_at.isoformat()
            + ("Z" if record.joined_at.tzinfo is None else ""),
        },
        201 if created else 200,
    )


@bp.get("/me/enrollments")
@protected()
def my_enrollments():
    lang = language()
    rows = db.session.scalars(
        db.select(Enrollment)
        .where(Enrollment.user_id == current_user.id)
        .order_by(Enrollment.joined_at.desc(), Enrollment.id.desc())
    ).all()
    result = []
    for row in rows:
        course = row.course
        visible = available(course)
        data = (
            public_course(course, lang)
            if visible
            else {"id": course.id, "title": translated(course, "title", lang)}
        )
        result.append(
            {
                "id": row.id,
                "joined_at": row.joined_at.isoformat()
                + ("Z" if row.joined_at.tzinfo is None else ""),
                "available": visible,
                "course": data,
            }
        )
    return ok(result)

import re
from flask import Blueprint, request
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .common import ApiError, ok, payload, protected
from ..extensions import db
from ..models import Category, Chapter, Course, Lesson, Quiz, QuizQuestion, User
from ..services.learning import lock_writes
from ..services.publishing import publication_errors
from ..services.catalog import integer_arg
from ..services.validation import text_field

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@bp.before_request
def serialize_admin_changes():
    if (
        request.method not in ("GET", "HEAD", "OPTIONS")
        and current_user.is_authenticated
        and current_user.role == "admin"
    ):
        lock_writes()


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
    if "status" in data:
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
            value = text_field(
                data,
                key,
                minimum=0 if key.startswith(("description_", "body_")) else 1,
                maximum=maximum,
            )
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


def editable(course_id):
    course = fetch(Course, course_id)
    if course.archived:
        raise ApiError("archived_content", 409)
    if course.status == "published":
        raise ApiError("unpublish_before_edit", 409)
    return course


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
        editable(course_id)
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
    editable(course_id)
    row = Chapter(course_id=course_id)
    apply_fields(row, payload(), True)
    db.session.add(row)
    return commit(row, 201)


@bp.patch("/courses/<int:course_id>/chapters/<int:chapter_id>")
@protected(admin=True)
def update_chapter(course_id, chapter_id):
    row = fetch(Chapter, chapter_id, course_id=course_id)
    editable(course_id)
    apply_fields(row, payload())
    return commit(row)


@bp.post("/courses/<int:course_id>/chapters/<int:chapter_id>/lessons")
@protected(admin=True)
def add_lesson(course_id, chapter_id):
    fetch(Chapter, chapter_id, course_id=course_id)
    editable(course_id)
    row = Lesson(chapter_id=chapter_id)
    apply_fields(row, payload(), True)
    db.session.add(row)
    return commit(row, 201)


@bp.patch("/courses/<int:course_id>/chapters/<int:chapter_id>/lessons/<int:lesson_id>")
@protected(admin=True)
def update_lesson(course_id, chapter_id, lesson_id):
    fetch(Chapter, chapter_id, course_id=course_id)
    row = fetch(Lesson, lesson_id, chapter_id=chapter_id)
    editable(course_id)
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
    if model is Chapter:
        editable(row.course_id)
    elif model is Lesson:
        editable(fetch(Chapter, row.chapter_id).course_id)
    if model is Course:
        row.status = "unpublished"
    row.archived = True
    return commit(row)


@bp.post("/courses/<int:course_id>/publish")
@protected(admin=True)
def publish(course_id):
    lock_writes()
    course = fetch(Course, course_id)
    errors = publication_errors(course)
    if errors:
        raise ApiError(
            "publication_failed",
            400,
            {str(index): value for index, value in enumerate(errors)},
        )
    course.status = "published"
    return commit(course)


@bp.post("/courses/<int:course_id>/unpublish")
@protected(admin=True)
def unpublish(course_id):
    course = fetch(Course, course_id)
    course.status = "unpublished"
    return commit(course)


def question_fields(row, data):
    row.prompt_zh = text_field(data, "prompt_zh", maximum=5000)
    row.prompt_en = text_field(data, "prompt_en", maximum=5000)
    row.explanation_zh = text_field(data, "explanation_zh", minimum=0, maximum=10000)
    row.explanation_en = text_field(data, "explanation_en", minimum=0, maximum=10000)
    options = data.get("options")
    if not isinstance(options, list) or not 2 <= len(options) <= 6:
        raise ApiError("invalid_content")
    clean, ids = [], set()
    for option in options:
        if (
            not isinstance(option, dict)
            or not isinstance(option.get("id"), str)
            or not re.fullmatch(r"[a-z0-9_-]{1,12}", option["id"])
            or option["id"] in ids
        ):
            raise ApiError("invalid_content")
        ids.add(option["id"])
        clean.append(
            {
                "id": option["id"],
                "text_zh": text_field(option, "text_zh", maximum=2000),
                "text_en": text_field(option, "text_en", maximum=2000),
            }
        )
    if (
        not isinstance(data.get("correct_option_id"), str)
        or data["correct_option_id"] not in ids
    ):
        raise ApiError("invalid_content")
    order = data.get("sort_order", 0)
    if type(order) is not int or not 0 <= order <= 10000:
        raise ApiError("invalid_content")
    row.options, row.correct_option_id, row.sort_order = (
        clean,
        data["correct_option_id"],
        order,
    )


@bp.route("/courses/<int:course_id>/quiz", methods=["GET", "PUT"])
@protected(admin=True)
def manage_quiz(course_id):
    fetch(Course, course_id)
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course_id))
    if request.method == "GET":
        return ok(
            {**serialize(quiz), "questions": [serialize(row) for row in quiz.questions]}
            if quiz
            else None
        )
    lock_writes()
    editable(course_id)
    data = payload()
    if quiz is None:
        quiz = Quiz(course_id=course_id)
        db.session.add(quiz)
    else:
        quiz.version += 1
    quiz.title_zh = text_field(data, "title_zh", maximum=160)
    quiz.title_en = text_field(data, "title_en", maximum=160)
    return commit(quiz)


@bp.post("/courses/<int:course_id>/quiz/questions")
@protected(admin=True)
def add_question(course_id):
    lock_writes()
    editable(course_id)
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course_id))
    if quiz is None:
        raise ApiError("quiz_required")
    row = QuizQuestion(quiz_id=quiz.id)
    question_fields(row, payload())
    quiz.version += 1
    db.session.add(row)
    return commit(row, 201)


@bp.patch("/courses/<int:course_id>/quiz/questions/<int:question_id>")
@protected(admin=True)
def update_question(course_id, question_id):
    lock_writes()
    editable(course_id)
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course_id))
    row = fetch(QuizQuestion, question_id)
    if quiz is None or row.quiz_id != quiz.id:
        raise ApiError("not_found", 404)
    data = payload()
    question_fields(row, {**serialize(row), **data})
    quiz.version += 1
    return commit(row)


@bp.post("/courses/<int:course_id>/quiz/questions/<int:question_id>/archive")
@protected(admin=True)
def archive_question(course_id, question_id):
    lock_writes()
    editable(course_id)
    quiz = db.session.scalar(db.select(Quiz).where(Quiz.course_id == course_id))
    row = fetch(QuizQuestion, question_id)
    if quiz is None or row.quiz_id != quiz.id:
        raise ApiError("not_found", 404)
    if not row.archived:
        row.archived = True
        quiz.version += 1
    return commit(row)


@bp.get("/users")
@protected(admin=True)
def users():
    page, per_page = integer_arg("page", 1, 100000), integer_arg("per_page", 20, 24)
    query = db.select(User)
    keyword = request.args.get("q", "").strip()
    if len(keyword) > 100:
        raise ApiError("invalid_query")
    if keyword:
        query = query.where(
            db.or_(
                User.nickname.icontains(keyword, autoescape=True),
                User.phone.icontains(keyword, autoescape=True),
            )
        )
    total = db.session.scalar(db.select(db.func.count()).select_from(query.subquery()))
    rows = db.session.scalars(
        query.order_by(User.id).offset((page - 1) * per_page).limit(per_page)
    ).all()
    return ok(
        [
            {
                "id": row.id,
                "nickname": row.nickname,
                "phone": row.phone[:6] + "****" + row.phone[-4:],
                "role": row.role,
                "is_active": row.is_active,
                "locale": row.locale,
            }
            for row in rows
        ],
        pagination={
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    )

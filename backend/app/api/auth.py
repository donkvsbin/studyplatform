from flask import Blueprint, request, session
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from .common import ApiError, ok, payload, protected
from ..extensions import db, login_manager
from ..models import User
from ..services import validation as v
from ..services.rate_limit import throttle

bp = Blueprint("auth", __name__, url_prefix="/api/v1")


@login_manager.user_loader
def load_user(user_id):
    if not user_id.isdigit():
        return None
    user = db.session.get(User, int(user_id))
    if (
        user
        and user.is_active
        and session.get("session_version") == user.session_version
    ):
        return user
    return None


@bp.get("/auth/csrf")
def csrf_token():
    return ok({"csrf_token": generate_csrf()})


@bp.post("/auth/register")
def register():
    throttle(("register", request.remote_addr), 20)
    data = payload()
    number = v.phone(data.get("phone"))
    secret = v.password(data)
    if data.get("confirm_password") != secret:
        raise ApiError(
            "validation_failed", fields={"confirm_password": "password_mismatch"}
        )
    user = User(
        phone=number,
        nickname=v.text_field(data, "nickname"),
        password_hash=generate_password_hash(secret),
        role="student",
        locale=v.locale(data.get("locale", "zh-CN")),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("phone_exists", 409)
    return ok(user.public(), 201)


@bp.post("/auth/login")
def login():
    data = payload()
    number = v.phone(data.get("phone"))
    throttle(("login-ip", request.remote_addr), 30)
    throttle(("login-phone", number), 8)
    secret = v.password(data)
    user = db.session.scalar(db.select(User).where(User.phone == number))
    if not user or not check_password_hash(user.password_hash, secret):
        raise ApiError("invalid_credentials", 401)
    if not user.is_active:
        raise ApiError("account_disabled", 403)
    session.clear()
    login_user(user)
    session["session_version"] = user.session_version
    return ok(user.public())


@bp.post("/auth/logout")
@protected()
def logout():
    logout_user()
    session.clear()
    return ok({"logged_out": True})


@bp.get("/auth/me")
@protected()
def me():
    return ok(current_user.public())


@bp.patch("/me")
@protected()
def update_me():
    data = payload()
    if "nickname" in data:
        current_user.nickname = v.text_field(data, "nickname")
    if "locale" in data:
        current_user.locale = v.locale(data["locale"])
    db.session.commit()
    return ok(current_user.public())


@bp.post("/me/password")
@protected()
def change_password():
    data = payload()
    throttle(("password", current_user.id), 8)
    if not check_password_hash(
        current_user.password_hash, v.password(data, "old_password")
    ):
        raise ApiError("incorrect_password", 400)
    secret = v.password(data, "new_password")
    if data.get("confirm_password") != secret:
        raise ApiError(
            "validation_failed", fields={"confirm_password": "password_mismatch"}
        )
    current_user.password_hash = generate_password_hash(secret)
    current_user.session_version += 1
    db.session.commit()
    logout_user()
    session.clear()
    return ok({"login_required": True})


@bp.get("/admin/stats")
@protected(admin=True)
def stats():
    from ..models import Course, Enrollment, Category
    from ..services.learning import summary
    from ..services.catalog import available

    enrollments = db.session.scalars(db.select(Enrollment)).all()
    return ok(
        {
            "users": db.session.scalar(db.select(db.func.count(User.id))),
            "published_courses": db.session.scalar(
                db.select(db.func.count(Course.id))
                .join(Category)
                .where(
                    Course.status == "published",
                    Course.archived.is_(False),
                    Category.archived.is_(False),
                )
            ),
            "enrollments": len(enrollments),
            "completed_courses": sum(
                available(row.course)
                and summary(row.course, row.user_id)["state"] == "completed"
                for row in enrollments
            ),
        }
    )


@bp.patch("/admin/users/<int:user_id>/status")
@protected(admin=True)
def user_status(user_id):
    from ..services.learning import lock_writes

    lock_writes()
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError("not_found", 404)
    if user.role == "admin":
        raise ApiError("admin_protected", 403)
    active = payload().get("is_active")
    if not isinstance(active, bool):
        raise ApiError("validation_failed", fields={"is_active": "invalid_boolean"})
    if user.is_active != active:
        user.is_active = active
        user.session_version += 1
    db.session.commit()
    return ok({"id": user.id, "is_active": user.is_active})

from datetime import datetime, timezone

from flask_login import UserMixin

from ..extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(16), unique=True, nullable=False)
    nickname = db.Column(db.String(40), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(12), nullable=False, default="student")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    locale = db.Column(db.String(8), nullable=False, default="zh-CN")
    session_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    __table_args__ = (
        db.CheckConstraint("role IN ('student', 'admin')", name="valid_role"),
        db.CheckConstraint("locale IN ('zh-CN', 'en')", name="valid_locale"),
    )

    def public(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "nickname": self.nickname,
            "role": self.role,
            "locale": self.locale,
        }


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    name_zh = db.Column(db.String(80), nullable=False)
    name_en = db.Column(db.String(80), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    archived = db.Column(db.Boolean, nullable=False, default=False)


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    title_zh = db.Column(db.String(160), nullable=False)
    title_en = db.Column(db.String(160), nullable=False)
    description_zh = db.Column(db.Text, nullable=False, default="")
    description_en = db.Column(db.Text, nullable=False, default="")
    objectives_zh = db.Column(db.JSON, nullable=False, default=list)
    objectives_en = db.Column(db.JSON, nullable=False, default=list)
    difficulty = db.Column(db.String(16), nullable=False, default="beginner")
    cover_kind = db.Column(db.String(16), nullable=False, default="web")
    status = db.Column(db.String(16), nullable=False, default="draft", index=True)
    archived = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )
    category = db.relationship(Category, lazy="joined")
    chapters = db.relationship(
        "Chapter", order_by="Chapter.sort_order, Chapter.id", lazy="selectin"
    )
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('draft', 'published', 'unpublished')",
            name="valid_course_status",
        ),
        db.CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="valid_difficulty",
        ),
    )


class Chapter(db.Model):
    __tablename__ = "chapters"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(
        db.Integer, db.ForeignKey("courses.id"), nullable=False, index=True
    )
    title_zh = db.Column(db.String(160), nullable=False)
    title_en = db.Column(db.String(160), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    archived = db.Column(db.Boolean, nullable=False, default=False)
    lessons = db.relationship(
        "Lesson", order_by="Lesson.sort_order, Lesson.id", lazy="selectin"
    )


class Lesson(db.Model):
    __tablename__ = "lessons"
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(
        db.Integer, db.ForeignKey("chapters.id"), nullable=False, index=True
    )
    title_zh = db.Column(db.String(160), nullable=False)
    title_en = db.Column(db.String(160), nullable=False)
    body_zh = db.Column(db.Text, nullable=False, default="")
    body_en = db.Column(db.Text, nullable=False, default="")
    video_url = db.Column(db.String(500), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=False, default=15)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    archived = db.Column(db.Boolean, nullable=False, default=False)
    __table_args__ = (
        db.CheckConstraint("duration_minutes > 0", name="positive_duration"),
    )


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    joined_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    course = db.relationship(Course, lazy="joined")
    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="unique_enrollment"),
    )

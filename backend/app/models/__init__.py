from datetime import datetime, timezone

from flask_login import UserMixin

from ..extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(16), unique=True, nullable=False)
    nickname = db.Column(db.String(40), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(12), nullable=False, default='student')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    locale = db.Column(db.String(8), nullable=False, default='zh-CN')
    session_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    __table_args__ = (
        db.CheckConstraint("role IN ('student', 'admin')", name='valid_role'),
        db.CheckConstraint("locale IN ('zh-CN', 'en')", name='valid_locale'),
    )

    def public(self):
        return {'id': self.id, 'phone': self.phone, 'nickname': self.nickname,
                'role': self.role, 'locale': self.locale}

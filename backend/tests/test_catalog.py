import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Category, Course, Chapter, Lesson, Enrollment
from app.services.seed import seed_demo
from conftest import register, login, write


@pytest.fixture()
def seeded(app):
    with app.app_context():
        assert seed_demo() == 3
    return app


def test_seed_bilingual_and_idempotent(seeded, client):
    register(client)
    login(client)
    write(client, "POST", "/courses/1/enrollment")
    with seeded.app_context():
        course = db.session.get(Course, 1)
        course.title_en = "Custom title"
        db.session.commit()
        assert seed_demo() == 0
        assert db.session.get(Course, 1).title_en == "Custom title"
        assert db.session.scalar(db.select(db.func.count(Lesson.id))) == 12
        assert db.session.scalar(db.select(db.func.count(Chapter.id))) == 6
        assert db.session.scalar(db.select(db.func.count(Enrollment.id))) == 1
        for lesson in db.session.scalars(db.select(Lesson)):
            assert len(lesson.body_zh) > 150 and len(lesson.body_en) > 150


def test_catalog_search_filter_and_pagination(seeded, client):
    result = client.get("/api/v1/courses?per_page=1&page=2").json
    assert len(result["data"]) == 1 and result["data"][0]["id"] == 2
    assert result["pagination"] == {"page": 2, "per_page": 1, "total": 3, "pages": 3}
    assert (
        client.get("/api/v1/courses?lang=en&q=Web").json["data"][0]["title"]
        == "Web Foundations"
    )
    assert client.get("/api/v1/courses?lang=zh-CN&q=Web").json["data"] == []
    assert (
        client.get("/api/v1/courses?category=3").json["data"][0]["title"]
        == "Python 入门"
    )
    assert client.get("/api/v1/courses?difficulty=advanced").json["data"] == []
    assert client.get("/api/v1/courses?q=%25").json["data"] == []
    assert (
        client.get("/api/v1/categories?lang=en").json["data"][0]["name"]
        == "Web development"
    )
    for query in (
        "page=0",
        "page=abc",
        "per_page=25",
        "category=-1",
        "difficulty=bad",
        "lang=fr",
        "page=" + "9" * 5000,
    ):
        assert client.get("/api/v1/courses?" + query).status_code == 400


def test_drafts_and_lesson_bodies_are_private(seeded, client):
    with seeded.app_context():
        course = db.session.get(Course, 1)
        course.status = "draft"
        db.session.commit()
    assert client.get("/api/v1/courses/1").status_code == 404
    assert len(client.get("/api/v1/courses").json["data"]) == 2
    detail = client.get("/api/v1/courses/2?lang=en").json["data"]
    assert detail["chapters"][0]["title"] == "Think in small instructions"
    assert "body_zh" not in str(detail) and "body_en" not in str(detail)
    assert client.get("/api/v1/courses/2/lessons/5").status_code == 404
    register(client)
    login(client)
    assert write(client, "POST", "/courses/1/enrollment").status_code == 404
    assert client.get("/api/v1/courses/2/lessons/5").status_code == 404


def test_enrollment_is_idempotent_and_user_scoped(seeded, client):
    assert write(client, "POST", "/courses/1/enrollment").status_code == 401
    register(client)
    login(client)
    first = write(client, "POST", "/courses/1/enrollment")
    again = write(client, "POST", "/courses/1/enrollment")
    assert first.status_code == 201 and again.status_code == 200
    assert first.json["data"]["id"] == again.json["data"]["id"]
    assert client.get("/api/v1/courses/1").json["data"]["enrolled"] is True
    other = seeded.test_client()
    register(other, "13800000002")
    login(other, "13800000002")
    assert other.get("/api/v1/me/enrollments?user_id=1").json["data"] == []
    assert len(client.get("/api/v1/me/enrollments").json["data"]) == 1
    with seeded.app_context():
        db.session.add(Enrollment(user_id=1, course_id=1))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_archiving_and_unpublishing_preserves_enrollment(seeded, client):
    register(client)
    login(client)
    write(client, "POST", "/courses/1/enrollment")
    with seeded.app_context():
        chapter = db.session.get(Chapter, 1)
        chapter.archived = True
        db.session.commit()
    assert client.get("/api/v1/courses/1").json["data"]["lesson_count"] == 2
    with seeded.app_context():
        course = db.session.get(Course, 1)
        course.status = "unpublished"
        db.session.commit()
    assert client.get("/api/v1/courses/1").status_code == 404
    assert write(client, "POST", "/courses/1/enrollment").status_code == 404
    item = client.get("/api/v1/me/enrollments").json["data"][0]
    assert item["available"] is False
    assert set(item["course"]) == {"id", "title"}


def test_basic_admin_content_api(seeded, client):
    assert client.get("/api/v1/admin/courses").status_code == 401
    register(client)
    login(client)
    assert write(client, "POST", "/admin/courses", {}).status_code == 403
    seeded.test_cli_runner().invoke(
        args=["create-admin"], input="13900000000\nAdminPass123\nAdminPass123\n"
    )
    admin = seeded.test_client()
    login(admin, "13900000000", "AdminPass123")
    category = write(
        admin,
        "POST",
        "/admin/categories",
        {"slug": "test-category", "name_zh": "测试分类", "name_en": "Test category"},
    ).json["data"]
    draft = write(
        admin,
        "POST",
        "/admin/courses",
        {
            "slug": "new-course",
            "title_zh": "新课程",
            "title_en": "New course",
            "category_id": category["id"],
        },
    )
    assert draft.status_code == 201 and draft.json["data"]["status"] == "draft"
    cid = draft.json["data"]["id"]
    assert client.get(f"/api/v1/courses/{cid}").status_code == 404
    chapter = write(
        admin,
        "POST",
        f"/admin/courses/{cid}/chapters",
        {"title_zh": "新章节", "title_en": "New chapter"},
    ).json["data"]
    chapter_id = chapter["id"]
    lesson = write(
        admin,
        "POST",
        f"/admin/courses/{cid}/chapters/{chapter_id}/lessons",
        {
            "title_zh": "新课时",
            "title_en": "New lesson",
            "body_zh": "原始正文",
            "body_en": "Original body",
        },
    )
    assert lesson.status_code == 201
    assert (
        admin.get(f"/api/v1/admin/courses/{cid}").json["data"]["chapters"][0][
            "lessons"
        ][0]["body_en"]
        == "Original body"
    )
    assert (
        write(
            admin,
            "PATCH",
            f"/admin/courses/1/chapters/{chapter_id}",
            {"title_zh": "篡改"},
        ).status_code
        == 404
    )
    assert (
        write(
            admin, "PATCH", f"/admin/courses/{cid}", {"status": "published"}
        ).status_code
        == 400
    )
    assert (
        write(
            admin,
            "PATCH",
            f"/admin/courses/{cid}/chapters/{chapter_id}/lessons/{lesson.json['data']['id']}",
            {"video_url": "https://other.example/video.mp4"},
        ).status_code
        == 400
    )
    assert write(admin, "POST", "/admin/categories/1/archive").status_code == 200
    assert client.get("/api/v1/courses/1").status_code == 404


def test_foreign_keys_are_enabled(app):
    with app.app_context():
        assert db.session.execute(db.text("PRAGMA foreign_keys")).scalar() == 1
        db.session.add(Enrollment(user_id=9999, course_id=9999))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

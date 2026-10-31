import pytest
from app.extensions import db
from app.models import Course, Lesson, QuizQuestion, LessonProgress
from app.services.seed import seed_demo
from conftest import login, register, write


@pytest.fixture()
def admin(app):
    with app.app_context():
        seed_demo()
    result = app.test_cli_runner().invoke(
        args=["create-admin"], input="13900000000\nAdminPass123\nAdminPass123\n"
    )
    assert result.exit_code == 0
    client = app.test_client()
    login(client, "13900000000", "AdminPass123")
    return client


def test_publish_requires_complete_bilingual_content(app, admin):
    draft = write(
        admin,
        "POST",
        "/admin/courses",
        {
            "slug": "empty-course",
            "title_zh": "空课程",
            "title_en": "Empty course",
            "category_id": 1,
        },
    ).json["data"]
    result = write(admin, "POST", f"/admin/courses/{draft['id']}/publish")
    assert result.status_code == 400
    assert "lessons_required" in result.json["error"]["fields"].values()
    assert "questions_required" in result.json["error"]["fields"].values()
    assert write(admin, "POST", "/admin/courses/1/unpublish").status_code == 200
    assert write(admin, "POST", "/admin/courses/1/publish").status_code == 200
    assert (
        write(
            admin, "PATCH", "/admin/courses/1", {"title_en": "Edit while live"}
        ).status_code
        == 409
    )
    write(admin, "POST", "/admin/courses/1/unpublish")
    write(admin, "PATCH", "/admin/courses/1/chapters/1/lessons/1", {"body_en": ""})
    assert (
        write(admin, "POST", "/admin/courses/1/publish").json["error"]["code"]
        == "publication_failed"
    )


def test_quiz_management_versions_and_cross_course_protection(admin):
    write(admin, "POST", "/admin/courses/1/unpublish")
    before = admin.get("/api/v1/admin/courses/1/quiz").json["data"]
    row = before["questions"][0]
    result = write(
        admin,
        "PATCH",
        f"/admin/courses/1/quiz/questions/{row['id']}",
        {"prompt_en": "Updated question"},
    )
    assert result.status_code == 200
    assert (
        admin.get("/api/v1/admin/courses/1/quiz").json["data"]["version"]
        == before["version"] + 1
    )
    assert (
        write(
            admin,
            "PATCH",
            "/admin/courses/1/quiz/questions/4",
            {"prompt_en": "Cross course"},
        ).status_code
        == 404
    )
    assert (
        write(
            admin, "POST", f"/admin/courses/1/quiz/questions/{row['id']}/archive"
        ).status_code
        == 200
    )
    assert write(admin, "POST", "/admin/courses/1/publish").status_code == 400


def test_unpublish_and_archive_preserve_learning_and_scores(app, admin):
    learner = app.test_client()
    register(learner)
    login(learner)
    write(learner, "POST", "/courses/1/enrollment")
    for lid in range(1, 5):
        write(learner, "PUT", f"/courses/1/lessons/{lid}/progress", {"completed": True})
    q = learner.get("/api/v1/courses/1/quiz").json["data"]
    attempt = write(
        learner,
        "POST",
        "/courses/1/quiz/attempts",
        {
            "version": q["version"],
            "submission_id": "archive-snapshot",
            "answers": {
                str(row["id"]): "abc"[i] for i, row in enumerate(q["questions"])
            },
        },
    ).json["data"]
    write(admin, "POST", "/admin/courses/1/unpublish")
    assert learner.get("/api/v1/courses/1/lessons/1").status_code == 404
    assert learner.get("/api/v1/courses/1/quiz").status_code == 404
    assert learner.get(f"/api/v1/me/quiz-attempts/{attempt['id']}").status_code == 200
    write(admin, "POST", "/admin/lessons/1/archive")
    assert write(admin, "POST", "/admin/courses/1/publish").status_code == 200
    summary = learner.get("/api/v1/me/enrollments").json["data"][0]["summary"]
    assert (
        summary["total_count"] == 3
        and summary["completed_count"] == 3
        and summary["state"] == "completed"
    )
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(LessonProgress.id))) == 4
    assert admin.get("/api/v1/admin/stats").json["data"]["completed_courses"] == 1


def test_admin_users_mask_phone_and_protect_role(app, admin):
    learner = app.test_client()
    register(learner, nickname="Search learner")
    login(learner)
    rows = admin.get("/api/v1/admin/users?q=Search").json["data"]
    assert len(rows) == 1 and "****" in rows[0]["phone"]
    assert "+8613800000001" not in str(rows)
    assert (
        write(
            learner,
            "PATCH",
            f"/admin/users/{rows[0]['id']}/status",
            {"is_active": False},
        ).status_code
        == 403
    )
    assert (
        write(
            admin, "PATCH", f"/admin/users/{rows[0]['id']}/status", {"is_active": False}
        ).status_code
        == 200
    )
    assert learner.get("/api/v1/auth/me").status_code == 401

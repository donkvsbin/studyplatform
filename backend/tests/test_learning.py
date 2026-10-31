from concurrent.futures import ThreadPoolExecutor
import uuid

import pytest

from app.extensions import db
from app.models import LessonProgress, Quiz, QuizAttempt, QuizQuestion
from app.services.seed import seed_demo
from conftest import register, login, write


@pytest.fixture()
def learner(app, client):
    with app.app_context():
        seed_demo()
    register(client)
    login(client)
    assert write(client, "POST", "/courses/1/enrollment").status_code == 201
    return client


def quiz_payload(client, correct=True, submission_id=None):
    quiz = client.get("/api/v1/courses/1/quiz").json["data"]
    return {
        "version": quiz["version"],
        "submission_id": submission_id or str(uuid.uuid4()),
        "answers": {
            str(row["id"]): ("abc"[i] if correct else "bca"[i])
            for i, row in enumerate(quiz["questions"])
        },
    }


def test_progress_is_persistent_idempotent_and_course_scoped(app, learner):
    assert learner.get("/api/v1/courses/1/lessons/1").json["data"]["lesson"]["body"]
    assert (
        write(
            learner, "PUT", "/courses/1/lessons/5/progress", {"completed": True}
        ).status_code
        == 404
    )
    result = write(
        learner,
        "PUT",
        "/courses/1/lessons/1/progress",
        {"completed": True, "video_position": 3.25},
    )
    assert result.json["data"]["summary"]["percent"] == 25
    again = write(learner, "PUT", "/courses/1/lessons/1/progress", {"completed": True})
    assert (
        again.json["data"]["progress"]["completed_at"]
        == result.json["data"]["progress"]["completed_at"]
    )
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(LessonProgress.id))) == 1
    assert (
        learner.get("/api/v1/courses/1/lessons/1").json["data"]["lesson"]["progress"][
            "video_position"
        ]
        == 3.25
    )
    assert (
        learner.get("/api/v1/me/enrollments").json["data"][0]["summary"][
            "resume_lesson_id"
        ]
        == 1
    )
    assert (
        write(
            learner, "PUT", "/courses/1/lessons/1/progress", {"completed": False}
        ).json["data"]["summary"]["percent"]
        == 0
    )


@pytest.mark.parametrize(
    "data",
    [
        {"completed": "yes"},
        {"video_position": -1},
        {"video_position": float("inf")},
        {"video_position": True},
        {"video_position": 86401},
    ],
)
def test_progress_rejects_invalid_inputs(learner, data):
    assert (
        write(learner, "PUT", "/courses/1/lessons/1/progress", data).status_code == 400
    )


def test_lesson_and_quiz_require_enrollment(app, learner):
    other = app.test_client()
    register(other, "13800000002")
    login(other, "13800000002")
    assert other.get("/api/v1/courses/1/lessons/1").status_code == 403
    assert other.get("/api/v1/courses/1/quiz").status_code == 403
    assert (
        write(
            other, "PUT", "/courses/1/lessons/1/progress", {"completed": True}
        ).status_code
        == 403
    )
    assert other.get("/api/v1/me/enrollments").json["data"] == []
    assert (
        learner.put(
            "/api/v1/courses/1/lessons/1/progress", json={"completed": True}
        ).json["error"]["code"]
        == "csrf_failed"
    )


def test_quiz_hides_keys_and_grades_server_side(learner):
    quiz = learner.get("/api/v1/courses/1/quiz").json["data"]
    assert "correct_option_id" not in str(quiz) and "explanation" not in str(quiz)
    data = {
        **quiz_payload(learner, False),
        "score": 100,
        "passed": True,
        "user_id": 999,
    }
    result = write(learner, "POST", "/courses/1/quiz/attempts", data)
    assert result.status_code == 201
    assert result.json["data"]["score"] == 0 and result.json["data"]["passed"] is False
    data = quiz_payload(learner)
    data["answers"][str(quiz["questions"][2]["id"])] = "a"
    result = write(learner, "POST", "/courses/1/quiz/attempts", data)
    assert result.json["data"]["correct_count"] == 2
    assert result.json["data"]["passed"] is True
    assert result.json["data"]["answers"][0]["explanation"]


def test_all_lessons_alone_do_not_complete_course(learner):
    for lid in range(1, 5):
        write(learner, "PUT", f"/courses/1/lessons/{lid}/progress", {"completed": True})
    state = learner.get("/api/v1/me/enrollments").json["data"][0]["summary"]
    assert state["percent"] == 100 and state["state"] == "quiz_required"
    write(learner, "POST", "/courses/1/quiz/attempts", quiz_payload(learner, False))
    assert (
        learner.get("/api/v1/me/enrollments").json["data"][0]["summary"]["state"]
        == "quiz_required"
    )
    write(learner, "POST", "/courses/1/quiz/attempts", quiz_payload(learner))
    assert (
        learner.get("/api/v1/me/enrollments").json["data"][0]["summary"]["state"]
        == "completed"
    )
    write(learner, "PUT", "/courses/1/lessons/1/progress", {"completed": False})
    assert (
        learner.get("/api/v1/me/enrollments").json["data"][0]["summary"]["state"]
        == "in_progress"
    )


def test_retry_is_idempotent_and_conflicting_payload_rejected(app, learner):
    data = quiz_payload(learner)
    first = write(learner, "POST", "/courses/1/quiz/attempts", data)
    again = write(learner, "POST", "/courses/1/quiz/attempts", data)
    assert first.status_code == 201 and again.status_code == 200
    assert first.json["data"]["id"] == again.json["data"]["id"]
    data["answers"][next(iter(data["answers"]))] = "b"
    assert write(learner, "POST", "/courses/1/quiz/attempts", data).status_code == 409
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(QuizAttempt.id))) == 1


def test_concurrent_network_retry_creates_one_result(app, learner):
    data = quiz_payload(learner)
    cookie = learner.get_cookie("session").value

    def submit(_):
        c = app.test_client()
        c.set_cookie("session", cookie)
        response = write(c, "POST", "/courses/1/quiz/attempts", data)
        return response.status_code, response.json

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(submit, range(2)))
    assert sorted(row[0] for row in results) == [200, 201]
    assert len({row[1]["data"]["id"] for row in results}) == 1


def test_quiz_version_and_answer_validation(app, learner):
    data = quiz_payload(learner)
    with app.app_context():
        quiz = db.session.get(Quiz, 1)
        quiz.version += 1
        db.session.commit()
    assert (
        write(learner, "POST", "/courses/1/quiz/attempts", data).json["error"]["code"]
        == "quiz_changed"
    )
    data = quiz_payload(learner)
    data["answers"].pop(next(iter(data["answers"])))
    assert write(learner, "POST", "/courses/1/quiz/attempts", data).status_code == 400
    data = quiz_payload(learner)
    data["answers"][next(iter(data["answers"]))] = "invalid"
    assert write(learner, "POST", "/courses/1/quiz/attempts", data).status_code == 400


def test_snapshots_are_immutable_and_user_scoped(app, learner):
    result = write(
        learner, "POST", "/courses/1/quiz/attempts", quiz_payload(learner)
    ).json["data"]
    with app.app_context():
        row = db.session.get(QuizQuestion, 1)
        row.prompt_en = "Changed question"
        row.correct_option_id = "b"
        row.explanation_en = "New explanation"
        db.session.commit()
    detail = learner.get(f"/api/v1/me/quiz-attempts/{result['id']}?lang=en").json[
        "data"
    ]
    assert detail["score"] == 100 and detail["answers"][0]["correct_option_id"] == "a"
    assert detail["answers"][0]["prompt"] != "Changed question"
    other = app.test_client()
    register(other, "13800000002")
    login(other, "13800000002")
    assert other.get(f"/api/v1/me/quiz-attempts/{result['id']}").status_code == 404
    assert other.get("/api/v1/me/quiz-attempts?user_id=1").json["data"] == []

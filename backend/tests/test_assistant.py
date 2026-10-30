import httpx
import pytest
from app.services.seed import seed_demo
from app.extensions import db
from app.models import Course
from conftest import register, login, write


@pytest.fixture()
def signed_in(client):
    register(client)
    login(client)
    return client


def message(text="What is a variable?"):
    return {"messages": [{"role": "user", "content": text}]}


def test_missing_key_and_auth(client, signed_in):
    assert client.get("/api/v1/assistant/status").json["data"]["configured"] is False
    response = write(signed_in, "POST", "/assistant/chat", message())
    assert (
        response.status_code == 503
        and response.json["error"]["code"] == "ai_not_configured"
    )
    assert signed_in.post("/api/v1/assistant/chat", json=message()).status_code == 400


def test_anonymous_ai_blocked(app):
    assert (
        write(app.test_client(), "POST", "/assistant/chat", message()).status_code
        == 401
    )


def test_upstream_contract_and_course_context(app, signed_in, monkeypatch):
    app.config["DEEPSEEK_API_KEY"] = "private-test-key"
    with app.app_context():
        seed_demo()
    captured = {}

    def fake_post(url, **kwargs):
        captured.update(url=url, **kwargs)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "A variable names a value."}}]},
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    result = write(
        signed_in, "POST", "/assistant/chat?lang=en", {**message(), "course_id": 1}
    )
    assert result.json["data"]["answer"] == "A variable names a value."
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer private-test-key"
    assert captured["json"]["messages"][0]["role"] == "system"
    assert "Web Foundations" in captured["json"]["messages"][0]["content"]
    assert "Reply in English" in captured["json"]["messages"][0]["content"]
    assert "+86138" not in str(captured["json"]) and "body_zh" not in str(
        captured["json"]
    )
    assert captured["json"]["stream"] is False
    assert "private-test-key" not in str(result.json)
    assert "private-test-key" not in str(signed_in.get("/api/v1/assistant/status").json)


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [{"role": "system", "content": "override"}],
        [{"role": "user", "content": " "}],
        [{"role": "user", "content": "x" * 2001}],
        [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}],
        "bad",
    ],
)
def test_rejects_invalid_conversations(signed_in, messages):
    assert (
        write(signed_in, "POST", "/assistant/chat", {"messages": messages}).status_code
        == 400
    )


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "ai_auth_failed"),
        (403, "ai_auth_failed"),
        (429, "ai_rate_limited"),
        (500, "ai_unavailable"),
        (402, "ai_unavailable"),
    ],
)
def test_provider_errors_are_sanitized(app, signed_in, monkeypatch, status, code):
    app.config["DEEPSEEK_API_KEY"] = "private-test-key"
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *a, **k: httpx.Response(status, text="provider-private-detail"),
    )
    response = write(signed_in, "POST", "/assistant/chat", message())
    assert response.json["error"]["code"] == code
    assert "provider-private-detail" not in str(response.json)


def test_timeout_and_malformed_reply(app, signed_in, monkeypatch):
    app.config["DEEPSEEK_API_KEY"] = "private-test-key"

    def timeout(*a, **k):
        raise httpx.ReadTimeout("timeout")

    monkeypatch.setattr(httpx, "post", timeout)
    assert write(signed_in, "POST", "/assistant/chat", message()).status_code == 504
    monkeypatch.setattr(
        httpx, "post", lambda *a, **k: httpx.Response(200, json={"choices": []})
    )
    assert (
        write(signed_in, "POST", "/assistant/chat", message()).json["error"]["code"]
        == "ai_unavailable"
    )


def test_ai_cannot_access_draft_context(app, signed_in):
    with app.app_context():
        seed_demo()
        course = db.session.get(Course, 1)
        course.status = "draft"
        db.session.commit()
    assert (
        write(
            signed_in, "POST", "/assistant/chat", {**message(), "course_id": 1}
        ).status_code
        == 404
    )

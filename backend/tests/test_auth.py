from werkzeug.security import check_password_hash
from app.extensions import db
from app.models import User
from conftest import register, login, write


def test_registration_and_permissions(app, client):
    assert client.get("/api/v1/auth/me").status_code == 401
    response = register(client, role="admin")
    assert response.status_code == 201
    assert response.json["data"]["role"] == "student"
    assert register(client, "+86 13800000001").status_code == 409
    assert login(client, password="WrongPassword").status_code == 401
    assert login(client).status_code == 200
    assert client.get("/api/v1/auth/me").json["data"]["phone"] == "+8613800000001"
    assert client.get("/api/v1/admin/stats").status_code == 403
    assert (
        write(
            client,
            "PATCH",
            "/me",
            {"nickname": "新昵称", "locale": "en", "role": "admin"},
        ).json["data"]["role"]
        == "student"
    )
    with app.app_context():
        user = db.session.get(User, 1)
        assert user.password_hash != "Password123"
        assert check_password_hash(user.password_hash, "Password123")
    assert write(client, "POST", "/auth/logout").status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_csrf_and_validation(client):
    assert (
        client.post("/api/v1/auth/login", json={}).json["error"]["code"]
        == "csrf_failed"
    )
    assert (
        client.post(
            "/api/v1/auth/register", json={}, headers={"X-CSRFToken": "wrong"}
        ).status_code
        == 400
    )
    assert register(client, "123").status_code == 400
    assert register(client, confirm_password="different").status_code == 400
    assert (
        register(client, password="short", confirm_password="short").status_code == 400
    )
    assert write(client, "POST", "/auth/register", ["bad"]).status_code == 400


def test_password_revokes_all_sessions(app, client):
    register(client)
    login(client)
    other = app.test_client()
    login(other)
    assert (
        write(
            client,
            "POST",
            "/me/password",
            {
                "old_password": "WrongPass",
                "new_password": "NewPassword",
                "confirm_password": "NewPassword",
            },
        ).status_code
        == 400
    )
    assert (
        write(
            client,
            "POST",
            "/me/password",
            {
                "old_password": "Password123",
                "new_password": "NewPassword",
                "confirm_password": "NewPassword",
            },
        ).status_code
        == 200
    )
    assert client.get("/api/v1/auth/me").status_code == 401
    assert other.get("/api/v1/auth/me").status_code == 401
    assert login(client).status_code == 401
    assert login(client, password="NewPassword").status_code == 200


def test_disable_enable_and_admin_guard(app, client):
    register(client)
    login(client)
    runner = app.test_cli_runner()
    assert (
        runner.invoke(
            args=["create-admin"], input="13900000000\nAdminPass123\nAdminPass123\n"
        ).exit_code
        == 0
    )
    admin = app.test_client()
    assert login(admin, "13900000000", "AdminPass123").status_code == 200
    assert admin.get("/api/v1/admin/stats").status_code == 200
    assert (
        write(admin, "PATCH", "/admin/users/1/status", {"is_active": False}).status_code
        == 200
    )
    assert client.get("/api/v1/auth/me").status_code == 401
    assert login(client).json["error"]["code"] == "account_disabled"
    write(admin, "PATCH", "/admin/users/1/status", {"is_active": True})
    assert client.get("/api/v1/auth/me").status_code == 401
    assert login(client).status_code == 200
    assert (
        write(admin, "PATCH", "/admin/users/2/status", {"is_active": False}).status_code
        == 403
    )


def test_cli_reset_revokes_session(app, client):
    register(client)
    login(client)
    runner = app.test_cli_runner()
    assert (
        runner.invoke(
            args=["reset-password"], input="13800000001\nChangedPass\nChangedPass\n"
        ).exit_code
        == 0
    )
    assert client.get("/api/v1/auth/me").status_code == 401
    assert login(client, password="ChangedPass").status_code == 200
    assert (
        runner.invoke(
            args=["create-admin"], input="13800000001\nAdminPass123\nAdminPass123\n"
        ).exit_code
        != 0
    )


def test_rate_limits(app, client):
    app.config["RATE_LIMIT_ENABLED"] = True
    for _ in range(8):
        assert login(client, password="WrongPassword").status_code == 401
    assert login(client, password="WrongPassword").status_code == 429

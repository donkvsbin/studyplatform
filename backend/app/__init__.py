from pathlib import Path
import secrets

from flask import Flask, send_from_directory
from sqlalchemy import text

from .config import BACKEND, Config
from .extensions import csrf, db, login_manager, migrate
from .api.common import ApiError, install_errors, ok


def create_app(test_config=None):
    app = Flask(__name__, instance_path=str(BACKEND / "instance"), static_folder=None)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config["SECRET_KEY"]:
        secret_file = Path(app.instance_path) / "secret.key"
        try:
            with secret_file.open("x", encoding="utf-8") as stream:
                stream.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = secret_file.read_text(encoding="utf-8").strip()
    db.init_app(app)
    migrate.init_app(
        app, db, directory=str(BACKEND / "migrations"), render_as_batch=True
    )
    login_manager.init_app(app)
    install_errors(app)
    csrf.init_app(app)
    from . import models  # noqa: F401 -- register migration metadata
    from .api.auth import bp as auth_bp
    from .cli import register_commands
    from .services.rate_limit import RateLimiter

    app.extensions["learnhub_limiter"] = RateLimiter()
    app.register_blueprint(auth_bp)
    from .api.courses import bp as courses_bp
    from .api.admin import bp as admin_bp

    app.register_blueprint(courses_bp)
    app.register_blueprint(admin_bp)
    from .api.assistant import bp as assistant_bp

    app.register_blueprint(assistant_bp)
    register_commands(app)

    @app.get("/api/v1/health")
    def health():
        db.session.execute(text("SELECT 1"))
        return ok({"status": "ok", "database": "ok", "service": "LearnHub"})

    dist = BACKEND.parent / "frontend" / "dist"

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def frontend(path):
        if path == "api" or path.startswith("api/"):
            raise ApiError("not_found", 404)
        target = (dist / path).resolve()
        if not target.is_relative_to(dist.resolve()):
            raise ApiError("not_found", 404)
        if target.is_file():
            return send_from_directory(dist, path)
        if path.startswith(("assets/", "demo/")):
            raise ApiError("not_found", 404)
        if (dist / "index.html").is_file():
            return send_from_directory(dist, "index.html")
        raise ApiError("frontend_not_built", 503)

    return app

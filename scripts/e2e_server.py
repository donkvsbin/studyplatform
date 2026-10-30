"""Isolated browser-test server: never touches the real local database."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from flask_migrate import upgrade
from waitress import serve
from app import create_app
from app.services.seed import seed_demo

with TemporaryDirectory(prefix="learnhub-e2e-") as directory:
    app = create_app(
        {
            "SECRET_KEY": "isolated-e2e-only",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + str(Path(directory) / "test.db"),
            "RATE_LIMIT_ENABLED": False,
            "DEEPSEEK_API_KEY": "",
        }
    )
    with app.app_context():
        upgrade()
        seed_demo()
    serve(app, host="127.0.0.1", port=5001)

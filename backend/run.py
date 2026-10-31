"""PyCharm entry point. Choose backend/.venv as the Python interpreter."""

import os
from pathlib import Path

from waitress import serve
from app import create_app


if __name__ == "__main__":
    if not (
        Path(__file__).resolve().parent.parent / "frontend/dist/index.html"
    ).is_file():
        raise SystemExit(
            "Build the frontend first: run scripts/start.ps1 from the project root."
        )
    port = int(os.getenv("LEARNHUB_PORT", "5000"))
    print(f"LearnHub: http://127.0.0.1:{port}", flush=True)
    serve(create_app(), host="127.0.0.1", port=port)

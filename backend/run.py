"""PyCharm entry point. Choose backend/.venv as the Python interpreter."""

import os
import socket
from pathlib import Path

from waitress import serve
from app import create_app


def open_listener(port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Waitress normally enables SO_REUSEADDR, which on Windows can let a
        # second process start on an occupied port and receive the wrong app.
        if os.name == "nt":
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        listener.bind(("127.0.0.1", port))
        return listener
    except OSError:
        listener.close()
        raise


def main():
    if not (
        Path(__file__).resolve().parent.parent / "frontend/dist/index.html"
    ).is_file():
        raise SystemExit(
            "Build the frontend first: run scripts/start.ps1 from the project root."
        )
    try:
        port = int(os.getenv("LEARNHUB_PORT", "5000"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise SystemExit("LEARNHUB_PORT must be a number between 1 and 65535.")
    try:
        listener = open_listener(port)
    except OSError:
        raise SystemExit(
            f"Port {port} is already in use or unavailable. Stop the other server, "
            "or run start.bat -Port 5002 to use http://127.0.0.1:5002. "
            "In PyCharm, set LEARNHUB_PORT=5002."
        )
    with listener:
        app = create_app()
        print(f"LearnHub: http://127.0.0.1:{port} (Ctrl+C to stop)", flush=True)
        serve(app, sockets=[listener])


if __name__ == "__main__":
    main()

import os
import socket
import threading
from urllib.request import urlopen

import pytest
from flask import Flask
from waitress import create_server

from run import open_listener


def test_occupied_reusable_port_is_rejected():
    with socket.socket() as existing:
        existing.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        existing.bind(("127.0.0.1", 0))
        existing.listen()
        with pytest.raises(OSError):
            listener = open_listener(existing.getsockname()[1])
            listener.close()


def test_waitress_serves_from_exclusive_listener():
    app = Flask("startup-test")
    app.add_url_rule("/", view_func=lambda: "correct application")
    with open_listener(0) as listener:
        port = listener.getsockname()[1]
        server = create_server(app, sockets=[listener])
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
                assert response.status == 200
                assert response.read() == b"correct application"
            if os.name == "nt":
                with socket.socket() as competing:
                    competing.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    with pytest.raises(OSError):
                        competing.bind(("127.0.0.1", port))
        finally:
            server.close()
            server.task_dispatcher.shutdown()
            thread.join(timeout=3)

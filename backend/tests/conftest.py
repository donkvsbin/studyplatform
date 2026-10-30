import pytest
from flask_migrate import upgrade
from app import create_app
from app.extensions import db


@pytest.fixture()
def app(tmp_path):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test-key',
                      'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp_path / "test.db"}',
                      'RATE_LIMIT_ENABLED': False, 'DEEPSEEK_API_KEY': ''})
    with app.app_context():
        upgrade()
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


def write(client, method, path, data=None):
    token = client.get('/api/v1/auth/csrf').json['data']['csrf_token']
    return client.open('/api/v1' + path, method=method, json=data or {}, headers={'X-CSRFToken': token})


def register(client, phone='13800000001', **extra):
    return write(client, 'POST', '/auth/register', {'phone': phone, 'nickname': 'Learner', 'password': 'Password123', 'confirm_password': 'Password123', **extra})


def login(client, phone='13800000001', password='Password123'):
    return write(client, 'POST', '/auth/login', {'phone': phone, 'password': password})

from app import create_app
from app.extensions import db


def test_health_and_unknown_api(tmp_path):
    app = create_app({'TESTING': True, 'SECRET_KEY': 'test', 'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp_path / "test.db"}'})
    client = app.test_client()
    assert client.get('/api/v1/health').json['data']['database'] == 'ok'
    response = client.get('/api/v1/no-such-api')
    assert response.status_code == 404
    assert response.json['error']['code'] == 'not_found'
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

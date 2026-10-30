from functools import wraps
from uuid import uuid4

from flask import g, jsonify, request
from flask_login import current_user
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import CSRFError


class ApiError(Exception):
    def __init__(self, code, status=400, fields=None):
        self.code, self.status, self.fields = code, status, fields


def ok(data, status=200, **extra):
    return jsonify(data=data, **extra), status


def payload():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise ApiError('invalid_json')
    return value


def protected(admin=False):
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                raise ApiError('unauthenticated', 401)
            if admin and current_user.role != 'admin':
                raise ApiError('forbidden', 403)
            return fn(*args, **kwargs)
        return wrapped
    return decorate


def install_errors(app):
    @app.before_request
    def identify_request():
        g.request_id = uuid4().hex

    @app.errorhandler(ApiError)
    def api_error(error):
        body = {'code': error.code}
        if error.fields:
            body['fields'] = error.fields
        return jsonify(error=body, request_id=getattr(g, 'request_id', uuid4().hex)), error.status

    @app.errorhandler(CSRFError)
    def csrf_error(_):
        return api_error(ApiError('csrf_failed', 400))

    @app.errorhandler(HTTPException)
    def http_error(error):
        return api_error(ApiError({404: 'not_found', 405: 'method_not_allowed', 413: 'request_too_large'}.get(error.code, 'bad_request'), error.code))

    @app.errorhandler(Exception)
    def unexpected_error(error):
        from ..extensions import db
        db.session.rollback()
        app.logger.error('Unhandled request failure (%s), request_id=%s', type(error).__name__, getattr(g, 'request_id', ''))
        return api_error(ApiError('server_error', 500))

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response

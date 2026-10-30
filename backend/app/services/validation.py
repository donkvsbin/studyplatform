import re
from ..api.common import ApiError


def phone(value):
    if not isinstance(value, str):
        raise ApiError('validation_failed', fields={'phone': 'invalid_phone'})
    value = re.sub(r'\s+', '', value)
    if value.startswith('+86'):
        value = value[3:]
    if not re.fullmatch(r'1[3-9]\d{9}', value, flags=re.ASCII):
        raise ApiError('validation_failed', fields={'phone': 'invalid_phone'})
    return '+86' + value


def text_field(data, key, minimum=1, maximum=40):
    value = data.get(key)
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise ApiError('validation_failed', fields={key: 'invalid_length'})
    return value.strip()


def password(data, key='password'):
    value = data.get(key)
    if not isinstance(value, str) or not 8 <= len(value) <= 128 or not value.strip():
        raise ApiError('validation_failed', fields={key: 'invalid_password'})
    return value


def locale(value):
    if value not in ('zh-CN', 'en'):
        raise ApiError('validation_failed', fields={'locale': 'invalid_locale'})
    return value

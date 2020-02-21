# -*- coding: utf-8 -*-
import six

from blueapps.utils.request_provider import get_request, get_x_request_id
from blueapps.utils.esbclient import (
    client, get_client_by_user,
    backend_client,
    get_client_by_request
)

__all__ = [
    'get_request', 'get_x_request_id', 'client', 'ok', 'ok_data', 'failed',
    'failed_data', 'backend_client', 'get_client_by_user',
    'get_client_by_request'
]


def ok(message="", **options):
    result = {'result': True, 'message': message, 'msg': message}
    result.update(**options)
    return result


def failed(message="", **options):
    if not isinstance(message, str):
        if isinstance(message, six.string_types):
            message = message.encode('utf-8')
        message = str(message)
    result = {'result': False, 'message': message, 'data': {}, 'msg': message}
    result.update(**options)
    return result


def failed_data(message, data, **options):
    if not isinstance(message, str):
        if isinstance(message, six.string_types):
            message = message.encode('utf-8')
        message = str(message)
    result = {
        'result': False,
        'message': message,
        'data': data,
        'msg': message
    }
    result.update(**options)
    return result


def ok_data(data=None, **options):
    if data is None:
        data = {}
    result = {
        'result': True,
        'message': "",
        'data': data,
        'msg': ""
    }
    result.update(**options)
    return result

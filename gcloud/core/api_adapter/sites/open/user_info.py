# -*- coding: utf-8 -*-

from gcloud.conf import settings


def get_user_info(request):
    client = settings.ESB_GET_CLIENT_BY_REQUEST(request)
    auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
    _get_user_info = getattr(auth, settings.ESB_AUTH_GET_USER_INFO)
    user_info = _get_user_info({})
    if 'data' in user_info:
        user_info['data']['bk_supplier_account'] = 0
    return user_info

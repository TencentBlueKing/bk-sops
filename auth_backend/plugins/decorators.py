# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
from functools import wraps

from django.http import JsonResponse
from django.utils.decorators import available_attrs

from auth_backend.plugins.constants import PRINCIPAL_TYPE_USER
from auth_backend.plugins.http import HttpResponseAuthFailed
from auth_backend.plugins.utils import build_need_permission

logger = logging.getLogger('root')


def verify_perms(auth_resource, resource_get, actions, scope_id_get=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            username = request.user.username
            instance_id = None

            if resource_get:
                try:
                    if resource_get['from'] == 'args':
                        instance_id = args[resource_get['key']]
                    elif resource_get['from'] == 'kwargs':
                        instance_id = kwargs[resource_get['key']]
                    else:
                        request_params = getattr(request, request.method)
                        instance_id = request_params[resource_get['key']]
                except Exception as e:
                    message = "verify_perms resolve resource error: %s" % e
                    result = {
                        'result': False,
                        'message': message,
                        'data': {}
                    }
                    return JsonResponse(result)

            permission = []
            actions_id = [act.id for act in actions]
            verify_result = auth_resource.verify_perms(PRINCIPAL_TYPE_USER,
                                                       username,
                                                       actions_id,
                                                       instance_id)
            if not verify_result['result']:
                message = ('verify perms of Resource[{resource}] by backend[{backend_cls}] '
                           'return error: {error}').format(
                    resource=auth_resource.name,
                    backend_cls=auth_resource.backend,
                    error=verify_result['message']
                )
                logger.error(message)
                result = {
                    'result': False,
                    'message': message,
                    'data': {}
                }
                return JsonResponse(result)
            verify_data = verify_result['data']
            for action_resource in verify_data:
                if not action_resource['is_pass']:
                    permission.append(build_need_permission(auth_resource,
                                                            action_resource['action_id'],
                                                            instance_id,
                                                            scope_id_get(request) if scope_id_get else None))

            if permission:
                return HttpResponseAuthFailed(permission)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

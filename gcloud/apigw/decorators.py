# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from functools import wraps

import ujson as json
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import available_attrs

from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed

from gcloud.conf import settings
from gcloud.core.models import Project
from gcloud.core.permissions import project_resource
from gcloud.apigw.utils import get_project_with
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ
from gcloud.apigw.exceptions import UserNotExistError

WHITE_APPS = {'bk_fta', 'bk_bcs'}
WHETHER_PREPARE_BIZ = getattr(settings, 'WHETHER_PREPARE_BIZ_IN_API_CALL', True)


def check_white_apps(request):
    app_code = getattr(request.jwt.app, settings.APIGW_APP_CODE_KEY)
    if app_code in WHITE_APPS:
        return True
    return False


def inject_user(request):
    username = getattr(request.jwt.app, settings.APIGW_USER_USERNAME_KEY)
    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=username)
    except user_model.DoesNotExist:
        if request.is_trust:
            user, _ = user_model.objects.get_or_create(username=username)
        else:
            raise UserNotExistError('user[username=%s] does not exist or has not logged in this APP' % username)

    setattr(request, 'user', user)


def mark_request_whether_is_trust(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kwargs):

        setattr(request, 'is_trust', check_white_apps(request))

        try:
            inject_user(request)
        except UserNotExistError as e:
            return JsonResponse({
                'result': False,
                'message': e.message
            })

        return view_func(request, *args, **kwargs)

    return wrapper


def _get_project_scope_from_request(request):
    if request.method == 'GET':
        obj_scope = request.GET.get('scope', PROJECT_SCOPE_CMDB_BIZ)
    else:
        params = json.loads(request.body)
        obj_scope = params.get('scope', PROJECT_SCOPE_CMDB_BIZ)

    return obj_scope


def project_inject(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kwargs):

        obj_id = kwargs.get('project_id')
        try:
            obj_scope = _get_project_scope_from_request(request)
        except Exception:
            return JsonResponse({
                'result': False,
                'message': 'invalid param format'
            })

        try:
            project = get_project_with(obj_id=obj_id, scope=obj_scope)
        except Project.DoesNotExist:
            return JsonResponse({
                'result': False,
                'message': 'project({id}) with scope({scope}) does not exist.'.format(id=obj_id, scope=obj_scope)
            })

        setattr(request, 'project', project)
        return view_func(request, *args, **kwargs)

    return wrapper


def api_verify_proj_perms(actions):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def wrapper(request, *args, **kwargs):
            if not getattr(request, 'is_trust', False):

                project = getattr(request, 'project', None)

                if not project:
                    obj_id = kwargs.get('project_id')
                    try:
                        obj_scope = _get_project_scope_from_request(request)
                    except Exception:
                        return JsonResponse({
                            'result': False,
                            'message': 'invalid param format'
                        })

                    try:
                        project = get_project_with(obj_id=obj_id, scope=obj_scope)
                    except Project.DoesNotExist:
                        return JsonResponse({
                            'result': False,
                            'message': 'project{id} with scope{scope} does not exist.'.format(id=obj_id,
                                                                                              scope=obj_scope)
                        })

                verify_or_raise_auth_failed(principal_type='user',
                                            principal_id=request.user.username,
                                            resource=project_resource,
                                            action_ids=[act.id for act in actions],
                                            instance=project,
                                            status=200)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def api_verify_perms(auth_resource, actions, get_kwargs):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def wrapper(request, *args, **kwargs):
            if not getattr(request, 'is_trust', False):
                get_filters = {}
                for kwarg, filter_arg in get_kwargs.items():
                    get_filters[filter_arg] = kwargs.get(kwarg)

                # project_id value replace
                if 'project_id' in get_filters:
                    obj_id = get_filters['project_id']
                    scope = _get_project_scope_from_request(request)
                    try:
                        project = get_project_with(obj_id=obj_id, scope=scope)
                    except Project.DoesNotExist:
                        return JsonResponse({
                            'result': False,
                            'message': 'project{id} with scope{scope} does not exist.'.format(id=obj_id, scope=scope)
                        })
                    get_filters['project_id'] = project.id

                instance = auth_resource.resource_cls.objects.get(**get_filters)

                verify_or_raise_auth_failed(principal_type='user',
                                            principal_id=request.user.username,
                                            resource=auth_resource,
                                            action_ids=[act.id for act in actions],
                                            instance=instance,
                                            status=200)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

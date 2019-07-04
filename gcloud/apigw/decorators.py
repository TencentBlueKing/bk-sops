# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
from functools import wraps

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import available_attrs

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    apigw_required = None

from gcloud.core.models import Business
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import (TaskTemplate,
                                     FILL_PARAMS_PERM_NAME)


WHITE_APPS = ['bk_fta']


def check_white_apps(request):
    if apigw_required is not None:
        app_code = request.jwt.app.app_code
    else:
        app_code = request.META.get('HTTP_BK_APP_CODE')
    if app_code in WHITE_APPS:
        return True
    return False


def get_user_and_biz_info(request, kwargs):
    if apigw_required is not None:
        username = request.jwt.user.username
    else:
        username = request.META.get('HTTP_BK_USERNAME')
    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=username)
    except user_model.DoesNotExist:
        result = {
            'result': False,
            'message': 'user: %s does not exist or has not logged in this APP' % username
        }
        return result

    bk_biz_id = kwargs.get('bk_biz_id')
    try:
        biz = Business.objects.get(cc_id=bk_biz_id)
    except Business.DoesNotExist:
        result = {
            'result': False,
            'message': 'business: %s does not exist' % bk_biz_id
        }
        return result

    result = {
        'result': True,
        'data': {
            'user': user,
            'biz': biz
        }
    }
    return result


def api_check_user_perm_of_business(permit):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            # 应用白名单，免用户校验
            if check_white_apps(request):
                if apigw_required is not None:
                    username = request.jwt.user.username
                else:
                    username = request.META.get('HTTP_BK_USERNAME')
                user_model = get_user_model()
                user, _ = user_model.objects.get_or_create(username=username)
                setattr(request, 'user', user)
                return view_func(request, *args, **kwargs)

            info = get_user_and_biz_info(request, kwargs)
            if not info['result']:
                return JsonResponse(info)
            user = info['data']['user']
            biz = info['data']['biz']
            setattr(request, 'user', user)

            if not user.has_perm(permit, biz):
                result = {
                    'result': False,
                    'message': 'user: %s does not have perm of business: %s' % (user.username, biz.cc_id)
                }
                return JsonResponse(result)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def api_check_user_perm_of_task(permit):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):

            # 应用白名单，免用户校验
            if check_white_apps(request):
                if apigw_required is not None:
                    username = request.jwt.user.username
                else:
                    username = request.META.get('HTTP_BK_USERNAME')
                user_model = get_user_model()
                user, _ = user_model.objects.get_or_create(username=username)
                setattr(request, 'user', user)
                return view_func(request, *args, **kwargs)

            info = get_user_and_biz_info(request, kwargs)
            if not info['result']:
                return JsonResponse(info)
            user = info['data']['user']
            biz = info['data']['biz']
            setattr(request, 'user', user)

            if permit == 'create_task':
                template_id = kwargs.get('template_id')
                try:
                    tmpl = TaskTemplate.objects.get(id=template_id, business=biz)
                except TaskTemplate.DoesNotExist:
                    result = {
                        'result': False,
                        'message': 'template: %s does not exist' % template_id
                    }
                    return JsonResponse(result)
                if not user.has_perm(FILL_PARAMS_PERM_NAME, tmpl):
                    result = {
                        'result': False,
                        'message': 'user: %s does not have perm[%s] of template: %s' % (user.username,
                                                                                        FILL_PARAMS_PERM_NAME,
                                                                                        template_id)
                    }
                    return JsonResponse(result)
            else:
                task_id = kwargs.get('task_id') or request.POST.get('task_id')
                try:
                    taskflow = TaskFlowInstance.objects.get(id=task_id, business=biz)
                except TaskFlowInstance.DoesNotExist:
                    result = {
                        'result': False,
                        'message': 'task: %s does not exist' % task_id
                    }
                    return JsonResponse(result)
                # 判断权限
                if not taskflow.user_has_perm(user, permit):
                    result = {
                        'result': False,
                        'message': 'user: %s does not have perm[execute_task] of task: %s' % (user.username,
                                                                                              task_id)
                    }
                    return JsonResponse(result)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

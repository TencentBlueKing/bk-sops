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

import json
import sys
from functools import wraps

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import available_attrs

from gcloud.commons.template.models import CommonTemplate, CommonTmplPerm
from gcloud.core.models import Business
from gcloud.core.utils import prepare_user_business
from gcloud.commons.template.constants import PermNm
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.conf import settings

if not sys.argv[1:2] == ['test'] and settings.RUN_VER != 'open':
    try:
        from bkoauth.decorators import apigw_required
    except ImportError:
        apigw_required = None
else:
    apigw_required = None

WHITE_APPS = {'bk_fta', 'bk_bcs'}


def check_white_apps(request):
    if apigw_required is not None:
        app_code = request.jwt.app.app_code
    else:
        app_code = request.META.get('HTTP_BK_APP_CODE')
    if app_code in WHITE_APPS:
        return True
    return False


def is_request_from_trust_apps_and_inject_user(request, prepare_biz=False):
    result = check_white_apps(request)
    if result:
        if apigw_required is not None:
            username = request.jwt.user.username
        else:
            username = request.META.get('HTTP_BK_USERNAME')
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(username=username)
        setattr(request, 'user', user)
        if prepare_biz:
            prepare_user_business(request)

    return result


def business_exist(kwargs):
    bk_biz_id = kwargs.get('bk_biz_id')
    try:
        Business.objects.get(cc_id=bk_biz_id)
    except Business.DoesNotExist:
        return False

    return True


def get_user_and_biz_info_and_inject_user(request, kwargs, prepare_biz=False):
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
            'message': 'user[username=%s] does not exist or has not logged in this APP' % username
        }
        return result

    setattr(request, 'user', user)
    if prepare_biz:
        prepare_user_business(request)

    bk_biz_id = kwargs.get('bk_biz_id')
    try:
        biz = Business.objects.get(cc_id=bk_biz_id)
    except Business.DoesNotExist:
        result = {
            'result': False,
            'message': 'business[bk_biz_id=%s] does not exist' % bk_biz_id
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


def check_user_has_perm_of_template(user, perm, biz, template_source, template_id):
    """
    @summary: 判断用户是否有流程模板/公共流程权限
    @param user:
    @param perm:
    @param biz:
    @param template_source: business or common
    @param template_id:
    @return:
    """
    # 通过业务流程模板创建任务
    if template_source == 'business':
        try:
            tmpl = TaskTemplate.objects.get(id=template_id, business=biz, is_deleted=False)
        except TaskTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'template[id=%s] does not exist' % template_id
            }
            return result
        if not user.has_perm(perm, tmpl):
            result = {
                'result': False,
                'message': ('user[username={username}] does not have perm[perm={perm}] '
                            'of template[id={template_id}]').format(username=user.username,
                                                                    perm=perm,
                                                                    template_id=template_id)
            }
            return result
    # 公共流程
    else:
        try:
            tmpl = CommonTemplate.objects.get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            result = {
                'result': False,
                'message': 'common template[id=%s] does not exist' % template_id
            }
            return result
        template_perm, _ = CommonTmplPerm.objects.get_or_create(common_template_id=template_id,
                                                                biz_cc_id=biz.cc_id)
        perm_name = 'common_%s' % perm
        if not user.has_perm(perm_name, template_perm):
            result = {
                'result': False,
                'message': ('user[username={username}] does not have perm[perm={perm}] '
                            'of common template[id={template_id}]').format(username=user.username,
                                                                           perm=perm_name,
                                                                           template_id=template_id)
            }
            return result
    return {'result': True, 'data': {}}


def api_check_user_perm_of_business(permit):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            # 应用白名单，免用户校验
            if is_request_from_trust_apps_and_inject_user(request, prepare_biz=True):
                if not business_exist(kwargs):
                    return JsonResponse({
                        'result': False,
                        'message': 'business[bk_biz_id=%s] does not exist' % kwargs.get('bk_biz_id')
                    })
                return view_func(request, *args, **kwargs)

            info = get_user_and_biz_info_and_inject_user(request, kwargs, prepare_biz=True)
            if not info['result']:
                return JsonResponse(info)
            user = info['data']['user']
            biz = info['data']['biz']

            if not user.has_perm(permit, biz):
                result = {
                    'result': False,
                    'message': ('user[username={username}] does not have perm of '
                                'business:[bk_biz_id={bk_biz_id}]').format(username=user.username,
                                                                           bk_biz_id=biz.cc_id)
                }
                return JsonResponse(result)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def api_check_user_perm_of_task(perm):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            # 应用白名单，免用户校验
            if is_request_from_trust_apps_and_inject_user(request):
                return view_func(request, *args, **kwargs)

            info = get_user_and_biz_info_and_inject_user(request, kwargs)
            if not info['result']:
                return JsonResponse(info)
            user = info['data']['user']
            biz = info['data']['biz']

            if perm == PermNm.CREATE_TASK_PERM_NAME:
                try:
                    params = json.loads(request.body)
                except Exception:
                    return JsonResponse({'result': False, 'message': 'invalid param format'})

                template_source = params.get('template_source', 'business')
                template_id = kwargs.get('template_id')
                result = check_user_has_perm_of_template(user, perm, biz, template_source, template_id)
                if not result['result']:
                    return JsonResponse(result)
            else:
                task_id = kwargs.get('task_id') or request.POST.get('task_id')
                try:
                    taskflow = TaskFlowInstance.objects.get(id=task_id, business=biz, is_deleted=False)
                except TaskFlowInstance.DoesNotExist:
                    result = {
                        'result': False,
                        'message': 'task[id=%s] does not exist' % task_id
                    }
                    return JsonResponse(result)
                # 判断权限
                if not taskflow.user_has_perm(user, perm):
                    result = {
                        'result': False,
                        'message': ('user[username={username}] does not have perm[perm={perm}] '
                                    'of task[id={task_id}]').format(username=user.username,
                                                                    perm=perm,
                                                                    task_id=task_id)
                    }
                    return JsonResponse(result)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

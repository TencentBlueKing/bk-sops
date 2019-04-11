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

import logging

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.models import Business
from gcloud.config.forms import ConfigForm


logger = logging.getLogger("root")


def biz_config(request, biz_cc_id):
    try:
        business = Business.objects.get(cc_id=biz_cc_id)
    except Business.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'business with id(%s) does not exist' % biz_cc_id
        })

    return JsonResponse({
        'result': True,
        'data': {
            'executor': business.executor,
            'always_use_executor': business.always_use_executor
        }
    })


@require_POST
@check_user_perm_of_business('manage_business')
def biz_executor(request, biz_cc_id):
    """
    @summary: 设置业务的执行者
    @param request:
    @param biz_cc_id:
    @return:
    """
    form = ConfigForm(request.POST)
    if not form.is_valid():
        return JsonResponse({
            'result': False,
            'message': form.errors
        })
    executor = form.clean()['executor']
    always_use_executor = form.clean()['always_use_executor']
    business = Business.objects.get(cc_id=biz_cc_id)
    if not executor:
        if always_use_executor:
            result = {
                'result': False,
                'message': 'can not turn on force use when executor is empty'
            }
            return JsonResponse(result)
        business.executor = ''
        business.always_use_executor = False
        business.save()
        result = {
            'result': True,
            'data': '',
        }
        return JsonResponse(result)
    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=executor)
    except user_model.DoesNotExist:
        logger.warning('set biz_executor failed: %s not found in User' % executor)
        result = {
            'result': False,
            'message': '%s has not logged in this APP' % executor
        }
        return JsonResponse(result)
    if not user.has_perm("manage_business", business):
        result = {
            'result': False,
            'message': '%s is not a maintainer,please add on Conf System(CC) first' % executor
        }
        return JsonResponse(result)
    business.executor = executor
    business.always_use_executor = always_use_executor
    business.save()
    result = {
        'result': True,
        'data': '',
    }
    return JsonResponse(result)

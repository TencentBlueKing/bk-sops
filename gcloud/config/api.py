# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.models import Business

logger = logging.getLogger("root")


@require_POST
@check_user_perm_of_business('manage_business')
def biz_executor(request, biz_cc_id):
    """
    @summary: 设置业务的执行者
    @param request:
    @param biz_cc_id:
    @return:
    """
    executor = request.POST.get('executor', '')
    business = Business.objects.get(cc_id=biz_cc_id)
    if not executor:
        business.executor = ''
        business.save()
        result = {
            'result': True,
            'data': '',
        }
        return JsonResponse(result)
    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=executor)
    except user_model.DoesNotExist as e:
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
    business.save()
    result = {
        'result': True,
        'data': '',
    }
    return JsonResponse(result)

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


from tastypie.exceptions import ImmediateHttpResponse

from iam import Request
from iam.exceptions import AuthFailedException, MultiAuthFailedException
from iam.contrib.django.response import IAMAuthFailedResponse


def allow_or_raise_immediate_response(iam, system, subject, action, resources, environment=None):
    request = Request(system, subject, action, resources, environment)

    allowed = iam.is_allowed(request)

    if not allowed:
        raise ImmediateHttpResponse(IAMAuthFailedResponse(AuthFailedException(system, subject, action, resources)))

    return


def allow_or_raise_immediate_response_for_resources_list(
    iam, system, subject, action, resources_list, environment=None
):
    if not resources_list:
        return

    resources_map = {}
    for resources in resources_list:
        resources_map[resources[0].id] = resources

    request = Request(system, subject, action, [], environment)
    result = iam.batch_is_allowed(request, resources_list)

    if not result:
        raise MultiAuthFailedException(system, subject, action, resources_list)

    not_allowed_list = []
    for tid, allow in result.items():
        if not allow:
            not_allowed_list.append(resources_map[tid])

    if not_allowed_list:
        raise MultiAuthFailedException(system, subject, action, not_allowed_list)

    return

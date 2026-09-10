# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.request_resources import load_resource_for_request


class TaskViewInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        tenant_id = request.user.tenant_id
        task_id = kwargs["task_id"]
        resource = load_resource_for_request(request, IAMMeta.TASK_RESOURCE, task_id)
        if request.is_trust:
            return

        PermissionService().require(
            request.user.username,
            tenant_id,
            PermissionCheck(IAMMeta.TASK_VIEW_ACTION, resource),
        )

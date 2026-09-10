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

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.scope_resolver import ScopeResolver


class FunctionViewInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        if request.is_trust:
            request._function_project_ids = None
            request._function_task_ids = None
            return

        tenant_id = request.user.tenant_id
        resolver = ScopeResolver()
        request._function_project_ids = resolver.authorized_scope(
            request.user.username, tenant_id, IAMMeta.FUNCTION_TASK_VIEW_ACTION
        ).ids(IAMMeta.PROJECT_RESOURCE)
        request._function_task_ids = resolver.authorized_scope(
            request.user.username, tenant_id, IAMMeta.TASK_VIEW_ACTION
        ).ids(IAMMeta.TASK_RESOURCE)

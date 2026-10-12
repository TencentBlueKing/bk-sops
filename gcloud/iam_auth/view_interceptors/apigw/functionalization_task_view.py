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

from gcloud.apigw.forms.get_functionalization_task_list import GetFunctionalizationTaskListForm
from gcloud.contrib.function.models import FunctionTask
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
        scope_kwargs = {}
        params = GetFunctionalizationTaskListForm(data=request.GET)
        if params.is_valid():
            project_id = params.cleaned_data.get("project_id")
            if project_id is not None:
                scope_kwargs["project_id"] = project_id
            task_ids = params.cleaned_data.get("task_id_in")
            valid_task_ids = task_ids and all(task_id.isdecimal() for task_id in task_ids)
            function_task_ids = params.cleaned_data.get("id_in")
            if function_task_ids and all(task_id.isdecimal() for task_id in function_task_ids):
                candidates = FunctionTask.objects.filter(id__in=function_task_ids, task__project__tenant_id=tenant_id)
                if project_id is not None:
                    candidates = candidates.filter(task__project_id=project_id)
                if valid_task_ids:
                    candidates = candidates.filter(task_id__in=task_ids)
                scope_kwargs["resource_ids"] = candidates.values_list("task_id", flat=True)
            elif valid_task_ids:
                scope_kwargs["resource_ids"] = task_ids
        resolver = ScopeResolver()
        project_scope = resolver.authorized_scope(request.user.username, tenant_id, IAMMeta.FUNCTION_TASK_VIEW_ACTION)
        task_scope = resolver.authorized_scope(
            request.user.username, tenant_id, IAMMeta.TASK_VIEW_ACTION, **scope_kwargs
        )
        project_queryset = project_scope.queryset(IAMMeta.PROJECT_RESOURCE)
        task_queryset = task_scope.queryset(IAMMeta.TASK_RESOURCE)
        request._function_project_ids = (
            project_queryset.values("id")
            if project_queryset is not None
            else project_scope.ids(IAMMeta.PROJECT_RESOURCE)
        )
        request._function_task_ids = (
            task_queryset.values("id") if task_queryset is not None else task_scope.ids(IAMMeta.TASK_RESOURCE)
        )

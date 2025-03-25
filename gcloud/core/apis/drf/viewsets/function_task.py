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
from django.db.models import Value
from rest_framework import permissions

from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.contrib.function.models import FunctionTask
from gcloud.core.apis.drf.permission import IamPermission, IamPermissionInfo
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers.function_task import FunctionTaskSerializer
from gcloud.core.apis.drf.viewsets import GcloudListViewSet
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.iam_auth.conf import TASK_ACTIONS


class FunctionTaskPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.FUNCTION_VIEW_ACTION),
    }


class FunctionTaskViewSet(GcloudListViewSet):
    queryset = FunctionTask.objects.filter(task__is_deleted=Value(0))
    serializer_class = FunctionTaskSerializer
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_function_task_obj, actions=TASK_ACTIONS, id_field="task.id"
    )
    permission_classes = [permissions.IsAuthenticated, FunctionTaskPermission]
    filter_fields = {
        "id": ["exact"],
        "task_id": ["exact"],
        "task__project__id": ["exact"],
        "task__pipeline_instance__name": ["icontains", "contains"],
        "task__pipeline_instance__is_started": ["exact"],
        "task__pipeline_instance__is_finished": ["exact"],
        "task__pipeline_instance__is_revoked": ["exact"],
        "creator": ["exact", "icontains"],
        "claimant": ["exact", "icontains"],
        "status": ["exact"],
        "create_time": ["gte", "lte"],
        "claim_time": ["gte", "lte"],
    }
    taskflow_multi_tenant_filter = True

    def list(self, request, *args, **kwargs):
        bk_audit_add_event(username=request.user.username, action_id=IAMMeta.FUNCTION_VIEW_ACTION)
        return super(FunctionTaskViewSet, self).list(request, *args, **kwargs)

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from rest_framework import permissions

from gcloud.core.apis.drf.viewsets import GcloudListViewSet
from gcloud.contrib.function.models import FunctionTask
from gcloud.core.apis.drf.serilaziers.function_task import FunctionTaskSerializer
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.iam_auth import res_factory, IAMMeta
from gcloud.iam_auth.conf import TASK_ACTIONS
from gcloud.core.apis.drf.permission import IamPermissionInfo, IamPermission


class FunctionTaskPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.FUNCTION_VIEW_ACTION),
    }


class FunctionTaskViewSet(GcloudListViewSet):
    queryset = FunctionTask.objects.filter(task__is_deleted=False)
    serializer_class = FunctionTaskSerializer
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_function_task_obj, actions=TASK_ACTIONS
    )
    permission_classes = [permissions.IsAuthenticated, FunctionTaskPermission]
    filter_fields = {
        "task__project__id": ["exact"],
        "creator": ["exact", "icontains"],
        "claimant": ["exact", "icontains"],
        "status": ["exact"],
        "create_time": ["gte", "lte"],
        "claim_time": ["gte", "lte"],
    }

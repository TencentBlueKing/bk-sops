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

from rest_framework.pagination import LimitOffsetPagination
from rest_framework import mixins

from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.apis.drf.serilaziers.appmaker import AppmakerSerializer
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import IAMMeta
from gcloud.core.apis.drf.permission import IamPermission, IamPermissionInfo, HAS_OBJECT_PERMISSION


class AppmakerPermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(
            IAMMeta.PROJECT_VIEW_ACTION, res_factory.resources_for_project, id_field="project__id"
        ),
        "destroy": IamPermissionInfo(
            IAMMeta.MINI_APP_DELETE_ACTION, res_factory.resources_for_mini_app_obj, HAS_OBJECT_PERMISSION
        ),
    }


class AppmakerListViewSet(GcloudListViewSet, mixins.DestroyModelMixin):
    queryset = AppMaker.objects.filter(is_deleted=False)
    serializer_class = AppmakerSerializer
    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_mini_app_obj,
        actions=[
            IAMMeta.MINI_APP_CREATE_TASK_ACTION,
            IAMMeta.MINI_APP_DELETE_ACTION,
            IAMMeta.MINI_APP_EDIT_ACTION,
            IAMMeta.MINI_APP_VIEW_ACTION,
        ],
    )
    filter_fields = {"editor": ["exact"], "project__id": ["exact"], "edit_time": ["gte", "lte"]}
    pagination_class = LimitOffsetPagination

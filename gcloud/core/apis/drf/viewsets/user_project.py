# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination

from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.iam_auth.utils import get_user_projects

from gcloud.core.models import Project
from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.serilaziers import ProjectSerializer
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper

from .base import GcloudListViewSet


class UserProjectFilter(AllLookupSupportFilterSet):
    class Meta:
        model = Project
        fields = {
            "is_disable": ALL_LOOKUP,
            "id": ["exact"],
            "bk_biz_id": ["exact"],
            "name": ["icontains"],
            "desc": ["icontains"],
            "creator": ["exact"],
        }


class UserProjectSetViewSet(GcloudListViewSet):
    queryset = Project.objects.all().order_by("-id")
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = UserProjectFilter
    pagination_class = LimitOffsetPagination
    search_fields = ["id", "name", "desc", "creator", "bk_biz_id"]

    iam_resource_helper = ViewSetResourceHelper(
        resource_func=res_factory.resources_for_project_obj,
        actions=[
            IAMMeta.PROJECT_VIEW_ACTION,
            IAMMeta.PROJECT_EDIT_ACTION,
            IAMMeta.FLOW_CREATE_ACTION,
            IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
        ],
    )

    def list(self, request, *args, **kwargs):
        self.queryset = get_user_projects(request.user.username)
        return super(UserProjectSetViewSet, self).list(request, *args, **kwargs)

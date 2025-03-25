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

from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.serilaziers import CommonProjectSerializer
from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet
from gcloud.core.models import ProjectCounter
from gcloud.iam_auth.utils import get_user_projects


class CommonProjectFilter(AllLookupSupportFilterSet):
    class Meta:
        model = ProjectCounter
        fields = {
            "id": ["exact"],
            "username": ALL_LOOKUP,
            "count": ALL_LOOKUP,
        }


class CommonProjectViewSet(GcloudListViewSet):
    queryset = ProjectCounter.objects.all().order_by("-count")
    search_fields = ["id", "username", "count", "project__name"]
    serializer_class = CommonProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = CommonProjectFilter
    project_multi_tenant_filter = True

    @staticmethod
    def get_default_projects(username, tenant_id):
        """初始化并返回用户有权限的项目"""

        projects = get_user_projects(username, tenant_id)
        if not projects:
            return ProjectCounter.objects.none()

        project_ids = projects.values_list("id", flat=True)

        # 初始化用户有权限的项目
        ProjectCounter.objects.bulk_create(
            [
                ProjectCounter(username=username, project_id=project_id)
                for project_id in project_ids
            ]
        )

        return ProjectCounter.objects.filter(username=username, project_id__in=project_ids, project__is_disable=False)

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(username=request.user.username, project__is_disable=False)

        # 第一次访问或无被授权的项目
        if not self.queryset.exists():
            self.queryset = self.get_default_projects(request.user.username, tenant_id=request.user.tenant_id)
        return super(CommonProjectViewSet, self).list(request, *args, **kwargs)

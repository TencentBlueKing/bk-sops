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
import logging

from django.db import IntegrityError
from django.db.models import BooleanField, ExpressionWrapper, Q
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.filtersets import ALL_LOOKUP, AllLookupSupportFilterSet
from gcloud.core.apis.drf.resource_helpers import ViewSetResourceHelper
from gcloud.core.apis.drf.serilaziers import ProjectWithFavSerializer
from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, res_factory
from gcloud.iam_auth.utils import get_user_projects

from .base import GcloudListViewSet

logger = logging.getLogger("root")


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
    serializer_class = ProjectWithFavSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = UserProjectFilter
    pagination_class = LimitOffsetPagination
    search_fields = ["id", "name", "desc", "creator", "bk_biz_id"]
    model_multi_tenant_filter = True

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
        user_project_ids = list(
            get_user_projects(request.user.username, request.user.tenant_id).values_list("id", flat=True)
        )
        user_fav_project_ids = list(Collection.objects.get_user_favorite_projects(request.user.username))
        self.list_queryset = (
            Project.objects.filter(id__in=user_project_ids)
            .annotate(is_fav=ExpressionWrapper(Q(id__in=user_fav_project_ids), output_field=BooleanField()))
            .order_by("-is_fav", "id")
        )
        return super(UserProjectSetViewSet, self).list(request, *args, **kwargs)

    @action(methods=["post"], detail=True)
    def favor(self, request, *args, **kwargs):
        try:
            Collection.objects.add_user_favorite_project(request.user.username, self.get_object())
        except IntegrityError as e:
            logger.exception(e)
            return Response({"result": False, "data": None, "message": "该用户已收藏该项目"}, status=400)
        return Response({"result": True, "data": "success", "message": ""})

    @action(methods=["delete"], detail=True)
    def cancel_favor(self, request, *args, **kwargs):
        project_id = kwargs["pk"]
        Collection.objects.remove_user_favorite_project(request.user.username, project_id)
        return Response({"result": True, "data": "success", "message": ""})

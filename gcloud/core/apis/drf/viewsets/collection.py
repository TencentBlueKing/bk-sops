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

import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, permissions, status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from gcloud import err_code
from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.serilaziers.collection import CollectionSerializer
from gcloud.core.apis.drf.viewsets import GcloudReadOnlyViewSet
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import utils as iam_auth_utils
from gcloud.iam_auth.utils import get_user_projects

logger = logging.getLogger("root")


class CollectionPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        action = view.action
        if action in ["retrieve", "destroy"]:
            return request.user.username == obj.username


class CollectionViewSet(GcloudReadOnlyViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, CollectionPermission]
    filter_fields = ["id", "category"]
    append_resource_actions = {
        IAMMeta.FLOW_RESOURCE: [
            IAMMeta.FLOW_VIEW_ACTION,
            IAMMeta.FLOW_CREATE_TASK_ACTION,
            IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
        ],
        IAMMeta.COMMON_FLOW_RESOURCE: [IAMMeta.COMMON_FLOW_VIEW_ACTION],
        IAMMeta.MINI_APP_RESOURCE: [IAMMeta.MINI_APP_VIEW_ACTION],
    }

    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(username=self.request.user.username)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for item in serializer.validated_data:
            username = item["username"]
            category = item["category"]
            instance_id = item["instance_id"]
            if Collection.objects.filter(username=username, category=category, instance_id=instance_id).exists():
                message = _(f"重复收藏: {username}实例ID: {category}, 类别: {instance_id}, 已经收藏过了, 无需再次收藏")
                logger.error(message)
                return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def injection_auth_actions(self, request, serializer_data, queryset_data):
        # 计算项目之下其他资源的权限
        resource_id_list_map = {r_type: [] for r_type in self.append_resource_actions}

        resource_allowed_actions_map = {}
        if not isinstance(serializer_data, list):
            serializer_data = [serializer_data]
        for item in serializer_data:
            if item["category"] in resource_id_list_map:
                resource_id_list_map[item["category"]].append(item["extra_info"]["id"])

        for r_type, id_list in resource_id_list_map.items():
            resource_allowed_actions_map[r_type] = getattr(
                iam_auth_utils, "get_{}_allowed_actions_for_user".format(r_type)
            )(request.user.username, self.append_resource_actions[r_type], id_list)

        # 计算有查看权限的项目资源
        user_projects = set(
            get_user_projects(request.user.username, request.user.tenant_id).values_list("id", flat=True)
        )

        for item in serializer_data:
            if item["category"] == "project":
                item["auth_actions"] = [IAMMeta.PROJECT_VIEW_ACTION] if item["instance_id"] in user_projects else []
                continue

            if item["category"] not in resource_allowed_actions_map:
                item["auth_actions"] = []
                continue

            resource_allowed_actions = resource_allowed_actions_map[item["category"]]

            item["auth_actions"] = [
                act for act, allow in resource_allowed_actions.get(str(item["extra_info"]["id"]), {}).items() if allow
            ]
        return serializer_data

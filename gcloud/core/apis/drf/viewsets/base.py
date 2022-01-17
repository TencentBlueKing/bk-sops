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
import logging
from collections import Iterable

from django.conf import settings
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from django_filters.rest_framework import DjangoFilterBackend

from gcloud.iam_auth import get_iam_client
from gcloud.core.apis.drf.viewsets import IAMMixin, ApiMixin
from gcloud.core.apis.drf.authentication import CsrfExemptSessionAuthentication

iam = get_iam_client()
iam_logger = logging.getLogger("iam")


class GcloudLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10


class GcloudCommonMixin(IAMMixin, ApiMixin):
    pagination_class = GcloudLimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    # 开发环境csrf豁免
    if settings.RUN_MODE == "DEVELOP":
        authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        self.queryset = {
            "list": self.queryset,
            "retrieve": getattr(self, "detail_queryset", self.queryset),
        }.get(self.action, self.queryset)

        return super(GcloudCommonMixin, self).get_queryset()

    def get_serializer_class(self):
        self.serializer_class = {
            "list": self.serializer_class,
            "retrieve": getattr(self, "detail_serializer_class", self.serializer_class),
            "update": getattr(self, "update_serializer_class", self.serializer_class),
            "crate": getattr(self, "create_serializer_class", self.serializer_class),
        }.get(self.action, self.serializer_class)

        return super(GcloudCommonMixin, self).get_serializer_class()

    def injection_auth_actions(self, request, serializer_data, queryset_data):
        """注入auth_action"""
        if isinstance(queryset_data, Iterable):
            auth_actions = self.iam_get_instances_auth_actions(request, list(queryset_data))
            if auth_actions:
                for data in serializer_data:
                    data["auth_actions"] = auth_actions[data["id"]]
        else:
            auth_actions = self.iam_get_instance_auth_actions(request, queryset_data)
            if auth_actions:
                serializer_data["auth_actions"] = auth_actions
        return serializer_data


class GcloudListViewSet(GcloudCommonMixin):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, queryset)
        return self.get_paginated_response(data) if page is not None else Response(data)


class GcloudRetrieveViewSet(GcloudCommonMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, instance)
        return Response(data)


class GcloudUpdateViewSet(mixins.UpdateModelMixin, GcloudRetrieveViewSet):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, instance)
        return Response(data)


class GcloudReadOnlyViewSet(GcloudListViewSet, GcloudRetrieveViewSet):
    """只读"""

    pass

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
from collections.abc import Iterable

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from gcloud.core.apis.drf.viewsets import ApiMixin, IAMMixin
from gcloud.core.apis.drf.viewsets.utils import MultiTenantMixin
from gcloud.iam_auth import get_iam_client

iam = get_iam_client()
iam_logger = logging.getLogger("iam")


class GcloudLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10


class GcloudOrderingFilter(OrderingFilter):
    ordering_param = "order_by"


class GcloudCommonMixin(IAMMixin, ApiMixin):
    pagination_class = GcloudLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, GcloudOrderingFilter)

    def get_queryset(self):
        """支持不同acton调用不同的queryset"""
        self.queryset = getattr(self, f"{self.action}_queryset", self.queryset)
        return super(GcloudCommonMixin, self).get_queryset()

    def get_serializer_class(self):
        """支持不同acton调用不同的serializer_class"""
        self.serializer_class = getattr(self, f"{self.action}_serializer_class", self.serializer_class)
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


class GcloudListViewSet(MultiTenantMixin, GcloudCommonMixin):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持使用方配置不分页
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, serializer.instance)
        return self.get_paginated_response(data) if page is not None else Response(data)


class GcloudRetrieveViewSet(GcloudCommonMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, instance)
        return Response(data)


class GcloudUpdateViewSet(generics.UpdateAPIView, GcloudRetrieveViewSet):
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
    pass


class GcloudReadOnlyUpdateViewSet(GcloudUpdateViewSet, GcloudReadOnlyViewSet):
    pass


class GcloudModelViewSet(GcloudReadOnlyViewSet, generics.CreateAPIView, generics.DestroyAPIView, GcloudUpdateViewSet):
    """
    crate 和 destroy 方法使用原生实现。如有需要，可自行重写方法
    """

    pass

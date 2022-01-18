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
from django.db.models import Q
from rest_framework import permissions
from django_filters import CharFilter

from pipeline.component_framework.models import ComponentModel
from gcloud.core.models import ProjectBasedComponent

from .base import GcloudReadOnlyViewSet
from ..filter import VarietyFilterSet
from ..serilaziers.component_model import ListSerializer, DetailSerializer


class ComponentModelFilter(VarietyFilterSet):
    project_id = CharFilter(method="filter_by_project_id")

    def filter_by_project_id(self, queryset, name, value):
        if value:
            exclude_component_codes = ProjectBasedComponent.objects.get_components_of_other_projects(value)
        else:
            exclude_component_codes = ProjectBasedComponent.objects.get_components()
        query_set = ~Q(code__in=exclude_component_codes)

        return queryset.filter(query_set)

    class Meta:
        model = ComponentModel
        fields = ["version"]


class ComponentModelSetViewSet(GcloudReadOnlyViewSet):
    queryset = ComponentModel.objects.filter(status=True).exclude(code="remote_plugin").order_by("name")
    detail_queryset = ComponentModel.objects.filter(status=True).order_by("name")

    serializer_class = ListSerializer
    detail_serializer_class = DetailSerializer

    permission_classes = [permissions.IsAuthenticated]

    filterset_class = ComponentModelFilter
    lookup_field = "code"

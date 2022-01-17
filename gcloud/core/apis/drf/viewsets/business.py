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
from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import Business

from .base import GcloudReadOnlyViewSet
from ..filter import VarietyFilterSet, ALL
from ..serilaziers import BusinessSerializer


class BusinessFilter(VarietyFilterSet):
    class Meta:
        model = Business
        fields = {
            "cc_id": ALL,
            "cc_name": ALL,
            "cc_owner": ALL,
            "cc_company": ALL,
        }


class BusinessSetViewSet(GcloudReadOnlyViewSet):
    queryset = Business.objects.exclude(status="disabled").exclude(
        life_cycle__in=[Business.LIFE_CYCLE_CLOSE_DOWN, _("停运")]
    )
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = BusinessFilter

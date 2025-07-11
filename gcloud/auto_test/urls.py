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
from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from gcloud.auto_test.apis.viewsets.periodic_task import PeriodicTaskViewSet
from gcloud.auto_test.apis.viewsets.template import CommonTemplateViewSet, ProjectTemplateViewSet
from gcloud.auto_test.apis.viewsets.token import AutoTestTokenViewSet

auto_test_router = DefaultRouter()
auto_test_router.register(r"template", ProjectTemplateViewSet, basename="template")
auto_test_router.register(r"common_template", CommonTemplateViewSet, basename="common_template")
auto_test_router.register(r"periodic_task", PeriodicTaskViewSet, basename="periodic_task")
auto_test_router.register(r"get_token", AutoTestTokenViewSet, basename="get_token")

urlpatterns = [
    re_path(r"^", include(auto_test_router.urls)),
]

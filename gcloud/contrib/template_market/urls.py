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

from gcloud.contrib.template_market.viewsets import TemplatePreviewAPIView, TemplateSceneViewSet

template_market_router = DefaultRouter()
template_market_router.register(r"templates_scene", TemplateSceneViewSet)

urlpatterns = [
    re_path(r"^api/", include(template_market_router.urls)),
    re_path(r"^api/template_preview/$", TemplatePreviewAPIView.as_view()),
]

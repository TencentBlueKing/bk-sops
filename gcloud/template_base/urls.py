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

from .apis.django import api
from .apis.drf.viewsets import DefaultTemplateSchemeViewSet

router = DefaultRouter()
router.register(r"default_scheme", DefaultTemplateSchemeViewSet)


urlpatterns = [
    re_path(r"^api/upload_yaml_templates/$", api.upload_and_check_yaml_templates),
    re_path(r"^api/export_yaml_templates/$", api.export_yaml_templates),
    re_path(r"^api/import_yaml_templates/$", api.import_yaml_templates),
    re_path(r"^api/", include(router.urls)),
]

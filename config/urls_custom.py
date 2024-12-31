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
from django.conf import settings
from django.urls import include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# 用户自定义 urlconf
urlpatterns_custom = [
    re_path(r"^", include("gcloud.core.urls")),
    re_path(r"^", include("gcloud.resources.urls")),
    re_path(r"^apigw/", include("gcloud.apigw.urls")),
    re_path(r"^common_template/", include("gcloud.common_template.urls")),
    re_path(r"^template/", include("gcloud.tasktmpl3.urls")),
    re_path(r"^template/", include("gcloud.template_base.urls")),
    re_path(r"^taskflow/", include("gcloud.taskflow3.urls")),
    re_path(r"^appmaker/", include("gcloud.contrib.appmaker.urls")),
    re_path(r"^collection/", include("gcloud.contrib.collection.urls")),
    re_path(r"^develop/", include("gcloud.contrib.develop.urls")),
    re_path(r"^function/", include("gcloud.contrib.function.urls")),
    re_path(r"^pipeline/", include("pipeline_plugins.base.urls")),
    re_path(r"^pipeline/", include("pipeline_plugins.components.urls")),
    re_path(r"^pipeline/", include("pipeline_plugins.variables.urls")),
    re_path(r"^analysis/", include("gcloud.contrib.analysis.urls")),
    re_path(r"^periodictask/", include("gcloud.periodictask.urls")),
    re_path(r"^weixin/", include("weixin.urls")),
    re_path(r"^weixin/login/", include("weixin.core.urls")),
    re_path(r"^admin/", include("gcloud.contrib.admin.urls")),
    re_path(r"^plugin_service/", include("plugin_service.urls")),
    re_path(r"^mako_operations/", include("gcloud.mako_template_helper.urls")),
    re_path(r"^engine_admin/", include("pipeline.contrib.engine_admin.urls")),
]

schema_view = get_schema_view(
    openapi.Info(
        title="BK-SOPS API",
        default_version="v1",
        description="标准运维API文档，接口返回中默认带有result、data、message等字段，如果响应体中没有体现，则说明响应体只展示了其中data字段的内容。",
    ),
    public=True,
    permission_classes=(permissions.IsAdminUser,),
)


if settings.ENVIRONMENT != "production" or settings.ENABLE_SWAGGER_UI:
    urlpatterns_custom += [
        re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]

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

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from weixin.viewsets import (
    WxCollectionViewSet,
    WxComponentModelSetViewSet,
    WxProjectViewSet,
    WxTaskFlowInstanceViewSet,
    WxTaskTemplateViewSet,
    WxTemplateSchemeViewSet,
    WxUserProjectViewSet,
    WxWxVariableViewSet,
)

from . import views

weixin_v3_drf_api = DefaultRouter()
weixin_v3_drf_api.register("weixin_template", WxTaskTemplateViewSet)
weixin_v3_drf_api.register("weixin_taskflow", WxTaskFlowInstanceViewSet)
weixin_v3_drf_api.register("weixin_component", WxComponentModelSetViewSet)
weixin_v3_drf_api.register("weixin_variable", WxWxVariableViewSet)
weixin_v3_drf_api.register("weixin_scheme", WxTemplateSchemeViewSet)
weixin_v3_drf_api.register("weixin_user_project", WxUserProjectViewSet)
weixin_v3_drf_api.register("weixin_project", WxProjectViewSet, basename="weixin_project")
weixin_v3_drf_api.register("weixin_collection", WxCollectionViewSet)


urlpatterns = [
    re_path(r"^$", views.home),
    re_path(r"^taskflow/", include("gcloud.taskflow3.urls")),
    re_path(r"^template/", include("gcloud.tasktmpl3.urls")),
    path(r"api/v3/", include(weixin_v3_drf_api.urls)),
]

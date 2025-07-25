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

URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import static

from config.urls_custom import urlpatterns_custom
from gcloud.core.views import page_not_found

urlpatterns = [
    re_path(r"^django_admin/", admin.site.urls),
    re_path(r"^account/", include("blueapps.account.urls")),
    re_path(r"^notice/", include("bk_notice_sdk.urls")),
]

# app自定义路径
urlpatterns += urlpatterns_custom

if settings.IS_LOCAL:
    urlpatterns += [
        # media
        re_path(r"^media/(?P<path>.*)$", static.serve, {"document_root": settings.MEDIA_ROOT}),
        path("favicon.ico", static.serve, {"document_root": settings.STATIC_ROOT, "path": "core/images/bk_sops.png"}),
    ]
    if not settings.DEBUG:
        urlpatterns += [
            re_path(r"^static/(?P<path>.*)$", static.serve, {"document_root": settings.STATIC_ROOT}),
        ]

handler404 = page_not_found

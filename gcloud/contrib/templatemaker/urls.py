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

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from gcloud.contrib.templatemaker.apis.drf.viewsets import TemplateMakerViewSet
from gcloud.contrib.templatemaker.apis.django import api

drf_api = DefaultRouter()
drf_api.register(r"template", TemplateMakerViewSet)

urlpatterns = [
    url(r"^api/maker/", include(drf_api.urls)),
    url(r"^api/process_maker/(?P<template_id>\d+)/", api.maker_template),
    url(r"^api/template_detail/(?P<template_id>\d+)/", api.get_template_market_details),
]

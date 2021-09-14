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
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request

from plugin_service.decorators import inject_plugin_client
from plugin_service.plugin_client import PluginServiceApiClient
from plugin_service.serializers import (
    PluginListResponseSerializer,
    DetailResponseSerializer,
    MetaResponseSerializer,
    LogResponseSerializer,
    LogQuerySerializer,
    PluginVersionQuerySerializer,
    PluginCodeQuerySerializer,
    PluginListQuerySerializer,
    PluginAppDetailResponseSerializer,
)


@swagger_auto_schema(
    method="GET", query_serializer=PluginListQuerySerializer, responses={200: PluginListResponseSerializer}
)
@api_view(["GET"])
def get_plugin_list(request: Request):
    """ 获取插件服务列表信息 """
    search_term = request.query_params.get("search_term")
    limit = request.query_params.get("limit")
    offset = request.query_params.get("offset")
    result = PluginServiceApiClient.get_plugin_list(search_term=search_term, limit=limit, offset=offset)
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET", query_serializer=PluginVersionQuerySerializer, responses={200: DetailResponseSerializer}
)
@api_view(["GET"])
@inject_plugin_client
def get_plugin_detail(request: Request):
    """ 获取插件服务详情 """
    plugin_version = request.query_params.get("plugin_version")
    result = request.plugin_client.get_detail(plugin_version)
    return JsonResponse(result)


@swagger_auto_schema(method="GET", query_serializer=PluginCodeQuerySerializer, responses={200: MetaResponseSerializer})
@api_view(["GET"])
@inject_plugin_client
def get_meta(request: Request):
    """ 获取插件服务元信息 """
    return JsonResponse(request.plugin_client.get_meta())


@swagger_auto_schema(method="GET", query_serializer=LogQuerySerializer, responses={200: LogResponseSerializer})
@api_view(["GET"])
@inject_plugin_client
def get_logs(request: Request):
    """ 获取插件服务执行日志 """
    trace_id = request.query_params.get("trace_id")
    result = request.plugin_client.get_logs(trace_id)
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET", query_serializer=PluginCodeQuerySerializer, responses={200: PluginAppDetailResponseSerializer}
)
@api_view(["GET"])
def get_plugin_app_detail(request: Request):
    """获取插件服务App详情"""
    result = PluginServiceApiClient.get_plugin_app_detail(request.query_params.get("plugin_code"))
    if result["result"] and "url" in result["data"]:
        result["data"].pop("url")
    return JsonResponse(result)

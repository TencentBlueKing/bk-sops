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

from plugin_service.decorators import inject_plugin_client, validate_params
from plugin_service.plugin_client import PluginServiceApiClient
from plugin_service.serializers import (
    PluginListResponseSerializer,
    DetailResponseSerializer,
    MetaResponseSerializer,
    LogResponseSerializer,
    LogQuerySerializer,
    PluginDetailQuerySerializer,
    PluginCodeQuerySerializer,
    PluginListQuerySerializer,
    PluginAppDetailResponseSerializer,
)


@swagger_auto_schema(
    method="GET", query_serializer=PluginListQuerySerializer, responses={200: PluginListResponseSerializer}
)
@api_view(["GET"])
@validate_params(PluginListQuerySerializer)
def get_plugin_list(request: Request):
    """ 获取插件服务列表信息 """
    search_term = request.validated_data.get("search_term")
    limit = request.validated_data.get("limit")
    offset = request.validated_data.get("offset")
    result = PluginServiceApiClient.get_plugin_list(search_term=search_term, limit=limit, offset=offset)
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET", query_serializer=PluginDetailQuerySerializer, responses={200: DetailResponseSerializer}
)
@api_view(["GET"])
@validate_params(PluginDetailQuerySerializer)
@inject_plugin_client
def get_plugin_detail(request: Request):
    """ 获取插件服务详情 """
    plugin_version = request.validated_data.get("plugin_version")
    with_app_detail = request.validated_data.get("with_app_detail")
    plugin_detail = request.plugin_client.get_detail(plugin_version)
    if not plugin_detail["result"]:
        return JsonResponse(plugin_detail)
    if with_app_detail:
        app_detail = PluginServiceApiClient.get_plugin_app_detail(request.validated_data.get("plugin_code"))
        if not app_detail["result"]:
            return JsonResponse(app_detail)
        plugin_detail["data"]["app"] = app_detail["data"]
    return JsonResponse(plugin_detail)


@swagger_auto_schema(method="GET", query_serializer=PluginCodeQuerySerializer, responses={200: MetaResponseSerializer})
@api_view(["GET"])
@validate_params(PluginCodeQuerySerializer)
@inject_plugin_client
def get_meta(request: Request):
    """ 获取插件服务元信息 """
    return JsonResponse(request.plugin_client.get_meta())


@swagger_auto_schema(method="GET", query_serializer=LogQuerySerializer, responses={200: LogResponseSerializer})
@api_view(["GET"])
@validate_params(LogQuerySerializer)
def get_logs(request: Request):
    """ 获取插件服务执行日志 """
    trace_id = request.validated_data.get("trace_id")
    scroll_id = request.validated_data.get("scroll_id")
    plugin_code = request.validated_data.get("plugin_code")
    result = PluginServiceApiClient.get_plugin_logs(plugin_code, trace_id, scroll_id)
    if result["result"]:
        logs = [
            f'[{log["ts"]}]{log["detail"]["json.levelname"]}-{log["detail"]["json.funcName"]}: '
            f'{log["detail"]["json.message"]}'
            for log in result["data"]["logs"]
        ]
        result["data"]["logs"] = "\n".join(logs)
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET", query_serializer=PluginCodeQuerySerializer, responses={200: PluginAppDetailResponseSerializer}
)
@api_view(["GET"])
@validate_params(PluginCodeQuerySerializer)
def get_plugin_app_detail(request: Request):
    """获取插件服务App详情"""
    result = PluginServiceApiClient.get_plugin_app_detail(request.validated_data.get("plugin_code"))
    return JsonResponse(result)

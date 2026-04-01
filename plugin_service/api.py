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
import logging

from django.conf import settings
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from plugin_service import env
from plugin_service.api_decorators import inject_plugin_client, validate_params
from plugin_service.conf import PLUGIN_DISTRIBUTOR_NAME, PLUGIN_LOGGER
from plugin_service.exceptions import PluginServiceException
from plugin_service.plugin_client import PluginServiceApiClient
from plugin_service.serializers import (
    DetailResponseSerializer,
    LogQuerySerializer,
    LogResponseSerializer,
    MetaResponseSerializer,
    PluginAppDetailResponseSerializer,
    PluginCodeQuerySerializer,
    PluginDetailListQuerySerializer,
    PluginDetailListResponseSerializer,
    PluginDetailQuerySerializer,
    PluginListQuerySerializer,
    PluginListResponseSerializer,
    PluginTagListResponseSerializer,
    PluginTagsListQuerySerializer,
)

logger = logging.getLogger(PLUGIN_LOGGER)

SYSTEM_TENANT_ID = "system"


def _resolve_plugin_tenant_id(request):
    """根据前端传来的 app_tenant_mode 推断插件所在的租户 ID"""
    app_tenant_mode = request.validated_data.get("app_tenant_mode") or request.query_params.get("app_tenant_mode")
    if app_tenant_mode == "global":
        return SYSTEM_TENANT_ID
    return getattr(request.user, "tenant_id", SYSTEM_TENANT_ID)


def _fetch_all_plugins_for_tenant(tenant_id, search_term=None, distributor_code_name=None, **extra_kwargs):
    """从指定租户拉取全量已部署插件（自动翻页）"""
    all_plugins = []
    offset = 0
    batch_size = 100
    while True:
        result = PluginServiceApiClient.get_plugin_detail_list(
            search_term=search_term,
            tenant_id=tenant_id,
            limit=batch_size,
            offset=offset,
            order_by="name",
            include_addresses=0,
            distributor_code_name=distributor_code_name,
            **extra_kwargs,
        )
        if not result["result"]:
            return result
        plugins = result["data"]["plugins"]
        all_plugins.extend(plugins)
        if not plugins or len(plugins) < batch_size or result["data"]["count"] <= offset + batch_size:
            break
        offset += batch_size
    return {"result": True, "data": {"plugins": all_plugins}}


@swagger_auto_schema(
    method="GET",
    operation_summary="获取插件服务列表信息",
    query_serializer=PluginListQuerySerializer,
    responses={200: PluginListResponseSerializer},
)
@api_view(["GET"])
@validate_params(PluginListQuerySerializer)
def get_plugin_list(request: Request):
    """获取插件服务列表信息"""
    search_term = request.validated_data.get("search_term")
    limit = request.validated_data.get("limit")
    offset = request.validated_data.get("offset")
    tag_id = request.validated_data.get("tag_id")
    tenant_id = getattr(request.user, "tenant_id", SYSTEM_TENANT_ID)
    extra_kwargs = {}
    if tag_id is not None:
        extra_kwargs["tag_id"] = tag_id
    result = PluginServiceApiClient.get_plugin_list(
        search_term=search_term,
        limit=limit,
        offset=offset,
        distributor_code_name=PLUGIN_DISTRIBUTOR_NAME,
        tenant_id=tenant_id,
        **extra_kwargs,
    )
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET",
    operation_summary="获取插件Tag列表信息",
    query_serializer=PluginTagsListQuerySerializer,
    responses={200: PluginTagListResponseSerializer},
)
@api_view(["GET"])
def get_plugin_tags(request: Request):
    """获取插件tag列表信息"""
    tenant_id = getattr(request.user, "tenant_id", SYSTEM_TENANT_ID)
    result = PluginServiceApiClient.get_plugin_tags_list(tenant_id=tenant_id)
    if request.query_params.get("with_unknown_tag") and result.get("result") and isinstance(result["data"], list):
        result["data"].append({"code_name": "OTHER", "name": "未分类", "id": -1})
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET",
    operation_summary="获取插件服务列表及详情信息",
    query_serializer=PluginDetailListQuerySerializer,
    responses={200: PluginDetailListResponseSerializer},
)
@api_view(["GET"])
@validate_params(PluginDetailListQuerySerializer)
def get_plugin_detail_list(request: Request):
    """获取插件服务列表及详情信息

    多租户模式下，需要同时获取 system 租户的全租户插件和用户所在租户的单租户插件，合并后返回。
    非多租户模式下，行为与原来一致（不传 X-Bk-Tenant-Id）。
    """
    search_term = request.validated_data.get("search_term")
    exclude_not_deployed = request.validated_data.get("exclude_not_deployed")
    tag_id = request.validated_data.get("tag_id")
    extra_kwargs = {}
    if tag_id is not None:
        extra_kwargs["tag_id"] = tag_id

    enable_multi_tenant = getattr(settings, "ENABLE_MULTI_TENANT_MODE", False)
    user_tenant_id = getattr(request.user, "tenant_id", None)

    if enable_multi_tenant and user_tenant_id:
        return _get_plugin_detail_list_multi_tenant(
            search_term=search_term,
            exclude_not_deployed=exclude_not_deployed,
            user_tenant_id=user_tenant_id,
            **extra_kwargs,
        )

    return _get_plugin_detail_list_single_tenant(request, search_term, exclude_not_deployed, **extra_kwargs)


def _get_plugin_detail_list_multi_tenant(search_term, exclude_not_deployed, user_tenant_id, **extra_kwargs):
    """多租户模式：从 system 租户和用户租户各拉一次，合并返回全量列表"""
    common_kwargs = dict(search_term=search_term, distributor_code_name=PLUGIN_DISTRIBUTOR_NAME, **extra_kwargs)

    system_result = _fetch_all_plugins_for_tenant(tenant_id=SYSTEM_TENANT_ID, **common_kwargs)
    if not system_result["result"]:
        return JsonResponse(system_result)

    tenant_result = _fetch_all_plugins_for_tenant(tenant_id=user_tenant_id, **common_kwargs)
    if not tenant_result["result"]:
        return JsonResponse(tenant_result)

    all_plugins = system_result["data"]["plugins"] + tenant_result["data"]["plugins"]

    # 按 plugin code 去重（理论上不会重复，保险起见）
    seen_codes = set()
    unique_plugins = []
    for plugin in all_plugins:
        code = plugin.get("plugin", {}).get("code", "")
        if code not in seen_codes:
            seen_codes.add(code)
            unique_plugins.append(plugin)

    if exclude_not_deployed:
        unique_plugins = [
            p for p in unique_plugins if p.get("deployed_statuses", {}).get(env.APIGW_ENVIRONMENT, {}).get("deployed")
        ]

    return JsonResponse(
        {
            "result": True,
            "message": None,
            "data": {
                "next_offset": -1,
                "plugins": unique_plugins,
                "return_plugin_count": len(unique_plugins),
            },
        }
    )


def _get_plugin_detail_list_single_tenant(request, search_term, exclude_not_deployed, **extra_kwargs):
    """非多租户模式：保持原有分页逻辑"""
    fetch_all = request.validated_data.get("fetch_all")
    limit = request.validated_data.get("limit")
    offset = request.validated_data.get("offset")

    if not fetch_all and exclude_not_deployed:
        plugins = []
        cur_offset = offset
        cur_limit = limit * 2
        while True:
            result = PluginServiceApiClient.get_plugin_detail_list(
                search_term=search_term,
                limit=cur_limit,
                offset=cur_offset,
                order_by="name",
                include_addresses=0,
                distributor_code_name=PLUGIN_DISTRIBUTOR_NAME,
                **extra_kwargs,
            )
            if not result["result"]:
                return JsonResponse(result)
            cur_plugins = result["data"]["plugins"]
            plugins.extend(
                [
                    (idx + cur_offset, plugin)
                    for idx, plugin in enumerate(cur_plugins)
                    if plugin["deployed_statuses"][env.APIGW_ENVIRONMENT]["deployed"]
                ]
            )
            cur_offset = cur_offset + cur_limit
            if result["data"]["count"] <= cur_offset or len(plugins) >= limit:
                break
        plugins = plugins[:limit]
        next_offset = plugins[-1][0] + 1 if len(plugins) > 0 else cur_offset
        return JsonResponse(
            {
                "result": True,
                "message": None,
                "data": {
                    "next_offset": next_offset,
                    "plugins": [plugin[1] for plugin in plugins],
                    "return_plugin_count": len(plugins),
                },
            }
        )

    if not fetch_all:
        extra_kwargs.update({"limit": limit, "offset": offset})
    result = PluginServiceApiClient.get_plugin_detail_list(
        search_term=search_term,
        order_by="name",
        include_addresses=0,
        distributor_code_name=PLUGIN_DISTRIBUTOR_NAME,
        **extra_kwargs,
    )
    if not result["result"]:
        return JsonResponse(result)

    plugins = (
        [
            plugin
            for plugin in result["data"]["plugins"]
            if plugin["deployed_statuses"][env.APIGW_ENVIRONMENT]["deployed"]
        ]
        if exclude_not_deployed
        else result["data"]["plugins"]
    )

    return JsonResponse(
        {
            "data": {
                "next_offset": -1 if fetch_all else limit + offset,
                "plugins": plugins,
                "return_plugin_count": len(plugins),
            },
            "result": True,
            "message": None,
        }
    )


@swagger_auto_schema(
    method="GET",
    operation_summary="获取插件服务详情",
    query_serializer=PluginDetailQuerySerializer,
    responses={200: DetailResponseSerializer},
)
@api_view(["GET"])
@validate_params(PluginDetailQuerySerializer)
@inject_plugin_client
def get_plugin_detail(request: Request):
    """获取插件服务详情"""
    plugin_version = request.validated_data.get("plugin_version")
    with_app_detail = request.validated_data.get("with_app_detail")
    plugin_detail = request.plugin_client.get_detail(plugin_version)
    if not plugin_detail["result"]:
        return JsonResponse(plugin_detail)
    if with_app_detail:
        tenant_id = _resolve_plugin_tenant_id(request)
        app_detail = PluginServiceApiClient.get_plugin_app_detail(
            request.validated_data.get("plugin_code"), tenant_id=tenant_id
        )
        if not app_detail["result"]:
            return JsonResponse(app_detail)
        plugin_detail["data"]["app"] = app_detail["data"]
    return JsonResponse(plugin_detail)


@swagger_auto_schema(
    method="GET",
    operation_summary="获取插件服务元信息",
    query_serializer=PluginCodeQuerySerializer,
    responses={200: MetaResponseSerializer},
)
@api_view(["GET"])
@validate_params(PluginCodeQuerySerializer)
@inject_plugin_client
def get_meta(request: Request):
    """获取插件服务元信息"""
    return JsonResponse(request.plugin_client.get_meta())


@swagger_auto_schema(
    method="POST",
    operation_summary="获取插件服务执行日志",
    request_body=LogQuerySerializer,
    responses={200: LogResponseSerializer},
)
@api_view(["POST"])
@validate_params(LogQuerySerializer)
def get_logs(request: Request):
    """获取插件服务执行日志"""
    trace_id = request.validated_data.get("trace_id")
    scroll_id = request.validated_data.get("scroll_id")
    plugin_code = request.validated_data.get("plugin_code")
    tenant_id = _resolve_plugin_tenant_id(request)
    result = PluginServiceApiClient.get_plugin_logs(plugin_code, trace_id, scroll_id, tenant_id=tenant_id)
    if result["result"]:
        logs = [
            f'[{log["ts"]}]{log["detail"]["json.levelname"]}-{log["detail"]["json.funcName"]}: '
            f'{log["detail"]["json.message"]}'
            for log in result["data"]["logs"]
        ]
        result["data"]["logs"] = "\n".join(logs)
    return JsonResponse(result)


@swagger_auto_schema(
    method="GET",
    operation_summary="获取插件服务App详情",
    query_serializer=PluginCodeQuerySerializer,
    responses={200: PluginAppDetailResponseSerializer},
)
@api_view(["GET"])
@validate_params(PluginCodeQuerySerializer)
def get_plugin_app_detail(request: Request):
    """获取插件服务App详情"""
    tenant_id = _resolve_plugin_tenant_id(request)
    result = PluginServiceApiClient.get_plugin_app_detail(
        request.validated_data.get("plugin_code"), tenant_id=tenant_id
    )
    return JsonResponse(result)


@swagger_auto_schema(
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"], operation_summary="获取插件服务提供的数据接口数据", responses={200: "插件数据接口返回"}
)
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def get_plugin_api_data(request: Request, plugin_code: str, data_api_path: str):
    """获取插件服务提供的数据接口数据"""
    app_tenant_mode = request.query_params.get("app_tenant_mode") or request.data.get("app_tenant_mode")
    if app_tenant_mode == "global":
        tenant_id = SYSTEM_TENANT_ID
    else:
        tenant_id = getattr(request.user, "tenant_id", SYSTEM_TENANT_ID)
    try:
        client = PluginServiceApiClient(plugin_code, tenant_id=tenant_id)
    except PluginServiceException as e:
        message = f"[get_plugin_api_data] error: {e}"
        logger.error(message)
        return JsonResponse({"message": message, "result": False, "data": None})
    # 注入插件特定前缀HEADER
    http_headers = dict(
        [(key[5:].replace("_", "-"), value) for key, value in request.META.items() if key.startswith("HTTP_BK_PLUGIN_")]
    )
    params = {
        "method": request.method,
        "url": "/" + data_api_path,
        "username": request.user.username,
        "data": request.data,
    }
    # 对于get请求带参数的情况，直接将参数拼接到url中
    if request.query_params:
        params["url"] = params["url"].rstrip("/") + "/?" + request.query_params.urlencode()

    token = request.COOKIES.get(env.APIGW_USER_AUTH_KEY_NAME)
    inject_authorization = {env.APIGW_USER_AUTH_KEY_NAME: token} if token else {}
    result = client.dispatch_plugin_api_request(
        params, inject_headers=http_headers, inject_authorization=inject_authorization
    )
    # 如果请求成功，只返回接口原始data数据
    result = result["data"] if result.get("result") else result
    return Response(result)

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
import copy
import logging

from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from gcloud.utils import crypto

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
    extra_kwargs = {}
    if tag_id is not None:
        extra_kwargs["tag_id"] = tag_id
    result = PluginServiceApiClient.get_plugin_list(
        search_term=search_term,
        limit=limit,
        offset=offset,
        distributor_code_name=PLUGIN_DISTRIBUTOR_NAME,
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
    result = PluginServiceApiClient.get_plugin_tags_list()
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
    """获取插件服务列表及详情信息"""
    search_term = request.validated_data.get("search_term")
    fetch_all = request.validated_data.get("fetch_all")
    limit = request.validated_data.get("limit")
    offset = request.validated_data.get("offset")
    exclude_not_deployed = request.validated_data.get("exclude_not_deployed")
    tag_id = request.validated_data.get("tag_id")
    extra_kwargs = {}
    if tag_id is not None:
        extra_kwargs["tag_id"] = tag_id

    # 滚动加载获取已部署对应环境插件
    if not fetch_all and exclude_not_deployed:
        plugins = []
        cur_offset = offset
        # 考虑到会有一些未部署到对应环境的情况，这里适当放大limit，减少请求次数
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

    response = {
        "data": {
            "next_offset": -1 if fetch_all else limit + offset,
            "plugins": plugins,
            "return_plugin_count": len(plugins),
        },
        "result": True,
        "message": None,
    }
    return JsonResponse(response)


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
        app_detail = PluginServiceApiClient.get_plugin_app_detail(request.validated_data.get("plugin_code"))
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
    method="GET",
    operation_summary="获取插件服务App详情",
    query_serializer=PluginCodeQuerySerializer,
    responses={200: PluginAppDetailResponseSerializer},
)
@api_view(["GET"])
@validate_params(PluginCodeQuerySerializer)
def get_plugin_app_detail(request: Request):
    """获取插件服务App详情"""
    result = PluginServiceApiClient.get_plugin_app_detail(request.validated_data.get("plugin_code"))
    return JsonResponse(result)


@swagger_auto_schema(
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"], operation_summary="获取插件服务提供的数据接口数据", responses={200: "插件数据接口返回"}
)
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def get_plugin_api_data(request: Request, plugin_code: str, data_api_path: str):
    """获取插件服务提供的数据接口数据"""
    try:
        client = PluginServiceApiClient(plugin_code)
    except PluginServiceException as e:
        message = f"[get_plugin_api_data] error: {e}"
        logger.error(message)
        return JsonResponse({"message": message, "result": False, "data": None})

    # 解密 request.data 中的密码字段
    try:
        data = _decrypt_request_data(request.data, plugin_code)
    except PluginServiceException as e:
        message = f"[get_plugin_api_data] decrypt error: {e}"
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
        "data": data,
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


def _decrypt_request_data(data, plugin_code: str):
    """
    解密请求数据中的密码字段，这个路由只会在用户输入的时候进行触发，这种密码变量设定只有顶层结构单独的密码变量才触发，嵌套的情况暂不处理

    遍历 data 中的每个字段，检查是否为 password_value 类型，
    如果是则尝试解密，解密失败则不处理只记录日志。

    :param data: 请求数据，格式为 dict
    :param plugin_code: 插件代码，用于日志记录
    :return: 解密后的数据（新字典，不修改原始数据）
    """
    if not isinstance(data, dict):
        return data

    # 先检测是否需要解密
    need_password_handle = any(
        isinstance(v, dict) and v.get("type") == "password_value"
        for v in data.values()
    )

    if not need_password_handle:
        return data

    # 创建数据的深拷贝，避免修改原始数据
    decrypted_data = copy.deepcopy(data)

    for key, value in decrypted_data.items():
        # 检查是否为密码结构体，暂不考虑深层嵌套情况
        if isinstance(value, dict) and value.get("type") == "password_value":
            cipher = value.get("value")
            if not cipher or not isinstance(cipher, str):
                logger.warning(
                    "[_decrypt_request_data] plugin_code: %s, key: %s, password_value is empty or not a string",
                    plugin_code,
                    key,
                )
                continue

            try:
                plain = crypto.decrypt(cipher)
                decrypted_data[key] = plain
                logger.debug(
                    "[_decrypt_request_data] plugin_code: %s, key: %s, decrypt success",
                    plugin_code,
                    key,
                )
            except Exception as e:
                # 解密失败，抛出异常，由调用方处理
                error_msg = f"decrypt password_value failed for key '{key}': {e}"
                logger.error(
                    "[_decrypt_request_data] plugin_code: %s, key: %s, decrypt failed: %s",
                    plugin_code,
                    key,
                    e,
                )
                raise PluginServiceException(error_msg)

    return decrypted_data

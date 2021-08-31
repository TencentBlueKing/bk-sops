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
import functools
import json
import logging
import os

import requests

from . import env
from .conf import PLUGIN_CLIENT_LOGGER
from .exceptions import PluginServiceNotDeploy, PluginServiceNetworkError

logger = logging.getLogger(PLUGIN_CLIENT_LOGGER)


def data_parser(func):
    """用于解析标准格式接口返回数据"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            message = f"plugin client request {func.__name__} error: {e}, with params: {args} and kwargs: {kwargs}."
            return False, {"message": message}
        if not result.get("result"):
            logger.error(f"{func.__name__} request error: {result.get('message')}")
            data = {"message": result.get("message")}
            if "trace_id" in result:
                data["trace_id"] = result["trace_id"]
            return False, data
        else:
            data = result.get("data")
            if "trace_id" in result and isinstance(data, dict):
                data["trace_id"] = result["trace_id"]
            return True, data

    return wrapper


def json_response_decoder(func):
    """用于处理json格式接口返回"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code != 200:
            message = (
                f"{func.__name__} gets error status code [{response.status_code}], "
                f"request with params: {args} and kwargs: {kwargs}. "
            )
            logger.error(message + f"response content: {response.content}")
            return {"result": False, "data": None, "message": message}
        return response.json()

    return wrapper


class PluginServiceApiClient:
    def __init__(self, plugin_code, plugin_host=None):
        self.plugin_code = plugin_code
        if not plugin_host:
            result = PluginServiceApiClient.get_plugin_app_detail(plugin_code)
            self.plugin_host = os.path.join(result["data"]["url"], "bk_plugin/")

    @staticmethod
    @json_response_decoder
    def get_paas_plugin_info(plugin_code=None, environment=None, limit=100, offset=0, search_term=None):
        """可支持请求获取插件服务列表或插件详情"""
        url = os.path.join(
            f"{env.APIGW_NETWORK_PROTOCAL}://paasv3.{env.APIGW_URL_SUFFIX}",
            environment or env.APIGW_ENVIRONMENT,
            "system/bk_plugins",
            plugin_code if plugin_code else "",
        )
        params = {"private_token": env.PAASV3_APIGW_API_TOKEN}
        if not plugin_code:
            # list接口相关参数
            params.update({"limit": limit, "offset": offset, "has_deployed": True})
            if search_term:
                params.update({"search_term": search_term})
        return requests.get(url, params=params)

    @data_parser
    @json_response_decoder
    def invoke(self, version, data):
        url = os.path.join(
            f"{env.APIGW_NETWORK_PROTOCAL}://{self.plugin_code}.{env.APIGW_URL_SUFFIX}",
            env.APIGW_ENVIRONMENT,
            "invoke",
            version,
        )
        headers = {
            "X-Bkapi-Authorization": json.dumps(
                {"bk_app_code": env.PLUGIN_SERVICE_APIGW_APP_CODE, "bk_app_secret": env.PLUGIN_SERVICE_APIGW_APP_SECRET}
            ),
            "Content-Type": "application/json",
        }
        return requests.post(url, data=json.dumps(data), headers=headers)

    @json_response_decoder
    def get_logs(self, trace_id):
        url = os.path.join(self.plugin_host, "logs", trace_id)
        return requests.get(url)

    @json_response_decoder
    def get_meta(self):
        url = os.path.join(self.plugin_host, "meta")
        return requests.get(url)

    @json_response_decoder
    def get_detail(self, version):
        url = os.path.join(self.plugin_host, "detail", version)
        return requests.get(url)

    @data_parser
    @json_response_decoder
    def get_schedule(self, trace_id):
        url = os.path.join(self.plugin_host, "schedule", trace_id)
        return requests.get(url)

    @staticmethod
    def get_plugin_list(search_term=None, limit=100, offset=0):
        result = PluginServiceApiClient.get_paas_plugin_info(
            search_term=search_term, environment="prod", limit=limit, offset=offset
        )
        if result.get("result") is False:
            return result

        plugins = [
            {
                "code": plugin["code"],
                "name": plugin["name"],
                "logo_url": plugin["logo_url"],
                "creator": plugin["creator"],
            }
            for plugin in result["results"]
        ]
        count = len(plugins)

        return {"result": True, "message": None, "data": {"count": count, "plugins": plugins}}

    @staticmethod
    def get_plugin_app_detail(plugin_code):
        result = PluginServiceApiClient.get_paas_plugin_info(plugin_code, environment="prod")

        if result.get("result") is False:
            raise PluginServiceNetworkError(f"Plugin Service {plugin_code} network error: {result.get('message')}")

        info = result["deployed_statuses"][env.APIGW_ENVIRONMENT]
        if not info["deployed"]:
            raise PluginServiceNotDeploy(f"Plugin Service {plugin_code} does not deployed.")
        plugin = result["plugin"]

        return {
            "result": True,
            "message": None,
            "data": {"url": info["url"], "name": plugin["name"], "code": plugin["code"], "updated": plugin["updated"]},
        }

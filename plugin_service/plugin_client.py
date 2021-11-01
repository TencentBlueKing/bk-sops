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
import json
import logging
import os

import requests

from . import env
from .conf import PLUGIN_CLIENT_LOGGER
from .client_decorators import data_parser, json_response_decoder, check_use_plugin_service
from .exceptions import PluginServiceNotUse, PluginServiceException

logger = logging.getLogger(PLUGIN_CLIENT_LOGGER)


class PluginServiceApiClient:
    def __init__(self, plugin_code, plugin_host=None):
        if not env.USE_PLUGIN_SERVICE == "1":
            raise PluginServiceNotUse("插件服务未启用，请联系管理员进行配置")
        self.plugin_code = plugin_code
        if not plugin_host:
            # 如果请求报错，会抛出PluginServiceException类型异常，需要调用方进行捕获处理
            result = PluginServiceApiClient.get_plugin_app_detail(plugin_code)
            if not result["result"]:
                raise PluginServiceException(result["message"])
            self.plugin_host = os.path.join(result["data"]["url"], "bk_plugin/")

    @data_parser
    @json_response_decoder
    def invoke(self, version, data):
        url, headers = self._prepare_apigw_api_request(path_params=["invoke", version])
        return requests.post(url, data=json.dumps(data), headers=headers)

    @json_response_decoder
    def dispatch_plugin_api_request(self, request_params):
        url, headers = self._prepare_apigw_api_request(path_params=["plugin_api_dispatch"])
        return requests.post(url, data=json.dumps(request_params), headers=headers)

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
    @check_use_plugin_service
    def get_plugin_logs(plugin_code, trace_id, scroll_id=None):
        result = PluginServiceApiClient.get_paas_logs(plugin_code, trace_id, scroll_id, environment="prod")
        if result.get("result") is False:
            return result
        return {"result": True, "message": None, "data": result}

    @staticmethod
    def get_plugin_list(search_term=None, limit=100, offset=0):
        # 如果不启动插件服务，直接返回空列表
        if not env.USE_PLUGIN_SERVICE == "1":
            return {"result": True, "message": "插件服务未启用，请联系管理员进行配置", "data": {"count": 0, "plugins": []}}
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
        count = result["count"]

        return {"result": True, "message": None, "data": {"count": count, "plugins": plugins}}

    @staticmethod
    @check_use_plugin_service
    def get_plugin_app_detail(plugin_code):
        result = PluginServiceApiClient.get_paas_plugin_info(plugin_code, environment="prod")

        if result.get("result") is False:
            return {
                "result": False,
                "data": None,
                "message": f"Plugin Service {plugin_code} network error: {result.get('message')}",
            }

        info = result["deployed_statuses"][env.APIGW_ENVIRONMENT]
        if not info["deployed"]:
            return {"result": False, "data": None, "message": f"Plugin Service {plugin_code} does not deployed."}
        plugin = result["plugin"]

        default_host = ""
        hosts = []
        DEFAULT_HOST_TYPE = 2
        for address in info["addresses"]:
            if address["type"] == DEFAULT_HOST_TYPE:
                default_host = address["address"]
            hosts.append(address["address"])
        return {
            "result": True,
            "message": None,
            "data": {
                "url": default_host,
                "urls": hosts,
                "name": plugin["name"],
                "code": plugin["code"],
                "updated": plugin["updated"],
            },
        }

    @staticmethod
    @json_response_decoder
    def get_paas_plugin_info(plugin_code=None, environment=None, limit=100, offset=0, search_term=None):
        """可支持通过PaaS平台请求获取插件服务列表或插件详情"""
        url, params = PluginServiceApiClient._prepare_paas_api_request(
            path_params=["system/bk_plugins", plugin_code if plugin_code else ""], environment=environment
        )
        if not plugin_code:
            # list接口相关参数
            params.update({"limit": limit, "offset": offset, "has_deployed": True})
            if search_term:
                params.update({"search_term": search_term})
        return requests.get(url, params=params)

    @staticmethod
    @json_response_decoder
    def get_paas_logs(plugin_code, trace_id, scroll_id=None, environment=None):
        """通过PaaS平台查询插件服务日志"""
        url, params = PluginServiceApiClient._prepare_paas_api_request(
            path_params=["system/bk_plugins", plugin_code, "logs"], environment=environment
        )
        params.update({"trace_id": trace_id})
        if scroll_id:
            params.update({"scroll_id": scroll_id})
        return requests.get(url, params=params)

    def _prepare_apigw_api_request(self, path_params: list):
        """插件服务APIGW接口请求信息准备"""
        url = os.path.join(
            f"{env.APIGW_NETWORK_PROTOCAL}://{self.plugin_code}.{env.APIGW_URL_SUFFIX}",
            env.APIGW_ENVIRONMENT,
            *path_params,
        )
        headers = {
            "X-Bkapi-Authorization": json.dumps(
                {"bk_app_code": env.PLUGIN_SERVICE_APIGW_APP_CODE, "bk_app_secret": env.PLUGIN_SERVICE_APIGW_APP_SECRET}
            ),
            "Content-Type": "application/json",
        }
        return url, headers

    @staticmethod
    def _prepare_paas_api_request(path_params: list, environment=None):
        """PaaS平台服务接口请求信息准备"""
        url = os.path.join(
            f"{env.APIGW_NETWORK_PROTOCAL}://paasv3.{env.APIGW_URL_SUFFIX}",
            environment or env.APIGW_ENVIRONMENT,
            *path_params,
        )
        params = {"private_token": env.PAASV3_APIGW_API_TOKEN}
        return url, params

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
import json
import logging
import os

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile

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

        # 如果请求报错，会抛出PluginServiceException类型异常，需要调用方进行捕获处理
        result = PluginServiceApiClient.get_plugin_app_detail(plugin_code)
        if not result["result"]:
            raise PluginServiceException(result["message"])
        self.plugin_host = plugin_host or os.path.join(result["data"]["url"], "bk_plugin/")
        self.plugin_apigw_name = result["data"]["apigw_name"] or plugin_code

    @data_parser
    @json_response_decoder
    def invoke(self, version, data):
        url, headers = self._prepare_apigw_api_request(path_params=["invoke", version])

        return requests.post(url, data=json.dumps(data), headers=headers)

    @json_response_decoder
    def dispatch_plugin_api_request(self, request_params, inject_headers=None, inject_authorization: dict = None):
        url, headers = self._prepare_apigw_api_request(
            path_params=["plugin_api_dispatch"], inject_authorization=inject_authorization
        )
        if inject_headers:
            headers.update(inject_headers)
        # 上传文件的情况
        if any([isinstance(data, InMemoryUploadedFile) for data in request_params["data"].values()]):
            headers.pop("Content-Type")
            files = dict(
                [
                    (key, (value.name, value.file.getvalue()))
                    for key, value in request_params["data"].items()
                    if isinstance(value, InMemoryUploadedFile)
                ]
            )
            request_params.pop("data")
            return PluginServiceApiClient._request_api_and_error_retry(
                url, method="post", data=request_params, headers=headers, files=files
            )
        return PluginServiceApiClient._request_api_and_error_retry(
            url, method="post", data=json.dumps(request_params), headers=headers
        )

    @json_response_decoder
    def get_meta(self):
        url = os.path.join(self.plugin_host, "meta")

        return PluginServiceApiClient._request_api_and_error_retry(url, method="get")

    @json_response_decoder
    def get_detail(self, version):
        url = os.path.join(self.plugin_host, "detail", version)

        return PluginServiceApiClient._request_api_and_error_retry(url, method="get")

    @data_parser
    @json_response_decoder
    def get_schedule(self, trace_id):
        url = os.path.join(self.plugin_host, "schedule", trace_id)

        return PluginServiceApiClient._request_api_and_error_retry(url, method="get")

    @staticmethod
    @check_use_plugin_service
    def get_plugin_logs(plugin_code, trace_id, scroll_id=None):
        result = PluginServiceApiClient.get_paas_logs(plugin_code, trace_id, scroll_id, environment="prod")
        if result.get("result") is False:
            return result
        return {"result": True, "message": None, "data": result}

    @staticmethod
    def get_plugin_list(search_term=None, limit=100, offset=0, distributor_code_name=None):
        """获取插件服务列表"""
        # 如果不启动插件服务，直接返回空列表
        if not env.USE_PLUGIN_SERVICE == "1":
            return {"result": True, "message": "插件服务未启用，请联系管理员进行配置", "data": {"count": 0, "plugins": []}}
        result = PluginServiceApiClient.get_paas_plugin_info(
            search_term=search_term,
            environment="prod",
            limit=limit,
            offset=offset,
            distributor_code_name=distributor_code_name,
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
    def get_plugin_detail_list(search_term=None, limit=100, offset=0, **kwargs):
        """获取插件服务列表及详情信息"""
        # 如果不启动插件服务，直接返回空列表
        if not env.USE_PLUGIN_SERVICE == "1":
            return {"result": True, "message": "插件服务未启用，请联系管理员进行配置", "data": {"count": 0, "plugins": []}}
        result = PluginServiceApiClient.batch_get_paas_plugin_detailed_info(
            search_term=search_term, environment="prod", limit=limit, offset=offset, **kwargs
        )
        if result.get("result") is False:
            return result
        return {"result": True, "message": None, "data": {"count": result["count"], "plugins": result["results"]}}

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
        profile = result["profile"]

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
                "apigw_name": profile["api_gw_name"],
            },
        }

    @staticmethod
    @json_response_decoder
    def get_paas_plugin_info(
        plugin_code=None, environment=None, limit=100, offset=0, search_term=None, distributor_code_name=None
    ):
        """可支持通过PaaS平台请求获取插件服务列表或插件详情"""
        url, params = PluginServiceApiClient._prepare_paas_api_request(
            path_params=["system/bk_plugins", plugin_code if plugin_code else ""], environment=environment
        )
        if not plugin_code:
            # list接口相关参数
            params.update({"limit": limit, "offset": offset, "has_deployed": True})
            if search_term:
                params.update({"search_term": search_term})
            if distributor_code_name:
                params.update({"distributor_code_name": distributor_code_name})
        return PluginServiceApiClient._request_api_and_error_retry(url, method="get", params=params)

    @staticmethod
    @json_response_decoder
    def batch_get_paas_plugin_detailed_info(
        environment=None, limit=100, offset=0, search_term=None, distributor_code_name=None, **kwargs
    ):
        """通过PaaS平台批量请求插件服务列表及对应详情"""
        url, params = PluginServiceApiClient._prepare_paas_api_request(
            path_params=["system/bk_plugins/batch/detailed"], environment=environment
        )
        params.update({"limit": limit, "offset": offset, "has_deployed": True, **kwargs})
        if search_term:
            params.update({"search_term": search_term})
        if distributor_code_name:
            params.update({"distributor_code_name": distributor_code_name})
        return PluginServiceApiClient._request_api_and_error_retry(url, method="get", params=params)

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

        return PluginServiceApiClient._request_api_and_error_retry(url, method="get", params=params)

    def _prepare_apigw_api_request(self, path_params: list, inject_authorization: dict = None):
        """插件服务APIGW接口请求信息准备"""
        url = os.path.join(
            f"{env.APIGW_NETWORK_PROTOCAL}://{self.plugin_apigw_name}.{env.APIGW_URL_SUFFIX}",
            env.APIGW_ENVIRONMENT,
            *path_params,
        )
        authorization_info = {
            "bk_app_code": env.PLUGIN_SERVICE_APIGW_APP_CODE,
            "bk_app_secret": env.PLUGIN_SERVICE_APIGW_APP_SECRET,
        }

        if inject_authorization:
            authorization_info.update(inject_authorization)

        headers = {
            "X-Bkapi-Authorization": json.dumps(authorization_info),
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

    @staticmethod
    def _request_api_and_error_retry(url, method, **kwargs):
        """请求API接口,失败进行重试"""
        for invoke_num in range(1, env.BKAPP_INVOKE_PAAS_RETRY_NUM + 1):
            try:
                logger.info(
                    "[PluginServiceApiClient] request url {} with method {} and kwargs {}".format(url, method, kwargs)
                )
                result = getattr(requests, method)(url, **kwargs)
                result.raise_for_status()
                break
            except Exception as e:
                message = "request api error,invoke_num:{},{} {},kwargs:{},error:{} ".format(
                    invoke_num, method, url, kwargs, str(e)
                )
                logger.error(message.replace(env.PAASV3_APIGW_API_TOKEN, "******"))

        return result

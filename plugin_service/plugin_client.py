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

logger = logging.getLogger(PLUGIN_CLIENT_LOGGER)


def response_parser(func):
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


class PluginServiceApiClient:
    def __init__(self, plugin_code, plugin_host=None):
        self.plugin_code = plugin_code
        if not plugin_host:
            # TODO: PaaS根据plugin_code获取host
            self.plugin_host = env.TEST_PLUGIN_HOST.rstrip("/")

    @response_parser
    def invoke(self, version, data):
        url = os.path.join(
            f"http://{self.plugin_code}.{env.APIGW_URL_SUFFIX}", env.APIGW_ENVIRONMENT, "invoke", version
        )
        headers = {
            "X-Bkapi-Authorization": json.dumps(
                {"bk_app_code": env.PLUGIN_SERVICE_APIGW_APP_CODE, "bk_app_secret": env.PLUGIN_SERVICE_APIGW_APP_SECRET}
            ),
            "Content-Type": "application/json",
        }
        return requests.post(url, data=json.dumps(data), headers=headers).json()

    def get_logs(self, trace_id):
        url = os.path.join(self.plugin_host, "logs", trace_id)
        return requests.get(url).json()

    def get_meta(self):
        url = os.path.join(self.plugin_host, "meta")
        return requests.get(url).json()

    def get_detail(self, version):
        url = os.path.join(self.plugin_host, "detail", version)
        return requests.get(url).json()

    @response_parser
    def get_schedule(self, trace_id):
        url = os.path.join(self.plugin_host, "schedule", trace_id)
        return requests.get(url).json()

    @staticmethod
    def get_plugin_list():
        # TODO: delete mock data
        return {"result": True, "message": None, "data": ["bk-plugin-demo"]}

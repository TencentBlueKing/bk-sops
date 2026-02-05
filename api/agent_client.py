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

logger = logging.getLogger("root")


class AgentClient:
    """
    智能体 API 客户端

    用于与智能体服务进行通信，发送请求并获取响应
    """

    # 环境变量名称
    ENV_AGENT_URL = "AGENT_PROCESS_BUILD_URL"
    ENV_AGENT_APP_CODE = "AGENT_PROCESS_BUILD_CODE"
    ENV_AGENT_APP_TOKEN = "AGENT_PROCESS_BUILD_TOKEN"

    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = 300

    def __init__(self, username: str = "admin"):
        """
        初始化客户端

        :param username: 用户名
        """
        self.username = username
        self._agent_url = None
        self._agent_app_code = None
        self._agent_app_token = None

    def _load_config(self):
        """从环境变量加载配置"""
        self._agent_url = os.environ.get(self.ENV_AGENT_URL)
        self._agent_app_code = os.environ.get(self.ENV_AGENT_APP_CODE)
        self._agent_app_token = os.environ.get(self.ENV_AGENT_APP_TOKEN)

        if not self._agent_url or not self._agent_app_code:
            raise ValueError("智能体 API 配置缺失，请检查环境变量 {} 和 {}".format(self.ENV_AGENT_URL, self.ENV_AGENT_APP_CODE))

    def _build_headers(self) -> dict:
        """
        构建请求头

        :return: 请求头字典
        """
        return {
            "Content-Type": "application/json",
            "X-Bkapi-Authorization": json.dumps(
                {"bk_app_code": self._agent_app_code, "bk_app_secret": self._agent_app_token or ""}
            ),
            "X-BKAIDEV-USER": self.username,
        }

    def call(self, input_content: str, stream: bool = False, timeout: int = None) -> dict:
        """
        调用智能体 API

        :param input_content: 输入内容（prompt）
        :param stream: 是否使用流式响应
        :param timeout: 超时时间（秒），默认 300 秒
        :return: API 响应结果
        """
        # 加载配置
        self._load_config()

        # 构建请求体
        request_body = {"input": input_content, "execute_kwargs": {"stream": stream}}

        # 发送请求
        response = requests.post(
            self._agent_url, headers=self._build_headers(), json=request_body, timeout=timeout or self.DEFAULT_TIMEOUT
        )

        logger.info("AgentClient.call - Response status: {}".format(response.status_code))
        logger.info("AgentClient.call - Response body: {}".format(response.text[:1000] if response.text else ""))

        response.raise_for_status()
        return response.json()

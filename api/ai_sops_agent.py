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

import enum
import json
import logging

import requests
from django.conf import settings

import env

logger = logging.getLogger("root")


PATH_CONFIG_MAP = {"plugin": f"invoke/{env.AGENT_VERSION}assistant", "user": "bk_plugin/openapi/agent/chat_completion"}


class AgentRequestType(enum.Enum):
    PLUGIN = "plugin"
    USER = "user"


class AgentRequestData:
    """根据请求类型构建不同的请求体"""

    def __init__(self, request_type: AgentRequestType):
        self.request_type = request_type

    def build(self, user_input: str, stream: bool = False) -> dict:
        if self.request_type == AgentRequestType.USER:
            return {
                "input": user_input,
                "execute_kwargs": {"stream": stream},
            }
        return {
            "inputs": {
                "command": "",
                "input": user_input,
                "chat_history": [],
            },
            "context": {
                "executor": "user",
            },
        }


class BKSopsAgentClient:
    """
    智能体 API 客户端

    用于与智能体服务进行通信，发送请求并获取响应
    """

    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = 300

    def __init__(self, agent_host, request_type=AgentRequestType.PLUGIN, username=""):
        self.app_code = settings.BK_APP_CODE
        self.app_secret = settings.BK_APP_SECRET
        self.agent_host = agent_host or env.BK_SOPS_AGENT_HOST
        self.request_path = PATH_CONFIG_MAP.get(request_type.value)
        self.apigw_environment = env.BKAPP_APIGW_ENVIRONMENT
        self.request_data = AgentRequestData(request_type)

        # 基础 headers
        self.headers = {
            "Content-Type": "application/json",
            "X-Bkapi-Authorization": json.dumps({"bk_app_code": self.app_code, "bk_app_secret": self.app_secret}),
        }
        # USER 类型需要额外传用户标识
        if request_type == AgentRequestType.USER:
            self.headers["X-BKAIDEV-USER"] = username

    def _make_request(self, method, params=None, data=None, timeout=None):
        try:
            url = f"{self.agent_host}/{self.apigw_environment}/{self.request_path}/"
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=timeout,
            )
            return response
        except Exception as e:
            logger.error(f"请求标准运维智能体API失败: {e}")
            return None

    def call_agent_apigw(self, user_input, stream: bool = False, timeout: int = None):
        data = self.request_data.build(user_input, stream=stream)
        response = self._make_request(method="POST", data=data, timeout=timeout or self.DEFAULT_TIMEOUT)
        if not response:
            logger.error("请求标准运维智能体API失败: 响应为空")
            return None

        try:
            result = response.json()
            if not result.get("result"):
                logger.error(f"请求标准运维智能体API失败: {result.get('message', '未知错误')}")
                return None
            return result.get("data", {})
        except (ValueError, AttributeError) as e:
            logger.error(f"解析响应失败: {e}")
            return None

    def summarize_task_execution(self, bk_biz_id, task_id):
        user_input = f"使用summarize_task_execution这个工具，帮我总结一下我的任务执行情况 ，业务ID是{bk_biz_id}，任务ID是 {task_id}"
        agent_output = self.call_agent_apigw(user_input=user_input)
        output = agent_output.get("outputs", {}).get("output", {})
        if not output:
            # 返回为None时，不发送通知
            return None
        return output

    def annalyze_task_error(self, bk_biz_id, task_id):
        user_input = f"我的标准运维任务执行失败了，业务ID是{bk_biz_id}，任务ID是{task_id}, 使用analyze_task_error这个工具帮我看看是什么问题"
        agent_output = self.call_agent_apigw(user_input=user_input)
        output = agent_output.get("outputs", {}).get("output", {})
        if not output:
            # 返回为None时，不发送通知
            return None
        return output

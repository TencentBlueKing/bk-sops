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
from datetime import datetime, timedelta
from typing import Union

from dateutil import tz
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow import AbstractIntervalGenerator, Service
from pipeline.core.flow.io import StringItemSchema
from pipeline.eri.runtime import BambooDjangoRuntime

from pipeline_plugins.components.utils.sites.open.utils import get_node_callback_url
from plugin_service.conf import PLUGIN_LOGGER
from plugin_service.exceptions import PluginServiceException
from plugin_service.plugin_client import PluginServiceApiClient

logger = logging.getLogger(PLUGIN_LOGGER)


class State:
    EMPTY = 1
    POLL = 2
    CALLBACK = 3
    SUCCESS = 4
    FAIL = 5


UNFINISHED_STATES = {State.POLL, State.CALLBACK}


class StepIntervalGenerator(AbstractIntervalGenerator):
    def __init__(self):
        super(StepIntervalGenerator, self).__init__()
        self.fix_interval = None

    def next(self):
        super(StepIntervalGenerator, self).next()
        # 最小 10s，最大 600s 一次
        return self.fix_interval or (10 if self.count < 30 else min((self.count - 25) ** 2, 600))


class RemotePluginService(Service):
    interval = StepIntervalGenerator()
    runtime = BambooDjangoRuntime()

    def outputs_format(self):
        return [
            self.OutputItem(
                name="Trace ID", key="trace_id", type="string", schema=StringItemSchema(description="Trace ID")
            ),
        ]

    def execute(self, data, parent_data):
        plugin_code = data.get_one_of_inputs("plugin_code")
        plugin_version = data.get_one_of_inputs("plugin_version")

        try:
            plugin_client = PluginServiceApiClient(plugin_code)
        except PluginServiceException as e:
            message = _(f"第三方插件client初始化失败, 错误内容: {e}")
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        detail_result = plugin_client.get_detail(plugin_version)
        if not detail_result["result"]:
            message = _(f"获取第三方插件详情失败, 错误内容: {detail_result['message']}")
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        plugin_context = dict(
            [
                (key, parent_data.inputs[key])
                for key in detail_result["data"]["context_inputs"]["properties"].keys()
                if key in parent_data.inputs
            ]
        )

        # 处理回调的情况
        if detail_result["data"].get("enable_plugin_callback"):
            logger.info("回调的节点，需要发送回调")
            self.interval = None
            plugin_context.update(
                {
                    "plugin_callback_info": {
                        "url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
                        "data": {},
                    }
                }
            )

        ok, result_data = plugin_client.invoke(plugin_version, {"inputs": data.inputs, "context": plugin_context})
        if not ok:
            message = _(
                f"调用第三方插件invoke接口错误, 错误内容: {result_data['message']}, trace_id: {result_data.get('trace_id')}"
            )
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        data.set_outputs("trace_id", result_data["trace_id"])
        self._inject_result_data_outputs(data, result_data)

        state = result_data["state"]
        if state == State.FAIL:
            data.set_outputs("ex_data", result_data["err"])
            return False
        if state in UNFINISHED_STATES:
            setattr(self, "__need_schedule__", True)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        plugin_code = data.get_one_of_inputs("plugin_code")
        trace_id = data.get_one_of_outputs("trace_id")

        if plugin_code in settings.REMOTE_PLUGIN_FIX_INTERVAL_CODES:
            self.interval.fix_interval = settings.REMOTE_PLUGIN_FIX_INTERVAL

        task_start_time = parent_data.get_one_of_inputs("task_start_time")
        # 如果插件是轮询模式且任务和节点执行时间均已经过期，则直接失败，通过先计算任务时间减少 DB 查询次数
        if (
            self.interval
            and self._is_start_time_expired(task_start_time)
            and self._is_start_time_expired(start_time=self._get_node_start_time())
        ):
            message = _(f"第三方插件执行时间超过最大限制时长：{settings.NODE_MAX_EXECUTION_DAYS} 天")
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        try:
            plugin_client = PluginServiceApiClient(plugin_code)
        except PluginServiceException as e:
            message = _(f"第三方插件client初始化失败, 错误内容: {e}")
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        ok, result_data = plugin_client.get_schedule(trace_id)

        if not ok:
            message = (
                f"remote plugin service schedule error: {result_data['message']}, "
                f"trace_id: {result_data.get('trace_id') or trace_id}"
            )
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        self._inject_result_data_outputs(data, result_data)

        state = result_data["state"]
        if state == State.FAIL:
            message = _("请通过第三方节点日志查看任务失败原因")
            logger.error(message)
            logger.error(f"[remote plugin service state failed]: {result_data}")
            data.set_outputs("ex_data", result_data.get("err") or message)
            return False
        if state in UNFINISHED_STATES:
            setattr(self, "__need_schedule__", True)
        if state == State.SUCCESS:
            self.finish_schedule()
        return True

    @staticmethod
    def _inject_result_data_outputs(data, result_data):
        outputs = result_data.get("outputs") or {}
        for key, output in outputs.items():
            data.set_outputs(key, output)

    @staticmethod
    def _is_start_time_expired(start_time: Union[str, datetime]) -> bool:
        if not start_time or settings.NODE_MAX_EXECUTION_DAYS == settings.WITHOUT_NODE_MAX_EXECUTION_DAYS_TAG:
            # 如果没有起始时间，无法比较，当作不会过期处理
            return False

        if isinstance(start_time, str):
            # 如果是 str 格式，忽略时区
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            now_time = datetime.now()
        else:
            now_time = datetime.now().astimezone(tz.tzutc())

        delta_time = now_time - start_time
        return delta_time > timedelta(days=settings.NODE_MAX_EXECUTION_DAYS)

    def _get_node_start_time(self) -> datetime:
        node_state = self.runtime.get_state(self.id)
        return node_state.started_time


class RemotePluginComponent(Component):
    code = "remote_plugin"
    name = "RemotePlugin"
    bound_service = RemotePluginService
    version = "1.0.0"

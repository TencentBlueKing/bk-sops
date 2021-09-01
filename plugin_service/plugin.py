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
import logging

from pipeline.component_framework.component import Component
from pipeline.core.flow import Service, StaticIntervalGenerator
from pipeline.core.flow.io import StringItemSchema
from plugin_service.conf import PLUGIN_LOGGER
from plugin_service.plugin_client import PluginServiceApiClient


logger = logging.getLogger(PLUGIN_LOGGER)


class State:
    EMPTY = 1
    POLL = 2
    CALLBACK = 3
    SUCCESS = 4
    FAIL = 5


class RemotePluginService(Service):
    interval = StaticIntervalGenerator(5)

    def outputs_format(self):
        return [
            self.OutputItem(
                name="Trace ID", key="trace_id", type="string", schema=StringItemSchema(description="Trace ID")
            ),
        ]

    def execute(self, data, parent_data):
        plugin_code = data.get_one_of_inputs("plugin_code")
        plugin_version = data.get_one_of_inputs("plugin_version")

        plugin_client = PluginServiceApiClient(plugin_code)

        ok, result_data = plugin_client.invoke(plugin_version, {"inputs": data.inputs, "context": parent_data.inputs})

        if not ok:
            message = (
                f"[remote plugin service invoke] error: {result_data['message']}, "
                f"trace_id: {result_data.get('trace_id')}"
            )
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        state = result_data["state"]
        data.set_outputs("trace_id", result_data["trace_id"])
        if state == State.FAIL:
            data.set_outputs("ex_data", result_data["err"])
            return False
        if state == State.POLL:
            setattr(self, "__need_schedule__", True)
        if state in [State.SUCCESS, State.POLL]:
            for key, output in result_data["outputs"].items():
                data.set_outputs(key, output)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        plugin_code = data.get_one_of_inputs("plugin_code")
        trace_id = data.get_one_of_outputs("trace_id")

        plugin_client = PluginServiceApiClient(plugin_code)
        ok, result_data = plugin_client.get_schedule(trace_id)

        if not ok:
            message = (
                f"remote plugin service schedule error: {result_data['message']}, "
                f"trace_id: {result_data.get('trace_id') or trace_id}"
            )
            logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        state = result_data["state"]
        if state == State.FAIL:
            data.set_outputs("ex_data", "please check the logs for the reason of task failure.")
            return False
        if state == State.POLL:
            setattr(self, "__need_schedule__", True)
        if state in [State.SUCCESS, State.POLL]:
            for key, output in result_data["outputs"].items():
                data.set_outputs(key, output)
        if state == State.SUCCESS:
            self.finish_schedule()
        return True


class RemotePluginComponent(Component):
    code = "remote_plugin"
    name = "RemotePlugin"
    bound_service = RemotePluginService
    version = "1.0.0"

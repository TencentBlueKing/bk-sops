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
import re
import typing
from abc import ABCMeta, abstractmethod

from pipeline.contrib.node_timer_event.adapter import NodeTimerEventAdapter
from pipeline.contrib.node_timer_event.constants import TimerType
from pipeline.contrib.node_timer_event.handlers import BaseAction
from pipeline.contrib.node_timer_event.types import TimerEvent
from pipeline.contrib.node_timer_event.utils import parse_timer_defined
from pipeline.core.data.base import DataObject

from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig

logger = logging.getLogger(__name__)

EVENT_KEY_PATTERN = re.compile(r"(?P<node_id>[a-z0-9]+)_(?P<version>[a-z0-9]+)")


class NodeTimerEventWithTimeoutConfigAdapter(NodeTimerEventAdapter):
    def __init__(self, node_id: str, version: str):

        super().__init__(node_id, version)

        self.events = self.events or []
        timeout_config: typing.Optional[TimeoutNodeConfig] = TimeoutNodeConfig.objects.filter(node_id=node_id).first()
        if not timeout_config and not self.events:
            return

        if timeout_config.action == "forced_fail_and_skip":
            defined = f"R1000/PT{timeout_config.timeout}S"
            timer_type = TimerType.TIME_CYCLE.value
        else:
            defined = f"PT{timeout_config.timeout}S"
            timer_type = TimerType.TIME_DURATION.value

        self.events = [
            {
                "enable": True,
                "action": timeout_config.action,
                "timer_type": timer_type,
                "defined": defined,
                "repetitions": parse_timer_defined(timer_type, defined)["repetitions"],
            }
        ] + self.events

        # 重新编号
        for idx, event in enumerate(self.events, 1):
            event["index"] = idx

        self.index__event_map: typing.Dict[int, TimerEvent] = {event["index"]: event for event in self.events}
        self.root_pipeline_id = timeout_config.root_pipeline_id

    @classmethod
    def parse_event_key(cls, key: str) -> typing.Dict[str, typing.Union[str, int]]:
        match = EVENT_KEY_PATTERN.match(key)
        if match:
            key_info: typing.Dict[str, typing.Union[str, int]] = match.groupdict()
            # 超时事件被置于首位
            key_info["index"] = 1
            return key_info
        return super().parse_event_key(key)

    def fetch_keys_to_be_rem(self) -> typing.List[str]:
        # 移除老协议的
        return super().fetch_keys_to_be_rem() + [f"{self.node_id}_{self.version}"]


class NodeTimeoutStrategy(metaclass=ABCMeta):
    TIMEOUT_NODE_OPERATOR = "sops_system"

    @abstractmethod
    def deal_with_timeout_node(self, task, node_id):
        pass


class ForcedFailStrategy(NodeTimeoutStrategy):
    def deal_with_timeout_node(self, task, node_id):
        return task.nodes_action("forced_fail", node_id, self.TIMEOUT_NODE_OPERATOR)


class ForcedFailAndSkipStrategy(NodeTimeoutStrategy):
    def deal_with_timeout_node(self, task, node_id):
        fail_result = task.nodes_action("forced_fail", node_id, self.TIMEOUT_NODE_OPERATOR)
        if fail_result["result"]:
            skip_result = task.nodes_action("skip", node_id, self.TIMEOUT_NODE_OPERATOR)
            return skip_result
        return fail_result


class ForcedFailAction(BaseAction):
    def do(self, data: DataObject, parent_data: DataObject, *args, **kwargs) -> bool:
        logger.info("[Action(forced_fail)] do: data -> %s, parent_data -> %s", data, parent_data)
        task_inst = TaskFlowInstance.objects.get(pk=parent_data.get_one_of_inputs("task_id"))
        task_inst.nodes_action("forced_fail", self.node_id, "sops_system")
        return True

    class Meta:
        action_name = "forced_fail"


class ForcedFailAndSkipAction(BaseAction):
    def do(self, data: DataObject, parent_data: DataObject, *args, **kwargs) -> bool:
        logger.info("[Action(forced_fail_and_skip)] do: data -> %s, parent_data -> %s", data, parent_data)
        return True

    class Meta:
        action_name = "forced_fail_and_skip"


node_timeout_handler = {
    "forced_fail": ForcedFailStrategy(),
    "forced_fail_and_skip": ForcedFailAndSkipStrategy(),
}

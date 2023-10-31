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
from abc import ABCMeta, abstractmethod

from pipeline.contrib.node_timer_event.handlers import BaseAction, register_action
from pipeline.core.data.base import DataObject

from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger(__name__)


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


@register_action("forced_fail")
class ForcedFailAction(BaseAction):
    def do(self, data: DataObject, parent_data: DataObject, *args, **kwargs) -> bool:
        logger.info("[Action(forced_fail)] do: data -> %s, parent_data -> %s", data, parent_data)
        task_inst = TaskFlowInstance.objects.get(pk=parent_data.get_one_of_inputs("task_id"))
        task_inst.nodes_action("forced_fail", self.node_id, "sops_system")
        return True


@register_action("forced_fail_and_skip")
class ForcedFailAndSkipAction(BaseAction):
    def do(self, data: DataObject, parent_data: DataObject, *args, **kwargs) -> bool:
        logger.info("[Action(forced_fail_and_skip)] do: data -> %s, parent_data -> %s", data, parent_data)
        return True


node_timeout_handler = {
    "forced_fail": ForcedFailStrategy(),
    "forced_fail_and_skip": ForcedFailAndSkipStrategy(),
}

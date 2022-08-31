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

import requests
from bamboo_engine import states
from bamboo_engine.context import Context
from bamboo_engine.eri import ContextValue, ContextValueType
from django.conf import settings
from django.core.exceptions import ValidationError

from pipeline.eri.runtime import BambooDjangoRuntime
from requests import HTTPError

from gcloud.taskflow3.domains.dispatchers import NodeCommandDispatcher
from gcloud.taskflow3.models import TaskCallBackRecord, TaskFlowInstance, TaskFlowRelation
from gcloud.utils.redis_lock import redis_lock

logger = logging.getLogger("root")


class TaskCallBacker:
    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id
        self.record = TaskCallBackRecord.objects.filter(task_id=self.task_id).first()
        self.extra_info = {"task_id": self.task_id, **json.loads(self.record.extra_info), **kwargs}

    def check_record_existence(self):
        return True if self.record else False

    def update_record(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.record, key, value)
        self.record.save(update_fields=list(kwargs.keys()))

    def callback(self):
        if self.record.url:
            return self._url_callback()
        return self._subprocess_callback()

    def _subprocess_callback(self):
        try:
            node_id, version, engine_ver = (
                self.extra_info["node_id"],
                self.extra_info["node_version"],
                self.extra_info["engine_ver"],
            )
            with redis_lock(settings.redis_inst, key=f"sc_{node_id}_{version}") as (acquired_result, err):
                if not acquired_result:
                    # 如果对应节点已经在回调，则直接忽略本次回调
                    logger.error(f"[TaskCallBacker _subprocess_callback] get lock error: {err}")
                    return True
                parent_task_id = TaskFlowRelation.objects.filter(task_id=self.task_id).first().parent_task_id
                dispatcher = NodeCommandDispatcher(engine_ver=engine_ver, node_id=node_id, taskflow_id=parent_task_id)
                runtime = BambooDjangoRuntime()
                node_state = runtime.get_state(node_id)
                if node_state.name == states.RUNNING:
                    dispatcher.dispatch(command="callback", operator="", version=version, data=self.extra_info)
                elif node_state.name == states.FAILED:
                    if self.extra_info["task_success"] is False:
                        logger.info(
                            f"[TaskCallBacker _subprocess_callback] info: child task not success: {self.task_id}"
                        )
                        return True
                    child_pipeline_id = TaskFlowInstance.objects.get(id=self.task_id).pipeline_instance.instance_id
                    child_outputs = runtime.get_execution_data_outputs(node_id=child_pipeline_id)
                    if child_outputs:
                        pipeline_id = TaskFlowInstance.objects.get(id=parent_task_id).pipeline_instance.instance_id
                        # 注入节点输出
                        outputs = {
                            key: ContextValue(key=key, type=ContextValueType.PLAIN, value=value)
                            for key, value in child_outputs.items()
                        }
                        cur_execution_outputs = runtime.get_execution_data_outputs(node_id)
                        cur_execution_outputs.update(outputs)
                        runtime.set_execution_data_outputs(node_id, cur_execution_outputs)
                        # 子流程输出同步到上下文
                        cur_outputs = runtime.get_data_outputs(node_id)
                        context = Context(runtime, [], {})
                        context.extract_outputs(pipeline_id, cur_outputs, child_outputs)
                    dispatcher.dispatch(command="skip", operator="")
                else:
                    raise ValidationError(f"node state is not running or failed, but {node_state.name}")
        except Exception as e:
            message = f"[TaskCallBacker _subprocess_callback] error: {e}, with data {self.record.extra_info}"
            logger.exception(message)
        else:
            logger.info(f"[TaskCallBacker _subprocess_callback] data: {self.record.extra_info}, callback success.")
        return True

    def _url_callback(self):
        url = self.record.url
        response = None
        try:
            response = requests.post(url, data=self.extra_info)
            response.raise_for_status()
        except HTTPError as e:
            message = (
                f"[TaskCallBacker call_back] {url}, data: {self.extra_info}, "
                f"response: {getattr(response, 'content', None)}, error: {e}"
            )
            logger.exception(message)
            return False
        return True

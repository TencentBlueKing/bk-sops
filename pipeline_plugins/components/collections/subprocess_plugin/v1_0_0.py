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
from typing import List

from bamboo_engine.context import Context
from bamboo_engine.template import Template
from django.db import transaction
from pipeline.core.flow.io import StringItemSchema, IntItemSchema

from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.core.models import EngineConfig
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from pydantic import BaseModel

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.taskflow3.models import TaskFlowInstance, TimeoutNodeConfig, TaskCallBackRecord, TaskFlowRelation
from gcloud.tasktmpl3.models import TaskTemplate
from pipeline.component_framework.component import Component
from pipeline.core.flow import Service

logger = logging.getLogger("celery")


class Subprocess(BaseModel):
    subprocess_name: str
    pipeline: dict
    template_id: str
    always_use_latest: bool = False
    template_source: str
    scheme_id_list: List[int] = []


class SubprocessPluginService(Service):
    __need_schedule__ = True
    runtime = BambooDjangoRuntime()

    def outputs_format(self):
        return [
            self.OutputItem(name="Task ID", key="task_id", type="int", schema=IntItemSchema(description="Task ID")),
            self.OutputItem(
                name="Task URL", key="task_url", type="string", schema=StringItemSchema(description="Task URL")
            ),
        ]

    def execute(self, data, parent_data):
        parent_task_id = parent_data.get_one_of_inputs("task_id")
        try:
            parent_task = TaskFlowInstance.objects.get(id=parent_task_id)
        except TaskFlowInstance.DoesNotExist:
            data.set_outputs("ex_data", f"parent task {parent_task_id} not found")
            return False

        if parent_task.engine_ver != EngineConfig.ENGINE_VER_V2:
            data.set_outputs("ex_data", "subprocess plugin only supports engine ver 2")
            return False

        subprocess_data = data.get_one_of_inputs("subprocess") or {}
        subprocess = Subprocess(**subprocess_data)
        pipeline_tree = subprocess.pipeline

        # 渲染父任务中的参数
        constants = pipeline_tree.get("constants", {})
        subprocess_inputs = {
            key: constant["value"] for key, constant in constants.items() if constant.get("need_render")
        }
        inputs_refs = Template(subprocess_inputs).get_reference()
        self.logger.info(f"subprocess original refs: {inputs_refs}")
        additional_refs = self.runtime.get_context_key_references(pipeline_id=self.top_pipeline_id, keys=inputs_refs)
        inputs_refs = inputs_refs.union(additional_refs)
        self.logger.info(f"subprocess final refs: {inputs_refs}")
        context_values = self.runtime.get_context_values(pipeline_id=self.top_pipeline_id, keys=inputs_refs)
        root_pipeline_inputs = {
            key: inputs.value for key, inputs in self.runtime.get_data_inputs(self.top_pipeline_id).items()
        }
        context = Context(self.runtime, context_values, root_pipeline_inputs)
        hydrated_context = context.hydrate(deformat=True)
        self.logger.info(f"subprocess parent hydrated context: {hydrated_context}")

        parsed_subprocess_inputs = Template(subprocess_inputs).render(hydrated_context)
        for key, constant in pipeline_tree.get("constants", {}).items():
            if constant.get("need_render") and key in parsed_subprocess_inputs:
                constant["value"] = parsed_subprocess_inputs[key]
        self.logger.info(f'subprocess parsed constants: {pipeline_tree.get("constants", {})}')

        # 构造pipeline_instance & taskflow_instance
        with transaction.atomic():
            pipeline_instance_kwargs = {
                "name": f'{parent_data.get_one_of_inputs("task_name")}-{subprocess.subprocess_name}',
                "creator": parent_task.executor,
                "pipeline_tree": pipeline_tree,
                "description": "",
            }
            template = (
                CommonTemplate(pipeline_template=None)
                if subprocess.template_source not in NON_COMMON_TEMPLATE_TYPES
                else TaskTemplate(pipeline_template=None)
            )
            pipeline_instance = TaskFlowInstance.objects.create_pipeline_instance(
                template=template, independent_subprocess=True, **pipeline_instance_kwargs
            )
            taskflow_kwargs = {
                "project_id": parent_data.get_one_of_inputs("project_id"),
                "pipeline_instance": pipeline_instance,
                "category": parent_task.category,
                "template_id": parent_task.template_id,
                "template_source": subprocess.template_source,
                "create_method": parent_task.create_method,
                "create_info": parent_task.create_info,
                "flow_type": parent_task.flow_type,
                "current_flow": parent_task.current_flow,
                "engine_ver": parent_task.engine_ver,
                "recorded_executor_proxy": parent_task.recorded_executor_proxy,
                "is_child_taskflow": True,
            }
            task = TaskFlowInstance.objects.create(**taskflow_kwargs)
            try:
                root_task_id = TaskFlowRelation.objects.get(task_id=parent_task_id).root_task_id
            except TaskFlowRelation.DoesNotExist:
                root_task_id = parent_task_id
            TaskFlowRelation.objects.create(task_id=task.id, parent_task_id=parent_task_id, root_task_id=root_task_id)

            # create callback record
            callback_info = {
                "source": f"subprocess task {task.id}",
                "node_id": self.id,
                "node_version": self.version,
                "engine_ver": parent_task.engine_ver,
            }
            TaskCallBackRecord.objects.create(task_id=task.id, url="", extra_info=json.dumps(callback_info))

            # crete auto retry strategy
            arn_creator = AutoRetryNodeStrategyCreator(
                taskflow_id=task.id, root_pipeline_id=task.pipeline_instance.instance_id
            )
            arn_creator.batch_create_strategy(task.pipeline_instance.execution_data)

            # create timeout config
            TimeoutNodeConfig.objects.batch_create_node_timeout_config(
                taskflow_id=task.id,
                root_pipeline_id=task.pipeline_instance.instance_id,
                pipeline_tree=task.pipeline_instance.execution_data,
            )

        task.task_action("start", parent_task.executor)
        data.set_outputs("task_id", task.id)
        data.set_outputs("task_url", task.url)
        return True

    def schedule(self, data, parent_data, callback_data=None):
        task_success = callback_data.get("task_success", False)
        task_id = data.get_one_of_outputs("task_id")
        self.finish_schedule()
        if not task_success:
            return False
        try:
            subprocess_task = TaskFlowInstance.objects.get(id=task_id)
        except TaskFlowInstance.DoesNotExist:
            message = f"subprocess task {task_id} not found"
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        subprocess_pipeline_id = subprocess_task.pipeline_instance.instance_id
        logger.info(f"subprocess pipeline id: {subprocess_pipeline_id}")
        subprocess_execution_data_outputs = self.runtime.get_execution_data_outputs(node_id=subprocess_pipeline_id)
        logger.info(f"subprocess execution data outputs: {subprocess_execution_data_outputs}")
        node_outputs = self.runtime.get_data_outputs(self.id)
        logger.info(f"node outputs: {node_outputs}")
        for origin_key, target_key in node_outputs.items():
            if origin_key in subprocess_execution_data_outputs:
                data.set_outputs(target_key, subprocess_execution_data_outputs[origin_key])
        return True


class SubprocessPluginComponent(Component):
    code = "subprocess_plugin"
    name = "SubprocessPlugin"
    bound_service = SubprocessPluginService
    version = "1.0.0"

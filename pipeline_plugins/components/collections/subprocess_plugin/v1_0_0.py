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
import copy
import datetime
import json
from typing import List

from bamboo_engine.context import Context
from bamboo_engine.template import Template
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow import Service
from pipeline.core.flow.io import IntItemSchema, StringItemSchema
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.models import PipelineTemplate
from pydantic import BaseModel

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES, PROJECT
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.contrib.operate_record.utils import extract_extra_info
from gcloud.core.models import EngineConfig, Project
from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.taskflow3.models import TaskCallBackRecord, TaskFlowInstance, TaskFlowRelation, TimeoutNodeConfig
from gcloud.tasktmpl3.models import TaskTemplate


class Subprocess(BaseModel):
    subprocess_name: str
    pipeline: dict
    template_id: str
    always_use_latest: bool = False
    template_source: str = PROJECT
    scheme_id_list: List[int] = []


class SubprocessPluginService(Service):
    __need_schedule__ = True
    runtime = BambooDjangoRuntime()

    def outputs_format(self):
        return [
            self.OutputItem(name="任务ID", key="task_id", type="int", schema=IntItemSchema(description="Task ID")),
            self.OutputItem(
                name="任务URL", key="task_url", type="string", schema=StringItemSchema(description="Task URL")
            ),
            self.OutputItem(
                name="任务名", key="task_name", type="string", schema=StringItemSchema(description="Task Name")
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
            key: constant["value"]
            for key, constant in constants.items()
            if constant.get("show_type") == "show" and constant.get("need_render", True)
        }
        raw_subprocess_inputs = copy.deepcopy(subprocess_inputs)
        inputs_refs = Template(subprocess_inputs).get_reference()
        self.logger.info(f"subprocess original refs: {inputs_refs}")
        additional_refs = self.runtime.get_context_key_references(pipeline_id=self.top_pipeline_id, keys=inputs_refs)
        inputs_refs = inputs_refs.union(additional_refs)
        self.logger.info(f"subprocess final refs: {inputs_refs}")
        context_values = self.runtime.get_context_values(pipeline_id=self.top_pipeline_id, keys=inputs_refs)
        context_mappings = {c.key: c for c in context_values}
        root_pipeline_inputs = {
            key: inputs.value for key, inputs in self.runtime.get_data_inputs(self.top_pipeline_id).items()
        }
        context = Context(self.runtime, context_values, root_pipeline_inputs)
        hydrated_context = context.hydrate(deformat=True)
        self.logger.info(f"subprocess parent hydrated context: {hydrated_context}")

        parsed_subprocess_inputs = Template(subprocess_inputs).render(hydrated_context)
        parent_constants = parent_task.pipeline_tree["constants"]
        for key, constant in pipeline_tree.get("constants", {}).items():
            # 如果父流程直接勾选，则直接使用父流程对应变量的值
            raw_constant_value = raw_subprocess_inputs.get(key)
            if (
                raw_constant_value
                and isinstance(raw_constant_value, str)
                and parent_constants.get(raw_constant_value)
                and self.id in parent_constants[raw_constant_value]["source_info"]
                and key in parent_constants[raw_constant_value]["source_info"][self.id]
            ):
                variable = context_mappings[raw_subprocess_inputs[key]]
                # 需要针对文本值下拉框进行特殊处理
                constant["value"] = (
                    variable.value["info_value"] if variable.code == "text_value_select" else variable.value
                )
            elif constant.get("need_render", True) and key in parsed_subprocess_inputs:
                constant["value"] = parsed_subprocess_inputs[key]
        self.logger.info(f'subprocess parsed constants: {pipeline_tree.get("constants", {})}')

        # 构造pipeline_instance & taskflow_instance
        with transaction.atomic():
            project_tz = (
                getattr(Project.objects.filter(id=parent_data.get_one_of_inputs("project_id")).first(), "time_zone")
                or settings.TIME_ZONE
            )
            time_stamp = datetime.datetime.now(tz=timezone.pytz.timezone(project_tz)).strftime("%Y%m%d%H%M%S")
            template_name = getattr(PipelineTemplate.objects.filter(template_id=subprocess.template_id).first(), "name")
            pipeline_instance_kwargs = {
                "name": f"{template_name}_{time_stamp}",
                "creator": parent_task.executor,
                "pipeline_tree": pipeline_tree,
                "description": "",
            }
            pipeline_template = PipelineTemplate.objects.filter(template_id=subprocess.template_id).first()
            template_cls = (
                CommonTemplate if subprocess.template_source not in NON_COMMON_TEMPLATE_TYPES else TaskTemplate
            )
            template = template_cls(pipeline_template=pipeline_template)
            primitive_template = template_cls.objects.filter(pipeline_template=pipeline_template).first()
            pipeline_instance = TaskFlowInstance.objects.create_pipeline_instance(
                template=template, independent_subprocess=True, **pipeline_instance_kwargs
            )
            taskflow_kwargs = {
                "project_id": parent_data.get_one_of_inputs("project_id"),
                "pipeline_instance": pipeline_instance,
                "category": parent_task.category,
                "template_id": parent_task.template_id,
                "template_source": parent_task.template_source,
                "create_method": parent_task.create_method,
                "create_info": parent_task.create_info,
                "flow_type": parent_task.flow_type,
                "current_flow": parent_task.current_flow,
                "engine_ver": parent_task.engine_ver,
                "recorded_executor_proxy": parent_task.recorded_executor_proxy,
                "is_child_taskflow": True,
            }
            if subprocess.template_source and getattr(primitive_template, "id", None):
                taskflow_kwargs.update(
                    {
                        "extra_info": json.dumps(
                            {
                                "primitive_template_source": subprocess.template_source,
                                "primitive_template_id": str(primitive_template.id),
                            }
                        )
                    }
                )
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

            # 记录操作流水
            pipeline_constants = pipeline_instance.execution_data.get("constants")
            extra_info = extract_extra_info(pipeline_constants)
            operate_record_signal.send(
                sender=RecordType.task.name,
                operator="system",
                operate_type=OperateType.create.name,
                operate_source=OperateSource.parent.name,
                instance_id=task.id,
                project_id=task.project_id,
                extra_info=extra_info,
            )

        task.task_action("start", parent_task.executor)
        data.set_outputs("task_id", task.id)
        data.set_outputs("task_url", task.url)
        data.set_outputs("task_name", task.name)

        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.task.name,
            operator="system",
            operate_type=OperateType.start.name,
            operate_source=OperateSource.parent.name,
            instance_id=task.id,
            project_id=task.project_id,
        )
        return True

    def schedule(self, data, parent_data, callback_data=None):
        task_success = callback_data.get("task_success", False)
        task_id = data.get_one_of_outputs("task_id")
        self.finish_schedule()
        if not task_success:
            data.set_outputs("ex_data", callback_data.get("ex_data") or "子流程执行失败，请检查失败节点")
            return False
        try:
            subprocess_task = TaskFlowInstance.objects.get(id=task_id)
        except TaskFlowInstance.DoesNotExist:
            message = _(f"子任务[{task_id}]不存在")
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False

        subprocess_pipeline_id = subprocess_task.pipeline_instance.instance_id
        self.logger.info(f"subprocess pipeline id: {subprocess_pipeline_id}")
        subprocess_execution_data_outputs = self.runtime.get_execution_data_outputs(node_id=subprocess_pipeline_id)
        self.logger.info(f"subprocess execution data outputs: {subprocess_execution_data_outputs}")
        node_outputs = self.runtime.get_data_outputs(self.id)
        self.logger.info(f"node outputs: {node_outputs}")
        for key in filter(lambda x: x in subprocess_execution_data_outputs, node_outputs.keys()):
            data.set_outputs(key, subprocess_execution_data_outputs[key])
        return True


class SubprocessPluginComponent(Component):
    code = "subprocess_plugin"
    name = "SubprocessPlugin"
    bound_service = SubprocessPluginService
    version = "1.0.0"

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
from typing import List, Dict

from django.db.models import QuerySet
from gcloud.contrib.cleaner.models import ExpiredTaskArchive
from gcloud.taskflow3.models import TaskFlowInstance

from pipeline.contrib.periodic_task.models import PeriodicTaskHistory
from pipeline.eri.models import (
    ContextValue,
    ContextOutputs,
    Process,
    Node,
    Data,
    State,
    ExecutionHistory,
    ExecutionData,
    CallbackData,
    Schedule,
)

from pipeline.models import PipelineInstance, TreeInfo, Snapshot
from pipeline_web.core.models import NodeInInstance


def get_clean_pipeline_instance_data(instance_ids: List[str]) -> Dict[str, QuerySet]:
    """
    根据 pipeline_instance_id 列表清除对应任务执行数据
    :param instance_ids: 需要清理的 pipeline_instance_id 列表
    :return: Dict[str, QuerySet]
    """
    pipeline_instances = PipelineInstance.objects.filter(instance_id__in=instance_ids)
    nodes_in_pipeline = NodeInInstance.objects.filter(instance_id__in=instance_ids)

    tree_info_ids = pipeline_instances.values_list("tree_info_id", flat=True)
    tree_info = TreeInfo.objects.filter(id__in=list(tree_info_ids))

    execution_snapshot_ids = pipeline_instances.values_list("execution_snapshot_id", flat=True)
    execution_snapshot = Snapshot.objects.filter(id__in=list(execution_snapshot_ids))

    pipeline_ids = instance_ids
    context_value = ContextValue.objects.filter(pipeline_id__in=pipeline_ids)
    context_outputs = ContextOutputs.objects.filter(pipeline_id__in=pipeline_ids)
    process = Process.objects.filter(root_pipeline_id__in=pipeline_ids)
    periodic_task_history = PeriodicTaskHistory.objects.filter(pipeline_instance_id__in=pipeline_ids)

    node_ids = list(nodes_in_pipeline.values_list("node_id", flat=True)) + instance_ids
    nodes = Node.objects.filter(node_id__in=node_ids)
    data = Data.objects.filter(node_id__in=node_ids)
    states = State.objects.filter(node_id__in=node_ids)
    execution_history = ExecutionHistory.objects.filter(node_id__in=node_ids)
    execution_data = ExecutionData.objects.filter(node_id__in=node_ids)
    callback_data = CallbackData.objects.filter(node_id__in=node_ids)
    schedules = Schedule.objects.filter(node_id__in=node_ids)

    return {
        "tree_info": tree_info,
        "nodes_in_pipeline": nodes_in_pipeline,
        "execution_snapshot": execution_snapshot,
        "context_value": context_value,
        "context_outputs": context_outputs,
        "process": process,
        "node": nodes,
        "data": data,
        "state": states,
        "execution_history": execution_history,
        "execution_data": execution_data,
        "callback_data": callback_data,
        "schedules": schedules,
        "periodic_task_history": periodic_task_history,
        "pipeline_instances": pipeline_instances,
    }


def archived_expired_task(expire_pipeline_instance_ids):
    """
    根据 instance_id 将过期任务的数据进行归档
    """
    try:
        tasks = (
            TaskFlowInstance.objects.select_related("pipeline_instance")
            .filter(pipeline_instance__instance_id__in=expire_pipeline_instance_ids)
            .order_by("id")
        )
        archived_task_list = []
        archived_task_ids = []
        for task in tasks:
            if task.is_deleted:
                continue
            archived_data = ExpiredTaskArchive(
                task_id=task.id,
                project_id=task.project_id,
                name=task.pipeline_instance.name,
                template_id=task.pipeline_instance.template_id,
                task_template_id=task.template_id,
                template_source=task.template_source,
                create_method=task.create_method,
                create_info=task.create_info,
                creator=task.pipeline_instance.creator,
                create_time=task.pipeline_instance.create_time,
                executor=task.pipeline_instance.executor,
                recorded_executor_proxy=task.recorded_executor_proxy,
                start_time=task.pipeline_instance.start_time,
                finish_time=task.pipeline_instance.finish_time,
                is_started=task.pipeline_instance.is_started,
                is_finished=task.pipeline_instance.is_finished,
                is_revoked=task.pipeline_instance.is_revoked,
                engine_ver=task.engine_ver,
                is_child_taskflow=task.is_child_taskflow,
                snapshot_id=task.pipeline_instance.snapshot_id,
                extra_info=json.dumps(
                    {
                        "flow_type": task.flow_type,
                        "current_flow": task.current_flow,
                        "extra_info": task.extra_info,
                    }
                ),
            )
            archived_task_ids.append(task.id)
            archived_task_list.append(archived_data)
    except Exception as e:
        raise Exception(f"Archived expired task error: {e}")

    return archived_task_list, archived_task_ids

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
import logging
import json
from typing import Dict, List

from django.conf import settings
from django.db.models import QuerySet
from pipeline.contrib.periodic_task.models import PeriodicTaskHistory
from pipeline.eri.models import (
    CallbackData,
    ContextOutputs,
    ContextValue,
    Data,
    ExecutionData,
    ExecutionHistory,
    Node,
    Process,
    Schedule,
    State,
)
from pipeline.models import PipelineInstance, Snapshot, TreeInfo

from gcloud.utils.data_handler import chunk_data
from gcloud.contrib.cleaner.models import ArchivedTaskInstance
from gcloud.taskflow3.models import AutoRetryNodeStrategy, TimeoutNodeConfig
from pipeline_web.core.models import NodeInInstance

logger = logging.getLogger("root")


def get_clean_pipeline_instance_data(instance_ids: List[str]) -> Dict[str, QuerySet]:
    """
    根据 pipeline_instance_id 列表清除对应任务执行数据
    :param instance_ids: 需要清理的 pipeline_instance_id 列表
    :return: Dict[str, QuerySet]
    """
    if not instance_ids:
        return {}

    pipeline_instances = PipelineInstance.objects.filter(instance_id__in=instance_ids)
    # 业务层表，无法覆盖周期任务数据
    nodes_in_pipeline = NodeInInstance.objects.filter(instance_id__in=instance_ids)

    tree_info_ids = pipeline_instances.values_list("tree_info_id", flat=True)
    tree_infos = TreeInfo.objects.filter(id__in=list(tree_info_ids))

    # 通过 tree_info 获得节点集合
    node_id_set = set(instance_ids)
    cover_tree_info_ids = set()
    # tree_info中带有计算好node_ids的情况
    for tree_info in tree_infos:
        if "node_id_set" in tree_info.data:
            node_id_set |= set(tree_info.data["node_id_set"])
            cover_tree_info_ids.add(tree_info.id)
    for pipeline_instance in pipeline_instances:
        if pipeline_instance.tree_info_id not in cover_tree_info_ids:
            pipeline_instance._get_node_id_set(node_id_set, pipeline_instance.execution_data)  # noqa

    execution_snapshot_ids = pipeline_instances.values_list("execution_snapshot_id", flat=True)
    execution_snapshot = Snapshot.objects.filter(id__in=list(execution_snapshot_ids))

    pipeline_ids = instance_ids
    logger.info(
        f"[get_clean_pipeline_instance_data] fetching pipeline_ids number: {len(pipeline_ids)}, "
        f"e.x.:{pipeline_ids[:3]}..."
    )
    context_value = ContextValue.objects.filter(pipeline_id__in=pipeline_ids)
    context_outputs = ContextOutputs.objects.filter(pipeline_id__in=pipeline_ids)
    process = Process.objects.filter(root_pipeline_id__in=pipeline_ids)
    periodic_task_history = PeriodicTaskHistory.objects.filter(pipeline_instance_id__in=pipeline_ids)

    node_ids = list(node_id_set)
    logger.info(f"[get_clean_pipeline_instance_data] fetching node_ids number: {len(node_ids)}, e.x.:{node_ids[:3]}...")
    callback_data = CallbackData.objects.filter(node_id__in=node_ids)  # CallbackData 的 node_id 字段没有索引，需要遍历不分块
    chunk_size = settings.CLEAN_EXPIRED_V2_TASK_NODE_BATCH_NUM
    retry_node = chunk_data(node_ids, chunk_size, lambda x: AutoRetryNodeStrategy.objects.filter(node_id__in=x))
    timeout_node = chunk_data(node_ids, chunk_size, lambda x: TimeoutNodeConfig.objects.filter(node_id__in=x))
    nodes_list = chunk_data(node_ids, chunk_size, lambda x: Node.objects.filter(node_id__in=x))
    data_list = chunk_data(node_ids, chunk_size, lambda x: Data.objects.filter(node_id__in=x))
    states_list = chunk_data(node_ids, chunk_size, lambda x: State.objects.filter(node_id__in=x))
    execution_history_list = chunk_data(node_ids, chunk_size, lambda x: ExecutionHistory.objects.filter(node_id__in=x))
    execution_data_list = chunk_data(node_ids, chunk_size, lambda x: ExecutionData.objects.filter(node_id__in=x))
    schedules_list = chunk_data(node_ids, chunk_size, lambda x: Schedule.objects.filter(node_id__in=x))

    return {
        "tree_info": tree_infos,
        "nodes_in_pipeline": nodes_in_pipeline,
        "execution_snapshot": execution_snapshot,
        "context_value": context_value,
        "context_outputs": context_outputs,
        "process": process,
        "periodic_task_history": periodic_task_history,
        "pipeline_instances": pipeline_instances,
        "retry_node": retry_node,
        "timeout_node": timeout_node,
        "callback_data": callback_data,
        "node_list": nodes_list,
        "data_list": data_list,
        "state_list": states_list,
        "execution_history_list": execution_history_list,
        "execution_data_list": execution_data_list,
        "schedules_list": schedules_list,
    }


def generate_archived_task_instances(tasks):
    """
    生成归档任务实例
    :param tasks: 待归档的过期任务
    :return: List[ArchivedTaskInstance], List[int]
    """
    archived_task_instances = []
    archived_task_ids = []
    try:
        for task in tasks:
            if task.is_deleted:
                continue
            archived_data = ArchivedTaskInstance(
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
            archived_task_instances.append(archived_data)
    except Exception as e:
        logger.exception(f"Generate archived task error: {e}")
        raise Exception(f"Generate archived task error: {e}")

    return archived_task_instances, archived_task_ids

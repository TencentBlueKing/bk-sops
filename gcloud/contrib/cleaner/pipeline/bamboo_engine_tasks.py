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
from pipeline_web.core.models import NodeInInstance

logger = logging.getLogger("root")


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
    logger.info(
        f"[get_clean_pipeline_instance_data] fetching pipeline_ids number: {pipeline_ids}, e.x.:{pipeline_ids[:3]}..."
    )
    context_value = ContextValue.objects.filter(pipeline_id__in=pipeline_ids)
    context_outputs = ContextOutputs.objects.filter(pipeline_id__in=pipeline_ids)
    process = Process.objects.filter(root_pipeline_id__in=pipeline_ids)
    periodic_task_history = PeriodicTaskHistory.objects.filter(pipeline_instance_id__in=pipeline_ids)

    node_ids = list(nodes_in_pipeline.values_list("node_id", flat=True)) + instance_ids
    logger.info(f"[get_clean_pipeline_instance_data] fetching node_ids number: {node_ids}, e.x.:{node_ids[:3]}...")
    chunk_size = settings.CLEAN_EXPIRED_V2_TASK_NODE_BATCH_NUM
    nodes_list = chunk_data(node_ids, chunk_size, lambda x: Node.objects.filter(node_id__in=x))
    data_list = chunk_data(node_ids, chunk_size, lambda x: Data.objects.filter(node_id__in=x))
    states_list = chunk_data(node_ids, chunk_size, lambda x: State.objects.filter(node_id__in=x))
    execution_history_list = chunk_data(node_ids, chunk_size, lambda x: ExecutionHistory.objects.filter(node_id__in=x))
    execution_data_list = chunk_data(node_ids, chunk_size, lambda x: ExecutionData.objects.filter(node_id__in=x))
    callback_data_list = chunk_data(node_ids, chunk_size, lambda x: CallbackData.objects.filter(node_id__in=x))
    schedules_list = chunk_data(node_ids, chunk_size, lambda x: Schedule.objects.filter(node_id__in=x))

    return {
        "tree_info": tree_info,
        "nodes_in_pipeline": nodes_in_pipeline,
        "execution_snapshot": execution_snapshot,
        "context_value": context_value,
        "context_outputs": context_outputs,
        "process": process,
        "periodic_task_history": periodic_task_history,
        "pipeline_instances": pipeline_instances,
        "node_list": nodes_list,
        "data_list": data_list,
        "state_list": states_list,
        "execution_history_list": execution_history_list,
        "execution_data_list": execution_data_list,
        "callback_data_list": callback_data_list,
        "schedules_list": schedules_list,
    }

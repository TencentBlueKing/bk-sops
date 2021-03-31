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

import copy
import logging

from pipeline.engine import states as pipeline_states
from bamboo_engine import states as bamboo_engine_states

from gcloud.constants import PROJECT
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.models import CommonTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.context import TaskContext
from gcloud.utils.dates import format_datetime

logger = logging.getLogger("root")


def get_instance_context(pipeline_instance, data_type, username=""):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance=pipeline_instance)
    except TaskFlowInstance.DoesNotExist:
        logger.warning("TaskFlowInstance does not exist: pipeline_template.id=%s" % pipeline_instance.pk)
        return {}
    # pipeline的root_pipeline_params数据，最终会传给插件的parent_data，是简单地字典格式
    if data_type == "data":
        return TaskContext(taskflow, username).__dict__
    # pipeline的root_pipeline_context数据，可以直接在参数中引用，如 ${_system.biz_cc_id}
    else:
        return TaskContext(taskflow, username).context()


def preview_template_tree(project_id, template_source, template_id, version, exclude_task_nodes_id):

    if template_source == PROJECT:
        template = TaskTemplate.objects.get(pk=template_id, is_deleted=False, project_id=project_id)
    else:
        template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)
    pipeline_tree = template.get_pipeline_tree_by_version(version)
    template_constants = copy.deepcopy(pipeline_tree["constants"])
    TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

    constants_not_referred = {
        key: value for key, value in list(template_constants.items()) if key not in pipeline_tree["constants"]
    }

    return {"pipeline_tree": pipeline_tree, "constants_not_referred": constants_not_referred}


def _format_status_time(status_tree):
    status_tree.setdefault("children", {})
    status_tree.pop("created_time", "")

    status_tree["start_time"] = format_datetime(status_tree.pop("started_time"))
    status_tree["finish_time"] = format_datetime(status_tree.pop("archived_time"))


def format_pipeline_status(status_tree):
    """
    @summary: 转换通过 pipeline api 获取的任务状态格式
    @return:
    """
    _format_status_time(status_tree)
    child_status = set()
    for identifier_code, child_tree in list(status_tree["children"].items()):
        format_pipeline_status(child_tree)
        child_status.add(child_tree["state"])

    if status_tree["state"] == pipeline_states.BLOCKED:
        if pipeline_states.RUNNING in child_status:
            status_tree["state"] = pipeline_states.RUNNING
        elif pipeline_states.FAILED in child_status:
            status_tree["state"] = pipeline_states.FAILED
        elif pipeline_states.SUSPENDED in child_status or "NODE_SUSPENDED" in child_status:
            status_tree["state"] = "NODE_SUSPENDED"
        # 子流程 BLOCKED 状态表示子节点失败
        elif not child_status:
            status_tree["state"] = pipeline_states.FAILED


def format_bamboo_engine_status(status_tree):
    """
    @summary: 转换通过 bamboo engine api 获取的任务状态格式
    @return:
    """
    _format_status_time(status_tree)
    child_status = set()
    for identifier_code, child_tree in list(status_tree["children"].items()):
        format_bamboo_engine_status(child_tree)
        child_status.add(child_tree["state"])

    if status_tree["state"] == bamboo_engine_states.RUNNING:
        if bamboo_engine_states.FAILED in child_status:
            status_tree["state"] = bamboo_engine_states.FAILED
        elif bamboo_engine_states.SUSPENDED in child_status or "NODE_SUSPENDED" in child_status:
            status_tree["state"] = "NODE_SUSPENDED"

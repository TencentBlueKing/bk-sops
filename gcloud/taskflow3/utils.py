# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import copy
import logging

from gcloud.constants import PROJECT
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.models import CommonTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.context import TaskContext

logger = logging.getLogger("root")


def get_instance_context(pipeline_instance, data_type, username=''):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance=pipeline_instance)
    except TaskFlowInstance.DoesNotExist:
        logger.warning('TaskFlowInstance does not exist: pipeline_template.id=%s' % pipeline_instance.pk)
        return {}
    # pipeline的root_pipeline_params数据，最终会传给插件的parent_data，是简单地字典格式
    if data_type == 'data':
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
    template_constants = copy.deepcopy(pipeline_tree['constants'])
    TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

    constants_not_referred = {
        key: value for key, value in list(template_constants.items())
        if key not in pipeline_tree['constants']
    }

    return {
        'pipeline_tree': pipeline_tree,
        'constants_not_referred': constants_not_referred
    }

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

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.context import TaskContext

logger = logging.getLogger("root")


def get_instance_context(pipeline_instance, data_type):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance=pipeline_instance)
    except TaskFlowInstance.DoesNotExist:
        logger.warning('TaskFlowInstance does not exist: pipeline_template.id=%s' % pipeline_instance.pk)
        return {}
    # pipeline的root_pipeline_params数据，最终会传给插件的parent_data，是简单地字典格式
    if data_type == 'data':
        return TaskContext(taskflow, pipeline_instance.executor).__dict__
    # pipeline的root_pipeline_context数据，可以直接在参数中引用，如 ${_system.biz_cc_id}
    else:
        return TaskContext(taskflow, pipeline_instance.executor).context()

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

import logging
from django.utils import translation

from gcloud.core.utils import get_biz_maintainer_info
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("root")


def get_instance_context(obj):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance=obj)
    except TaskFlowInstance.DoesNotExist:
        logger.warning('TaskFlowInstance Does not exist: pipeline_template.id=%s' % obj.pk)
        return {}
    operator = obj.executor
    biz_cc_id = taskflow.business.cc_id
    supplier_account = taskflow.business.cc_owner
    executor, _ = get_biz_maintainer_info(biz_cc_id, operator, use_in_context=True)
    context = {
        'language': translation.get_language(),
        'biz_cc_id': biz_cc_id,
        'biz_cc_name': taskflow.business.cc_name,
        'biz_supplier_account': supplier_account,
        # 执行任务的操作员
        'operator': operator,
        # 调用ESB接口的执行者
        'executor': executor,
        'task_id': taskflow.id,
        'task_name': taskflow.pipeline_instance.name
    }
    return context

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
import traceback

from gcloud.contrib.operate_record.models import TemplateOperateRecord, TaskOperateRecord


logger = logging.getLogger("root")


def record_template_operation_helper(operator, operate_type, template_id, operate_source, project_id=-1):
    try:
        TemplateOperateRecord.objects.create(
            operator=operator,
            operate_type=operate_type,
            instance_id=template_id,
            operate_source=operate_source,
            project_id=project_id,
        )
    except Exception:
        logger.error("record operate failed, error:{}".format(traceback.format_exc()))


def record_task_operation_helper(
    operator, operate_type, taskflow_id, operate_source, project_id=-1, node_id="", extra_info=""
):
    try:
        TaskOperateRecord.objects.create(
            operator=operator,
            operate_type=operate_type,
            instance_id=taskflow_id,
            operate_source=operate_source,
            project_id=project_id,
            node_id=node_id,
            extra_info=extra_info,
        )
    except Exception:
        logger.error("record operate failed, error:{}".format(traceback.format_exc()))

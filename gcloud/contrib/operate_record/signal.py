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

from django.dispatch import Signal, receiver

from gcloud.contrib.operate_record.helpers import record_template_operation_helper, record_task_operation_helper
from gcloud.contrib.operate_record.constants import RecordType

# signal_sender: RecordType
operate_record_signal = Signal(
    ["operator", "operate_type", "operate_source", "instance_id", "project_id", "node_id", "extra_info"]
)


@receiver(operate_record_signal, sender=RecordType.template.name)
def record_template_handler(operator, operate_type, operate_source, instance_id, project_id, **kwargs):
    record_template_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        template_id=instance_id,
        project_id=project_id,
    )


@receiver(operate_record_signal, sender=RecordType.common_template.name)
def record_common_template_handler(operator, operate_type, operate_source, instance_id, **kwargs):
    record_template_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        template_id=instance_id,
    )


@receiver(operate_record_signal, sender=RecordType.task.name)
def record_task_handler(operator, operate_type, operate_source, instance_id, project_id, extra_info, **kwargs):
    record_task_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        taskflow_id=instance_id,
        project_id=project_id,
        extra_info=extra_info,
    )


@receiver(operate_record_signal, sender=RecordType.task_node.name)
def record_task_node_handler(operator, operate_type, operate_source, instance_id, project_id, node_id, **kwargs):
    record_task_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        taskflow_id=instance_id,
        project_id=project_id,
        node_id=node_id,
    )

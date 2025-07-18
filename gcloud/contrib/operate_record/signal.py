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

from gcloud.contrib.operate_record.constants import RecordType
from gcloud.contrib.operate_record.helpers import record_task_operation_helper, record_template_operation_helper

# signal_sender: RecordType
# ["operator", "operate_type", "operate_source", "instance_id", "project_id", "node_id", "extra_info"]
operate_record_signal = Signal()


@receiver(operate_record_signal, sender=RecordType.template)
def record_template_handler(operator, operate_type, operate_source, instance_id, project_id, **kwargs):
    record_template_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        template_id=instance_id,
        project_id=project_id,
    )


@receiver(operate_record_signal, sender=RecordType.common_template)
def record_common_template_handler(operator, operate_type, operate_source, instance_id, **kwargs):
    record_template_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        template_id=instance_id,
    )


@receiver(operate_record_signal, sender=RecordType.task)
def record_task_handler(operator, operate_type, operate_source, instance_id, project_id, extra_info="", **kwargs):
    record_task_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        taskflow_id=instance_id,
        project_id=project_id,
        extra_info=extra_info,
    )


@receiver(operate_record_signal, sender=RecordType.task_node)
def record_task_node_handler(operator, operate_type, operate_source, instance_id, project_id, node_id, **kwargs):
    record_task_operation_helper(
        operator=operator,
        operate_type=operate_type,
        operate_source=operate_source,
        taskflow_id=instance_id,
        project_id=project_id,
        node_id=node_id,
    )

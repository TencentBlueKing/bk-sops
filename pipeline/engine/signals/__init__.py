# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.dispatch import Signal

pipeline_ready = Signal(providing_args=['process_id'])
child_process_ready = Signal(providing_args=['child_id'])
process_ready = Signal(providing_args=['parent_id', 'current_node_id', 'call_from_child'])
batch_process_ready = Signal(providing_args=['process_id_list', 'pipeline_id'])
wake_from_schedule = Signal(providing_args=['process_id, activity_id'])
schedule_ready = Signal(providing_args=['schedule_id', 'countdown', 'process_id'])
process_unfreeze = Signal(providing_args=['process_id'])
# activity failed signal
activity_failed = Signal(providing_args=['pipeline_id', 'pipeline_activity_id'])

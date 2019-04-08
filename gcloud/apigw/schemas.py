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

from gcloud.core.constant import TASK_FLOW, PERIOD_TASK_NAME_MAX_LENGTH

APIGW_CREATE_TASK_PARAMS = {
    'type': 'object',
    'required': ['name'],
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': PERIOD_TASK_NAME_MAX_LENGTH,
        },
        'flow_type': {
            'type': 'string',
            'enum': TASK_FLOW.keys()
        },
        'constants': {
            'type': 'object',
        },
        'exclude_task_nodes_id': {
            'type': 'array',
        }
    }
}

APIGW_CREATE_PERIODIC_TASK_PARAMS = {
    'type': 'object',
    'required': ['name', 'cron'],
    'properties': {
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': PERIOD_TASK_NAME_MAX_LENGTH,
        },
        'cron': {
            'type': 'object'
        },
        'exclude_task_nodes_id': {
            'type': 'array',
        },
        'constants': {
            'type': 'object',
        },
    }
}

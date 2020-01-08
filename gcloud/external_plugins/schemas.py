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

import copy

from gcloud.external_plugins.models import source_cls_factory

NAME_MAX_LENGTH = 50
NAME_PATTERN = r'^([a-zA-Z0-9_]+)$'


ADD_SOURCE_SCHEMA = {
    'type': 'object',
    'required': ['type', 'name', 'details'],
    'properties': {
        'id': {
            'type': 'integer',
        },
        'type': {
            'type': 'string', 'enum': source_cls_factory.keys()
        },
        'name': {
            'type': 'string',
            'minLength': 1,
            'maxLength': NAME_MAX_LENGTH,
            'pattern': NAME_PATTERN,
        },
        'packages': {
            'type': 'object',
            'patternProperties': {
                NAME_PATTERN: {
                    'type': 'object',
                    'required': ['version', 'modules'],
                    'properties': {
                        'version': {
                            'type': 'string'
                        },
                        'modules': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        },
                    },
                }
            }
        },
        'details': {
            'type': 'object',
            'oneOf': [
                {
                    'type': 'object',
                    'required': ['repo_address', 'repo_raw_address', 'branch'],
                    'properties': {
                        'repo_address': {
                            'type': 'string'
                        },
                        'repo_raw_address': {
                            'type': 'string'
                        },
                        'branch': {
                            'type': 'string'
                        },
                    }
                },
                {
                    'type': 'object',
                    'required': ['service_address', 'bucket', 'access_key', 'secret_key'],
                    'properties': {
                        'service_address': {
                            'type': 'string'
                        },
                        'bucket': {
                            'type': 'string'
                        },
                        'access_key': {
                            'type': 'string'
                        },
                        'secret_key': {
                            'type': 'string'
                        },
                    }
                },
                {
                    'type': 'object',
                    'required': ['path'],
                    'properties': {
                        'path': {
                            'type': 'string'
                        },
                    }
                }
            ]
        }
    }
}

UPDATE_SOURCE_SCHEMA = copy.deepcopy(ADD_SOURCE_SCHEMA)
UPDATE_SOURCE_SCHEMA['required'] = ['type', 'details']

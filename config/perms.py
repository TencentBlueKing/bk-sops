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

from gcloud.core.permissions import project_resource
from gcloud.commons.template.permissions import common_template_resource
from gcloud.tasktmpl3.permissions import task_template_resource
from gcloud.taskflow3.permissions import taskflow_resource
from gcloud.contrib.appmaker.permissions import mini_app_resource
from gcloud.periodictask.permissions import periodic_task_resource

bk_iam_perm_templates = [
    {
        'name': u"运维",
        'id': 'operation',
        'desc': '',
        'resource_actions': [
            {
                'resource': project_resource,
                'actions': [
                    project_resource.actions.create,
                    project_resource.actions.view,
                    project_resource.actions.edit,
                    project_resource.actions.create_template,
                    project_resource.actions.use_common_template,
                ]
            },
            {
                'resource': common_template_resource,
                'actions': [
                    common_template_resource.actions.view,
                    common_template_resource.actions.create_task,
                ]
            },
            {
                'resource': task_template_resource,
                'actions': [
                    task_template_resource.actions.view,
                    task_template_resource.actions.edit,
                    task_template_resource.actions.delete,
                    task_template_resource.actions.create_task,
                    task_template_resource.actions.create_mini_app,
                    task_template_resource.actions.create_periodic_task
                ]
            },
            {
                'resource': taskflow_resource,
                'actions': [
                    taskflow_resource.actions.view,
                    taskflow_resource.actions.edit,
                    taskflow_resource.actions.operate,
                    taskflow_resource.actions.claim,
                    taskflow_resource.actions.delete,
                    taskflow_resource.actions.clone
                ]
            },
            {
                'resource': mini_app_resource,
                'actions': [
                    mini_app_resource.actions.view,
                    mini_app_resource.actions.edit,
                    mini_app_resource.actions.delete,
                    mini_app_resource.actions.create_task
                ]
            },
            {
                'resource': periodic_task_resource,
                'actions': [
                    periodic_task_resource.actions.view,
                    periodic_task_resource.actions.edit,
                    periodic_task_resource.actions.delete
                ]
            }
        ]
    },
    {
        'name': u"产品",
        'id': 'product_manager',
        'desc': '',
        'resource_actions': [
            {
                'resource': project_resource,
                'actions': [
                    project_resource.actions.view,
                    project_resource.actions.create_template,
                ]
            },
            {
                'resource': task_template_resource,
                'actions': [
                    task_template_resource.actions.view,
                    task_template_resource.actions.edit,
                    task_template_resource.actions.create_task,
                ]
            },
            {
                'resource': mini_app_resource,
                'actions': [
                    mini_app_resource.actions.view,
                    mini_app_resource.actions.create_task
                ]
            },
            {
                'resource': periodic_task_resource,
                'actions': [
                    periodic_task_resource.actions.view,
                ]
            }
        ]
    },
    {
        'name': u"测试",
        'id': 'tester',
        'desc': '',
        'resource_actions': [
            {
                'resource': project_resource,
                'actions': [
                    project_resource.actions.view,
                    project_resource.actions.create_template,
                ]
            },
            {
                'resource': task_template_resource,
                'actions': [
                    task_template_resource.actions.view,
                    task_template_resource.actions.edit,
                    task_template_resource.actions.create_task,
                ]
            },
            {
                'resource': mini_app_resource,
                'actions': [
                    mini_app_resource.actions.view,
                    mini_app_resource.actions.create_task
                ]
            },
            {
                'resource': periodic_task_resource,
                'actions': [
                    periodic_task_resource.actions.view,
                ]
            }
        ]
    },
    {
        'name': u"开发",
        'id': 'developer',
        'desc': '',
        'resource_actions': [
            {
                'resource': project_resource,
                'actions': [
                    project_resource.actions.view,
                    project_resource.actions.create_template,
                ]
            },
            {
                'resource': task_template_resource,
                'actions': [
                    task_template_resource.actions.view,
                    task_template_resource.actions.edit,
                    task_template_resource.actions.create_task,
                ]
            },
            {
                'resource': mini_app_resource,
                'actions': [
                    mini_app_resource.actions.view,
                    mini_app_resource.actions.create_task
                ]
            },
            {
                'resource': periodic_task_resource,
                'actions': [
                    periodic_task_resource.actions.view,
                ]
            }
        ]
    },
    {
        'name': u'职能化',
        'id': 'functor',
        'desc': '',
        'resource_actions': [
            {
                'resource': project_resource,
                'actions': [
                    project_resource.actions.view,
                ]
            },
            {
                'resource': task_template_resource,
                'actions': [
                    task_template_resource.actions.view,
                ]
            },
        ]
    }
]

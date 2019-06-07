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

from django.utils.translation import ugettext_lazy as _

# from gcloud.core.models import Project
# from gcloud.tasktmpl3.models import TaskTemplate

from .resources import Resource


project_resource = Resource(
    rtype='project',
    name=_(u"项目"),
    actions=[
        {
            'action_id': 'create',
            'action_name': _(u"创建"),
            'is_related_resource': False
        },
        {
            'action_id': 'view',
            'action_name': _(u"查看"),
            'is_related_resource': True
        },
        {
            'action_id': 'edit',
            'action_name': _(u"编辑"),
            'is_related_resource': True
        },
        {
            'action_id': 'disable',
            'action_name': _(u"停用"),
            'is_related_resource': True
        },
        {
            'action_id': 'create_template',
            'action_name': _(u"新建流程"),
            'is_related_resource': True
        },
        {
            'action_id': 'use_common_template',
            'action_name': _(u"创建"),
            'is_related_resource': True
        }
    ]
)

template_rsource = Resource(
    rtype='flow-template',
    name=_(u"流程模板"),
    actions=[
        {
            'action_id': 'view',
            'action_name': _(u"查看"),
            'is_related_resource': True
        },
        {
            'action_id': 'edit',
            'action_name': _(u"编辑"),
            'is_related_resource': True
        },
        {
            'action_id': 'delete',
            'action_name': _(u"删除"),
            'is_related_resource': True
        },
        {
            'action_id': 'create_task',
            'action_name': _(u"新建任务"),
            'is_related_resource': True
        },
        {
            'action_id': 'create_mini_app',
            'action_name': _(u"新建轻应用"),
            'is_related_resource': True
        },
        {
            'action_id': 'create_periodic_task',
            'action_name': _(u"新建周期任务"),
            'is_related_resource': True
        }
    ],
    parent=project_resource,
)

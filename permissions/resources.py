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

from auth_backend.resources.base import Action, NeverInitiateResource
from auth_backend.backends.bkiam import BkIAMBackend
from auth_backend.resources.django import DjangoModelResource
from auth_backend.resources.inspect import FixedCreatorFieldInspect

from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.models import CommonTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.periodictask.models import PeriodicTask

SCOPE_TYPE = 'system'
SCOPE_ID = 'bk_sops'
SCOPE_NAME = _(u"标准运维")

# no parent resource
project_resource = DjangoModelResource(
    rtype='project',
    name=_(u"项目"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='create', name=_(u"创建"), is_instance_related=False),
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='create_template', name=_(u"新建流程"), is_instance_related=True),
        Action(id='use_common_template', name=_(u"使用公共流程"), is_instance_related=True),
    ],
    operations=[
        {
            'operate_id': 'create',
            'actions_id': ['create']
        },
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'create_template',
            'actions_id': ['view', 'create_template']
        },
        {
            'operate_id': 'use_common_template',
            'actions_id': ['view', 'use_common_template']
        }
    ],
    resource_cls=Project,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f=None))

# has parent resource
task_template_resource = DjangoModelResource(
    rtype='flow-template',
    name=_(u"流程模板"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='delete', name=_(u"删除"), is_instance_related=True),
        Action(id='create_task', name=_(u"新建任务"), is_instance_related=True),
        Action(id='create_mini_app', name=_(u"新建轻应用"), is_instance_related=True),
        Action(id='create_periodic_task', name=_(u"新建周期任务"), is_instance_related=True),
    ],
    operations=[
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'delete',
            'actions_id': ['view', 'delete']
        },
        {
            'operate_id': 'create_task',
            'actions_id': ['view', 'create_task']
        },
        {
            'operate_id': 'create_periodic_task',
            'actions_id': ['view', 'create_periodic_task']
        },
        {
            'operate_id': 'create_mini_app',
            'actions_id': ['view', 'create_mini_app']
        },
        {
            'operate_id': 'clone',
            'actions_id': ['view']
        },
        {
            'operate_id': 'export',
            'actions_id': ['view']
        }
    ],
    parent=project_resource,
    resource_cls=TaskTemplate,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator_name',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f='project'))

common_template_resource = DjangoModelResource(
    rtype='common-template',
    name=_(u"公共流程"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='create', name=_(u"新建"), is_instance_related=False),
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='delete', name=_(u"删除"), is_instance_related=True),
        Action(id='create_task', name=_(u"新建任务"), is_instance_related=True)
    ],
    operations=[
        {
            'operate_id': 'create',
            'actions_id': ['create']
        },
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'delete',
            'actions_id': ['view', 'delete']
        },
        {
            'operate_id': 'create_task',
            'actions_id': ['view', 'create_task']
        }
    ],
    parent=project_resource,
    resource_cls=CommonTemplate,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator_name',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f='project'))

taskflow_resource = DjangoModelResource(
    rtype='flow-instance',
    name=_(u"流程实例"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='operate', name=_(u"控制"), is_instance_related=True),
        Action(id='claim', name=_(u"认领"), is_instance_related=True),
        Action(id='delete', name=_(u"删除"), is_instance_related=True),
        Action(id='clone', name=_(u"克隆"), is_instance_related=True)
    ],
    operations=[
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'operate',
            'actions_id': ['view', 'operate']
        },
        {
            'operate_id': 'claim',
            'actions_id': ['view', 'claim']
        },
        {
            'operate_id': 'delete',
            'actions_id': ['view', 'delete']
        },
        {
            'operate_id': 'clone',
            'actions_id': ['view', 'clone']
        }
    ],
    parent=project_resource,
    resource_cls=TaskFlowInstance,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f='project'))

mini_app_resource = DjangoModelResource(
    rtype='mini-app',
    name=_(u"轻应用"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='delete', name=_(u"删除"), is_instance_related=True),
        Action(id='create_task', name=_(u"新建任务"), is_instance_related=True)
    ],
    operations=[
        {
            'operate_id': 'view',
            'actions_id': ['view'],
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'delete',
            'actions_id': ['view', 'delete']
        },
        {
            'operate_id': 'create_task',
            'actions_id': ['view', 'create_task']
        }
    ],
    resource_cls=AppMaker,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f='project'))

periodic_task_resource = DjangoModelResource(
    rtype='periodic-task',
    name=_(u"周期任务"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='delete', name=_(u"删除"), is_instance_related=True)
    ],
    operations=[
        {
            'operate_id': 'view',
            'actions_id': ['view'],
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        },
        {
            'operate_id': 'delete',
            'actions_id': ['view', 'delete']
        },
    ],
    resource_cls=PeriodicTask,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f='project'))

# no instance resource
statistics_resource = NeverInitiateResource(
    rtype='statistics',
    name=_(u"统计数据"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[Action(id='view', name=_(u"查看"), is_instance_related=False)],
    backend=BkIAMBackend())

audit_data_resource = NeverInitiateResource(
    rtype='audit-data',
    name=_(u"审计数据"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[Action(id='view', name=_(u"查看"), is_instance_related=False)],
    backend=BkIAMBackend())

admin_operate_resource = NeverInitiateResource(
    rtype='admin-operate',
    name=_(u"后台管理"),
    scope_type=SCOPE_TYPE,
    scope_id=SCOPE_ID,
    scope_name=SCOPE_NAME,
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=False),
        Action(id='edit', name=_(u"编辑"), is_instance_related=False)
    ],
    backend=BkIAMBackend())

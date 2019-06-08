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

from auth_backend.resources.base import Action
from auth_backend.backends.bkiam import BkIAMBackend
from auth_backend.resources.django import DjangoModelResource
from auth_backend.resources.inspect import FixedCreatorFieldInspect

from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate

import logging

logger = logging.getLogger('auth')
c_handler = logging.StreamHandler()
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)
logger.setLevel(logging.DEBUG)

project_resource = DjangoModelResource(
    rtype='project',
    name=_(u"项目"),
    scope_type='system',
    scope_id='bk_sops',
    actions=[
        Action(id='create', name=_(u"创建"), is_instance_related=False),
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='disable', name=_(u"停用"), is_instance_related=True),
        Action(id='create_template', name=_(u"新建流程"), is_instance_related=True),
        Action(id='use_common_template', name=_(u"使用公共流程"), is_instance_related=True),
    ],
    resource_cls=Project,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f=None))

task_template_resource = DjangoModelResource(
    rtype='flow-template',
    name=_(u"流程模板"),
    scope_type='system',
    scope_id='bk_sops',
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=True),
        Action(id='edit', name=_(u"编辑"), is_instance_related=True),
        Action(id='delete', name=_(u"删除"), is_instance_related=True),
        Action(id='create_task', name=_(u"新建任务"), is_instance_related=True),
        Action(id='create_mini_app', name=_(u"新建轻应用"), is_instance_related=True),
        Action(id='create_periodic_task', name=_(u"新建周期任务"), is_instance_related=True),
    ],
    parent=project_resource,
    resource_cls=TaskTemplate,
    backend=BkIAMBackend(),
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f='project'))

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


from django.utils.translation import ugettext_lazy as _
from pipeline.component_framework.component import Component

from gcloud.conf import settings

__group_name__ = _("节点管理(Nodeman)")

from pipeline_plugins.components.collections.sites.open.nodeman.create_task.v4_0 import (
    NodemanCreateTaskService as NodemanCreateTaskV4Service,
)

VERSION = "v7.0"


class NodemanCreateTaskService(NodemanCreateTaskV4Service):
    pass


class NodemanCreateTaskComponent(Component):
    name = _("新建任务")
    code = "nodeman_create_task"
    bound_service = NodemanCreateTaskService
    form = "%scomponents/atoms/nodeman/create_task/v7_0.js" % settings.STATIC_URL
    version = VERSION
    desc = _("v7.0版本 支持选择寻址方式 \n" "注意：bk_apigateway版本>=1.12.17")

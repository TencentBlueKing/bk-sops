# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from gcloud.conf import settings

__group_name__ = _("蓝鲸服务(BK)")


class DisplayService(Service):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("展示内容"), key="bk_display_message", type="string", schema=StringItemSchema(description=_("展示内容"))
            ),
        ]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        return True


class DisplayComponent(Component):
    name = _("消息展示")
    code = "bk_display"
    bound_service = DisplayService
    form = "%scomponents/atoms/bk/display/v1_0.js" % settings.STATIC_URL
    version = "1.0"
    desc = _("本插件为仅用于消息展示的空节点")

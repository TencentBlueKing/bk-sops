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
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings

from ..base import NodeManBaseService

__group_name__ = _("节点管理(Nodeman)")

from ..ip_v6_base import NodemanPluginIPMixin

INSTALL_TYPE = ["MAIN_INSTALL_PLUGIN"]


class NodemanPluginOperateService(NodeManBaseService, NodemanPluginIPMixin):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="bk_biz_id",
                type="int",
                schema=IntItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("插件操作信息"),
                key="nodeman_plugin_operate",
                type="object",
                schema=ObjectItemSchema(
                    description=_("插件操作内容"),
                    property_schemas={
                        "nodeman_op_type": StringItemSchema(description=_("插件操作类型")),
                        "nodeman_plugin": StringItemSchema(description=_("插件名称")),
                        "nodeman_plugin_version": StringItemSchema(description=_("插件版本")),
                        "install_config": ArrayItemSchema(
                            description=_("安装操作参数"),
                            item_schema=StringItemSchema(
                                description=_("安装选项，nodeman_op_type值为MAIN_INSTALL_PLUGIN时可填"),
                                enum=["keep_config", "no_restart"],
                            ),
                        ),
                    },
                ),
            ),
            self.InputItem(
                name=_("主机信息"),
                key="nodeman_host_info",
                type="object",
                schema=ObjectItemSchema(
                    description=_("主机信息内容"),
                    property_schemas={
                        "nodeman_bk_cloud_id": IntItemSchema(description=_("主机所在管控区域 ID")),
                        "nodeman_host_ip": StringItemSchema(
                            description=_("主机ip,多个以英文','分隔，nodeman_host_input_type值为host_ip时必填")
                        ),
                    },
                ),
            ),
        ]

    def get_input_type(self, data):
        return "host_ip"

    def outputs_format(self):
        outputs_format = super(NodemanPluginOperateService, self).outputs_format()
        return outputs_format

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        bk_biz_id = data.inputs.biz_cc_id

        bk_cloud_id = data.inputs.nodeman_bk_cloud_id
        ip_str = data.inputs.nodeman_host_ip
        host_result = self.get_host_list(executor, self.logger, bk_biz_id, ip_str, bk_cloud_id)
        if not host_result["result"]:
            data.set_outputs(
                "ex_data", _("获取bk_host_id失败:{},请确认管控区域是否正确".format(host_result["message"]))
            )
            return False
        host = [int(host_id) for host_id in host_result["data"]]

        return self.execute_operate(data, host, executor, bk_biz_id)


class NodemanPluginOperateComponent(Component):
    name = _("插件操作")
    code = "nodeman_plugin_operate"
    bound_service = NodemanPluginOperateService
    form = "%scomponents/atoms/nodeman/plugin_operate/v2_0.js" % settings.STATIC_URL
    version = "v2.0"
    desc = _("移除填写方式，只支持主机IP方式\n 管控区域ID、主机IP支持 设置为变量 \n 管控区域ID 支持AllowCreate \n")

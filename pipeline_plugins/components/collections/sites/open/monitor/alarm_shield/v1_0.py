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

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component
from pipeline.core.flow.io import ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from packages.bkapi.bk_monitor.shortcuts import get_client_by_username
from pipeline_plugins.components.collections.sites.open.monitor.base import MonitorBaseService
from pipeline_plugins.components.utils.sites.open.utils import get_module_id_list_by_name
from pipeline_plugins.variables.utils import (
    get_list_by_selected_names,
    get_service_template_list,
    get_service_template_list_by_names,
    get_set_list,
)

SCOPE = {"business": "bk_alarm_shield_business", "IP": "bk_alarm_shield_IP", "node": "bk_alarm_shield_node"}

ALL_SELECTED_STR = "all"

__group_name__ = _("监控平台(Monitor)")


class MonitorAlarmShieldService(MonitorBaseService):
    def inputs_format(self):
        return [
            self.InputItem(
                name=_("屏蔽范围类型"),
                key="bk_alarm_shield_info",
                type="object",
                schema=ObjectItemSchema(description=_("屏蔽范围类型"), property_schemas={}),
            ),
            self.InputItem(
                name=_("策略 ID"),
                key="bk_alarm_shield_target",
                type="string",
                schema=StringItemSchema(description=_("需要执行屏蔽的指标")),
            ),
            self.InputItem(
                name=_("屏蔽开始时间"),
                key="bk_alarm_shield_begin_time",
                type="string",
                schema=StringItemSchema(description=_("开始屏蔽的时间")),
            ),
            self.InputItem(
                name=_("屏蔽结束时间"),
                key="bk_alarm_shield_end_time",
                type="string",
                schema=StringItemSchema(description=_("结束屏蔽的时间")),
            ),
        ]

    def execute(self, data, parent_data):
        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(username=executor, stage=settings.BK_APIGW_STAGE_NAME)
        combine = data.get_one_of_inputs("bk_alarm_shield_info")
        scope_type = combine.get("bk_alarm_shield_scope")
        scope_value = combine.get(SCOPE[scope_type])
        target = data.get_one_of_inputs("bk_alarm_shield_target")
        begin_time = data.get_one_of_inputs("bk_alarm_shield_begin_time")
        end_time = data.get_one_of_inputs("bk_alarm_shield_end_time")

        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        request_body = self.get_request_body(
            bk_biz_id, begin_time, end_time, scope_type, scope_value, executor, tenant_id
        )
        if "all" not in target:
            request_body["dimension_config"].update({"metric_id": target})

        result_flag = self.send_request(tenant_id, request_body, data, client)

        return result_flag

    def get_dimension_config(self, shied_type, shied_value, bk_biz_id, username, tenant_id):
        dimension_map = {
            "business": self.get_biz_dimension,
            "IP": self.get_ip_dimension,
            "node": self.get_node_dimension,
        }
        return dimension_map[shied_type](shied_value, bk_biz_id, username, tenant_id)

    def get_request_body(
        self, bk_biz_id, begin_time, end_time, shied_type, shied_value, username, tenant_id
    ):
        dimension_config = self.get_dimension_config(
            shied_type, shied_value, bk_biz_id, username, tenant_id
        )
        request_body = self.build_request_body(
            begin_time=begin_time,
            bk_biz_id=bk_biz_id,
            shied_type=shied_type,
            dimension_config=dimension_config,
            end_time=end_time,
        )
        return request_body

    def get_ip_dimension(self, scope_value, bk_biz_id, username, tenant_id):
        ip_dimension = super(MonitorAlarmShieldService, self).get_ip_dimension_config(
            tenant_id, scope_value, bk_biz_id, username
        )
        return ip_dimension

    @staticmethod
    def get_biz_dimension(scope_value, bk_biz_id, username, tenant_id):
        return {"scope_type": "biz"}

    @staticmethod
    def get_node_dimension(scope_value, bk_biz_id, username, tenant_id):
        bk_set_method = scope_value["bk_set_method"]
        if bk_set_method == "select":
            bk_set_value = scope_value["bk_set_select"]
        else:
            bk_set_value = scope_value["bk_set_text"]

        bk_module_method = scope_value["bk_module_method"]
        if bk_module_method == "select":
            bk_module_value = scope_value["bk_module_select"]
        else:
            bk_module_value = scope_value["bk_module_text"]

        # 获取全部集群列表
        set_list = get_set_list(tenant_id, username, bk_biz_id)

        # 集群全选，筛选条件不为空则调接口获取集群id列表
        if ALL_SELECTED_STR not in bk_set_value:
            selected_set_names = bk_set_value
            # 根据选中的集群名称获取选中的集群列表
            set_list = get_list_by_selected_names(selected_set_names, set_list)
        # 获取全部服务模板列表
        service_template_list = get_service_template_list(tenant_id, username, bk_biz_id)
        # 服务模板全选，则调接口获取服务模板列表
        if ALL_SELECTED_STR not in bk_module_value:
            selected_service_template_names = bk_module_value
            # 通过选中的或输入的集群模板获取集群模板列表
            service_template_list = get_service_template_list_by_names(
                selected_service_template_names, service_template_list
            )
        # 获取模块id列表
        module_ids = get_module_id_list_by_name(tenant_id, bk_biz_id, username, set_list, service_template_list)
        target = [{"bk_obj_id": "module", "bk_inst_id": module_id["bk_module_id"]} for module_id in module_ids]

        return {"scope_type": "node", "target": target}


class MonitorAlarmShieldComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按范围)")
    code = "monitor_alarm_shield"
    bound_service = MonitorAlarmShieldService
    form = "{static_url}components/atoms/monitor/alarm_shield/v1_0.js".format(static_url=settings.STATIC_URL)
    version = "1.0"
    desc = _('注意： 1.屏蔽方案选择"自定义监控"时，屏蔽范围CC大区和集群必须选择"all"')

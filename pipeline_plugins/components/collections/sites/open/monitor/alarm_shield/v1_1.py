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
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from gcloud.conf.default_settings import ESB_GET_OLD_CLIENT_BY_USER as get_client_by_user
from gcloud.conf import settings
from gcloud.utils import cmdb
from gcloud.core.models import Business
from gcloud.utils.handlers import handle_api_error

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.utils.sites.open.choose_time_tools import choose_time
from pipeline_plugins.components.utils.sites.open.utils import get_module_id_list_by_name
from pipeline_plugins.variables.utils import (
    get_set_list,
    get_list_by_selected_names,
    get_service_template_list,
    get_service_template_list_by_names,
)

__group_name__ = _("监控平台(Monitor)")

monitor_handle_api_error = partial(handle_api_error, __group_name__)

SCOPE = {"business": "bk_alarm_shield_business", "IP": "bk_alarm_shield_IP", "node": "bk_alarm_shield_node"}

ALL_SELECTED_STR = "all"


class MonitorAlarmShieldService(Service):
    def inputs_format(self):
        return (
            [
                self.InputItem(
                    name=_("屏蔽范围类型"),
                    key="bk_alarm_shield_info",
                    type="object",
                    schema=ObjectItemSchema(description=_(u"屏蔽范围类型"), property_schemas={}),
                ),
                self.InputItem(
                    name=_("策略 ID"),
                    key="bk_alarm_shield_target",
                    type="string",
                    schema=StringItemSchema(description=_("需要执行屏蔽的指标")),
                ),
                self.InputItem(
                    name=_("时间选择"),
                    key="bk_alarm_time_type",
                    type="string",
                    schema=StringItemSchema(description=_("开始屏蔽的时间")),
                ),
                self.InputItem(
                    name=_("屏蔽开始时间"),
                    key="bk_alarm_shield_begin_time",
                    type="string",
                    schema=StringItemSchema(description=_("开始屏蔽的时间")),
                ),
                self.InputItem(
                    name=_("屏蔽结束时间"),
                    key="bk_alarm_end_time",
                    type="string",
                    schema=StringItemSchema(description=_("结束屏蔽的时间")),
                ),
                self.InputItem(
                    name=_("屏蔽持续时间"),
                    key="bk_alarm_shield_duration",
                    type="string",
                    schema=StringItemSchema(description=_("屏蔽持续的时间")),
                ),
            ],
        )

    def execute(self, data, parent_data):
        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        combine = data.get_one_of_inputs("bk_alarm_shield_info")
        scope_type = combine.get("bk_alarm_shield_scope")
        scope_value = combine.get(SCOPE[scope_type])
        target = data.get_one_of_inputs("bk_alarm_shield_target")
        begin_time = data.get_one_of_inputs("bk_alarm_shield_begin_time")
        end_time = data.get_one_of_inputs("bk_alarm_shield_end_time")
        time_type = int(data.get_one_of_inputs("bk_alarm_time_type"))
        shield_duration = data.get_one_of_inputs("bk_alarm_shield_duration")
        try:
            begin_time, end_time = choose_time(time_type, begin_time, end_time, shield_duration)
        except ValueError:
            return False

        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        supplier_account = supplier_account_for_business(bk_biz_id)

        request_body = self.get_request_body(
            bk_biz_id, begin_time, end_time, scope_type, scope_value, executor, supplier_account
        )
        if "all" not in target:
            request_body["dimension_config"].update({"metric_id": target})

        result_flag = self.send_request(request_body, data, client)

        return result_flag

    def get_dimension_config(self, shied_type, shied_value, bk_biz_id, username, bk_supplier_account):
        dimension_map = {
            "business": self.get_biz_dimension,
            "IP": self.get_ip_dimension,
            "node": self.get_node_dimension,
        }
        return dimension_map[shied_type](shied_value, bk_biz_id, username, bk_supplier_account)

    def get_request_body(self, bk_biz_id, begin_time, end_time, shied_type, shied_value, username, bk_supplier_account):
        category_map = {"business": "scope", "IP": "scope", "node": "scope", "strategy": "strategy"}
        dimension_config = self.get_dimension_config(shied_type, shied_value, bk_biz_id, username, bk_supplier_account)
        request_body = {
            "begin_time": begin_time,
            "bk_biz_id": bk_biz_id,
            "category": category_map[shied_type],
            "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
            "description": "shield by bk_sops",
            "dimension_config": dimension_config,
            "end_time": end_time,
            "notice_config": {},
            "shield_notice": False,
            "source": settings.APP_ID,
        }
        return request_body

    def send_request(self, request_body, data, client):
        response = client.monitor.create_shield(request_body)
        if not response["result"]:
            message = monitor_handle_api_error("monitor.create_shield", request_body, response)
            self.logger.error(message)
            shield_id = ""
            ret_flag = False
        else:
            shield_id = response["data"]["id"]
            ret_flag = True
            message = response["message"]
        data.set_outputs("shield_id", shield_id)
        data.set_outputs("message", message)
        return ret_flag

    def get_ip_dimension(self, scope_value, bk_biz_id, username, bk_supplier_account):
        ip_list = scope_value.split(",")
        hosts = cmdb.get_business_host(
            username=username,
            bk_biz_id=bk_biz_id,
            supplier_account=Business.objects.supplier_account_for_business(bk_biz_id),
            host_fields=["bk_host_id", "bk_cloud_id", "bk_host_innerip"],
            ip_list=ip_list,
        )
        if not hosts:
            raise Exception("cmdb.get_business_host return empty")

        target = []
        for host in hosts:
            target.append({"ip": host["bk_host_innerip"], "bk_cloud_id": host["bk_cloud_id"]})

        return {"scope_type": "ip", "target": target}

    @staticmethod
    def get_biz_dimension(scope_value, bk_biz_id, username, bk_supplier_account):
        return {"scope_type": "biz"}

    @staticmethod
    def get_node_dimension(scope_value, bk_biz_id, username, bk_supplier_account):
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
        set_list = get_set_list(username, bk_biz_id, bk_supplier_account)

        # 集群全选，筛选条件不为空则调接口获取集群id列表
        if ALL_SELECTED_STR not in bk_set_value:
            selected_set_names = bk_set_value
            # 根据选中的集群名称获取选中的集群列表
            set_list = get_list_by_selected_names(selected_set_names, set_list)
        # 获取全部服务模板列表
        service_template_list = get_service_template_list(username, bk_biz_id, bk_supplier_account)
        # 服务模板全选，则调接口获取服务模板列表
        if ALL_SELECTED_STR not in bk_module_value:
            selected_service_template_names = bk_module_value
            # 通过选中的或输入的集群模板获取集群模板列表
            service_template_list = get_service_template_list_by_names(
                selected_service_template_names, service_template_list
            )
        # 获取模块id列表
        module_ids = get_module_id_list_by_name(bk_biz_id, username, set_list, service_template_list)
        target = [{"bk_obj_id": "module", "bk_inst_id": module_id} for module_id in module_ids]

        return {"scope_type": "node", "target": target}

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("屏蔽Id"), key="shield_id", type="string", schema=StringItemSchema(description=_("创建的告警屏蔽 ID"))
            ),
            self.OutputItem(
                name=_("详情"), key="message", type="string", schema=StringItemSchema(description=_("创建的告警屏蔽详情"))
            ),
        ]


class MonitorAlarmShieldComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按范围)")
    code = "monitor_alarm_shield"
    bound_service = MonitorAlarmShieldService
    form = "{static_url}components/atoms/monitor/alarm_shield/v1_1.js".format(static_url=settings.STATIC_URL)
    version = "1.1"
    desc = _('注意： 1.屏蔽方案选择"自定义监控"时，屏蔽范围CC大区和集群必须选择"all"')

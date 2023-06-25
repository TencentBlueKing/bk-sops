# -*- coding: utf-8 -*-
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from pipeline.core.flow.io import ObjectItemSchema, StringItemSchema

from api.collections.monitor import BKMonitorClient
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.monitor.base import (
    MonitorBaseService,
)
from pipeline_plugins.components.utils.sites.open.choose_time_tools import choose_time
from pipeline_plugins.components.utils.sites.open.utils import (
    get_module_id_list_by_name,
)
from pipeline_plugins.variables.utils import (
    get_list_by_selected_names,
    get_service_template_list,
    get_service_template_list_by_names,
    get_set_list,
)

ALL_SELECTED_STR = "all"


class MonitorAlarmShieldServiceBase(MonitorBaseService):
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
        ]

    def get_scope_value(self, bk_biz_id, scope_type, combine):
        scope = {"business": "bk_alarm_shield_business", "IP": "bk_alarm_shield_IP", "node": "bk_alarm_shield_node"}
        scope_value = combine.get(scope[scope_type])
        return scope_value

    def execute(self, data, parent_data):
        bk_biz_id = parent_data.get_one_of_inputs("biz_cc_id")
        executor = parent_data.get_one_of_inputs("executor")
        client = BKMonitorClient(username=executor)
        combine = data.get_one_of_inputs("bk_alarm_shield_info")
        scope_type = combine.get("bk_alarm_shield_scope")
        scope_value = self.get_scope_value(bk_biz_id, scope_type, combine)
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
        dimension_config = self.get_dimension_config(shied_type, shied_value, bk_biz_id, username, bk_supplier_account)
        request_body = self.build_request_body(
            begin_time=begin_time,
            bk_biz_id=bk_biz_id,
            shied_type=shied_type,
            dimension_config=dimension_config,
            end_time=end_time,
        )
        return request_body

    def get_ip_dimension(self, scope_value, bk_biz_id, username, bk_supplier_account):
        ip_dimension = super(MonitorAlarmShieldServiceBase, self).get_ip_dimension_config(
            scope_value, bk_biz_id, username
        )
        return ip_dimension

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
        target = [{"bk_obj_id": "module", "bk_inst_id": module_id["bk_module_id"]} for module_id in module_ids]

        return {"scope_type": "node", "target": target}

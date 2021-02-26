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

from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    CallAssertion,
    ExecuteAssertion,
    Call,
    Patcher,
)
from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1 import MonitorAlarmShieldComponent


class MonitorAlarmShieldComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [ALTER_BILL_FAIL_CASE, ALTER_BILL_SUCCESS_CASE]

    def component_cls(self):
        return MonitorAlarmShieldComponent


class MockClient(object):
    def __init__(self, create_shield_result=None):
        self.monitor = MagicMock()
        self.monitor.create_shield = MagicMock(return_value=create_shield_result)


# mock path
GET_CLIENT_BY_USER = "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1.get_client_by_user"
GET_MODULE_ID_LIST_BY_NAME = (
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1" ".get_module_id_list_by_name"
)
GET_SET_LIST = "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1.get_set_list"
GET_LIST_BY_SELECTED_NAMES = (
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1" ".get_list_by_selected_names"
)
GET_SERVICE_TEMPLATE_LIST = (
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1" ".get_service_template_list"
)
GET_SERVICE_TEMPLATE_LIST_BY_NAMES = (
    "pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.v1_1" ".get_service_template_list_by_names"
)

# mock client
CREATE_SHIELD_FAIL_CLIENT = MockClient(create_shield_result={"result": False, "message": "create shield fail"})

CREATE_SHIELD_SUCCESS_CLIENT = MockClient(
    create_shield_result={"result": True, "data": {"id": "1"}, "message": "success"}
)

INPUT_DATA = {
    "bk_alarm_shield_info": {
        "bk_alarm_shield_scope": "node",
        "bk_alarm_shield_business": 2,
        "bk_alarm_shield_node": {
            "bk_set_method": "select",
            "bk_set_select": ["set_name1", "set_name2"],
            "bk_set_text": "",
            "bk_module_method": "select",
            "bk_module_select": ["module_name1", "module_name2", "module_name3"],
            "bk_module_text": "",
        },
        "bk_alarm_shield_IP": "",
    },
    "bk_alarm_shield_target": ["bk_monitor.system.load.load5", "bk_monitor.system.cpu_summary.usage"],
    "bk_alarm_shield_begin_time": "2020-09-28 11:18:58",
    "bk_alarm_shield_end_time": "2020-09-28 11:18:58",
    "bk_alarm_time_type": "0",
    "bk_alarm_shield_duration": "0",
}


def get_set_list(username, bk_biz_id, bk_supplier_account, kwargs=None):
    set_list = [
        {"bk_set_id": 2, "bk_set_name": "set_name1"},
        {"bk_set_id": 3, "bk_set_name": "set_name2"},
        {"bk_set_id": 4, "bk_set_name": "set_name3"},
        {"bk_set_id": 5, "bk_set_name": "set_name4"},
    ]
    return set_list


def get_list_by_selected_names(set_names, set_list):
    selected_names = [{"bk_set_id": 2, "bk_set_name": "set_name1"}, {"bk_set_id": 3, "bk_set_name": "set_name2"}]
    return selected_names


def get_service_template_list(username, bk_biz_id, bk_supplier_account):
    service_template_list = [
        {"bk_biz_id": 2, "name": "module_name1", "service_category_id": 32, "id": 51},
        {"bk_biz_id": 2, "name": "module_name2", "service_category_id": 32, "id": 50},
        {"bk_biz_id": 2, "name": "module_name3", "service_category_id": 2, "id": 47},
        {"bk_biz_id": 2, "name": "module_name4", "service_category_id": 2, "id": 46},
        {"bk_biz_id": 2, "name": "module_name5", "service_category_id": 2, "id": 45},
    ]
    return service_template_list


def get_service_template_list_by_names(service_template_names, service_template_list):
    service_template_names_list = [
        {"bk_biz_id": 2, "name": "module_name1", "service_category_id": 32, "id": 51},
        {"bk_biz_id": 2, "name": "module_name2", "service_category_id": 32, "id": 50},
        {"bk_biz_id": 2, "name": "module_name3", "service_category_id": 2, "id": 47},
        {"bk_biz_id": 2, "name": "module_name4", "service_category_id": 2, "id": 46},
        {"bk_biz_id": 2, "name": "module_name5", "service_category_id": 2, "id": 45},
    ]
    return service_template_names_list


def get_module_id_list_by_name(bk_biz_id, username, set_list, service_template_list):
    module_id = [1, 2, 3, 4, 5]
    return module_id


# test case
ALTER_BILL_FAIL_CASE = ComponentTestCase(
    name="create shield fail case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "shield_id": "",
            "message": '调用监控平台(Monitor)接口monitor.create_shield返回失败, params={"begin_time":"2020-09-28 11:18:58",'
            '"bk_biz_id":2,"category":"scope","cycle_config":{"begin_time":"","end_time":"","day_list":[],'
            '"week_list":[],"type":1},"description":"shield by bk_sops","dimension_config":'
            '{"scope_type":"node","target":[{"bk_obj_id":"module","bk_inst_id":1},{"bk_obj_id":"module",'
            '"bk_inst_id":2},{"bk_obj_id":"module","bk_inst_id":3},{"bk_obj_id":"module","bk_inst_id":4},'
            '{"bk_obj_id":"module","bk_inst_id":5}],"metric_id":["bk_monitor.system.load.load5",'
            '"bk_monitor.system.cpu_summary.usage"]},"end_time":"2020-09-28 11:18:58","notice_config":{},'
            '"shield_notice":false,"source":"bk_sops"}, error=create shield fail',
        },
    ),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_SHIELD_FAIL_CLIENT.monitor.create_shield,
            calls=[
                Call(
                    {
                        "begin_time": "2020-09-28 11:18:58",
                        "bk_biz_id": 2,
                        "category": "scope",
                        "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
                        "description": "shield by bk_sops",
                        "dimension_config": {
                            "scope_type": "node",
                            "target": [
                                {"bk_obj_id": "module", "bk_inst_id": 1},
                                {"bk_obj_id": "module", "bk_inst_id": 2},
                                {"bk_obj_id": "module", "bk_inst_id": 3},
                                {"bk_obj_id": "module", "bk_inst_id": 4},
                                {"bk_obj_id": "module", "bk_inst_id": 5},
                            ],
                            "metric_id": ["bk_monitor.system.load.load5", "bk_monitor.system.cpu_summary.usage"],
                        },
                        "end_time": "2020-09-28 11:18:58",
                        "notice_config": {},
                        "shield_notice": False,
                        "source": "bk_sops",
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_SHIELD_FAIL_CLIENT),
        Patcher(target=GET_SET_LIST, side_effect=get_set_list),
        Patcher(target=GET_LIST_BY_SELECTED_NAMES, side_effect=get_list_by_selected_names),
        Patcher(target=GET_SERVICE_TEMPLATE_LIST, side_effect=get_service_template_list),
        Patcher(target=GET_SERVICE_TEMPLATE_LIST_BY_NAMES, side_effect=get_service_template_list_by_names),
        Patcher(target=GET_MODULE_ID_LIST_BY_NAME, side_effect=get_module_id_list_by_name),
    ],
)

ALTER_BILL_SUCCESS_CASE = ComponentTestCase(
    name="create shield success case",
    inputs=INPUT_DATA,
    parent_data={"executor": "executor", "biz_cc_id": 2},
    execute_assertion=ExecuteAssertion(success=True, outputs={"shield_id": "1", "message": "success"}),
    schedule_assertion=None,
    execute_call_assertion=[
        CallAssertion(
            func=CREATE_SHIELD_SUCCESS_CLIENT.monitor.create_shield,
            calls=[
                Call(
                    {
                        "begin_time": "2020-09-28 11:18:58",
                        "bk_biz_id": 2,
                        "category": "scope",
                        "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
                        "description": "shield by bk_sops",
                        "dimension_config": {
                            "scope_type": "node",
                            "target": [
                                {"bk_obj_id": "module", "bk_inst_id": 1},
                                {"bk_obj_id": "module", "bk_inst_id": 2},
                                {"bk_obj_id": "module", "bk_inst_id": 3},
                                {"bk_obj_id": "module", "bk_inst_id": 4},
                                {"bk_obj_id": "module", "bk_inst_id": 5},
                            ],
                            "metric_id": ["bk_monitor.system.load.load5", "bk_monitor.system.cpu_summary.usage"],
                        },
                        "end_time": "2020-09-28 11:18:58",
                        "notice_config": {},
                        "shield_notice": False,
                        "source": "bk_sops",
                    }
                )
            ],
        )
    ],
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=CREATE_SHIELD_SUCCESS_CLIENT),
        Patcher(target=GET_SET_LIST, side_effect=get_set_list),
        Patcher(target=GET_LIST_BY_SELECTED_NAMES, side_effect=get_list_by_selected_names),
        Patcher(target=GET_SERVICE_TEMPLATE_LIST, side_effect=get_service_template_list),
        Patcher(target=GET_SERVICE_TEMPLATE_LIST_BY_NAMES, side_effect=get_service_template_list_by_names),
        Patcher(target=GET_MODULE_ID_LIST_BY_NAME, side_effect=get_module_id_list_by_name),
    ],
)

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

from mock import MagicMock, patch

from django.test import TestCase

from pipeline_plugins.variables.collections.sites.open.cmdb.var_set_group_selector import (
    VarSetGroupSelector,
    SetGroupInfo,
)

GET_CLIENT_BY_USER = "pipeline_plugins.variables.collections.sites.open.cmdb.var_set_group_selector.get_client_by_user"


class MockClient(object):
    def __init__(self, execute_dynamic_group_return=None):
        self.cc = MagicMock()
        self.cc.execute_dynamic_group = MagicMock(return_value=execute_dynamic_group_return)


INPUT_OUTPUT_SUCCESS_CLIENT = MockClient(
    execute_dynamic_group_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 1,
            "info": [
                {
                    "bk_obj_id": "set",
                    "bk_set_id": "123",
                    "bk_set_name": "set123",
                    "bk_set_env": "3",
                    "bk_category": "200",
                    "bk_set_desc": "测试",
                    "bk_uniq_id": "123",
                    "bk_alias_name": "测试",
                    "bk_service_status": "1",
                    "bk_open_time": "2020-09-12 16：58",
                    "bk_capacity": "1",
                    "description": "测试group",
                    "bk_world_id": "321",
                    "bk_svc_name": "测试group23",
                    "bk_customer": "运维",
                    "bk_operation_state": "1",
                    "bk_enable_relate_webplat": "77",
                    "bk_is_gcs": False,
                    "bk_outer_source": "1.1.1.1",
                    "bk_set_idc": "21",
                    "bk_system": "测试系统",
                    "bk_platform": "测试平台",
                    "bk_chn_name": "测试"
                }
            ]
        }
    },
)

MULTI_INPUT_OUTPUT_CLIENT = MockClient(
    execute_dynamic_group_return={
        "result": True,
        "code": 0,
        "message": "",
        "data": {
            "count": 2,
            "info": [
                {
                    "bk_obj_id": "set",
                    "bk_set_id": "123",
                    "bk_set_name": "set123",
                    "bk_set_env": "3",
                    "bk_category": "200",
                    "bk_set_desc": "测试",
                    "bk_uniq_id": "123",
                    "bk_alias_name": "测试",
                    "bk_service_status": "1",
                    "bk_open_time": "2020-09-12 16：58",
                    "bk_capacity": "1",
                    "description": "测试group",
                    "bk_world_id": "321",
                    "bk_svc_name": "测试group23",
                    "bk_customer": "运维",
                    "bk_operation_state": "1",
                    "bk_enable_relate_webplat": "77",
                    "bk_is_gcs": False,
                    "bk_outer_source": "1.1.1.1",
                    "bk_set_idc": "21",
                    "bk_system": "测试系统",
                    "bk_platform": "测试平台",
                    "bk_chn_name": "测试"
                },
                {
                    "bk_obj_id": "set2",
                    "bk_set_id": "1234",
                    "bk_set_name": "set1234",
                    "bk_set_env": "3",
                    "bk_category": "200",
                    "bk_set_desc": "测试2",
                    "bk_uniq_id": "1234",
                    "bk_alias_name": "测试2",
                    "bk_service_status": "1",
                    "bk_open_time": "2020-09-12 16：00",
                    "bk_capacity": "1",
                    "description": "测试group2",
                    "bk_world_id": "4321",
                    "bk_svc_name": "测试group234",
                    "bk_customer": "运维2",
                    "bk_operation_state": "1",
                    "bk_enable_relate_webplat": "772",
                    "bk_is_gcs": False,
                    "bk_outer_source": "2.2.2.2",
                    "bk_set_idc": "212",
                    "bk_system": "测试系统2",
                    "bk_platform": "测试平台2",
                    "bk_chn_name": "测试"
                }
            ]
        }
    },
)

GET_GROUP_INFO_FAIL_CLIENT = MockClient(
    execute_dynamic_group_return={"result": False},
)


class VarSetGroupSelectorTestCase(TestCase):
    def setUp(self):
        self.value = {"bk_group_id": "456"}
        self.multi_value = {"bk_group_id": "789"}
        self.pipeline_data = {
            "executor": "admin",
            "biz_cc_id": "123",
        }
        self.input_output_success_return = SetGroupInfo(
            {
                "bk_set_id": ["123"],
                "bk_set_name": ["set123"],
                "bk_set_env": ["3"],
                "bk_category": ["200"],
                "bk_set_desc": ["测试"],
                "bk_uniq_id": ["123"],
                "bk_alias_name": ["测试"],
                "bk_service_status": ["1"],
                "bk_open_time": ["2020-09-12 16：58"],
                "bk_capacity": ["1"],
                "description": ["测试group"],
                "bk_world_id": ["321"],
                "bk_svc_name": ["测试group23"],
                "bk_customer": ["运维"],
                "bk_operation_state": ["1"],
                "bk_enable_relate_webplat": ["77"],
                "bk_is_gcs": ["False"],
                "bk_outer_source": ["1.1.1.1"],
                "bk_set_idc": ["21"],
                "bk_system": ["测试系统"],
                "bk_platform": ["测试平台"],
                "bk_chn_name": ["测试"],
                "flat__bk_set_id": "123",
                "flat__bk_set_name": "set123",
                "flat__bk_set_env": "3",
                "flat__bk_category": "200",
                "flat__bk_set_desc": "测试",
                "flat__bk_uniq_id": "123",
                "flat__bk_alias_name": "测试",
                "flat__bk_service_status": "1",
                "flat__bk_open_time": "2020-09-12 16：58",
                "flat__bk_capacity": "1",
                "flat__description": "测试group",
                "flat__bk_world_id": "321",
                "flat__bk_svc_name": "测试group23",
                "flat__bk_customer": "运维",
                "flat__bk_operation_state": "1",
                "flat__bk_enable_relate_webplat": "77",
                "flat__bk_is_gcs": "False",
                "flat__bk_outer_source": "1.1.1.1",
                "flat__bk_set_idc": "21",
                "flat__bk_system": "测试系统",
                "flat__bk_platform": "测试平台",
                "flat__bk_chn_name": "测试"
            }
        )
        self.multi_output_success_return = SetGroupInfo(
            {
                "bk_set_id": ["123", "1234"],
                "bk_set_name": ["set123", "set1234"],
                "bk_set_env": ["3", "3"],
                "bk_category": ["200", "200"],
                "bk_set_desc": ["测试", "测试2"],
                "bk_uniq_id": ["123", "1234"],
                "bk_alias_name": ["测试", "测试2"],
                "bk_service_status": ["1", "1"],
                "bk_open_time": ["2020-09-12 16：58", "2020-09-12 16：00"],
                "bk_capacity": ["1", "1"],
                "description": ["测试group", "测试group2"],
                "bk_world_id": ["321", "4321"],
                "bk_svc_name": ["测试group23", "测试group234"],
                "bk_customer": ["运维", "运维2"],
                "bk_operation_state": ["1", "1"],
                "bk_enable_relate_webplat": ["77", "772"],
                "bk_is_gcs": ["False", "False"],
                "bk_outer_source": ["1.1.1.1", "2.2.2.2"],
                "bk_set_idc": ["21", "212"],
                "bk_system": ["测试系统", "测试系统2"],
                "bk_platform": ["测试平台", "测试平台2"],
                "bk_chn_name": ["测试", "测试"],
                "flat__bk_set_id": "123,1234",
                "flat__bk_set_name": "set123,set1234",
                "flat__bk_set_env": "3,3",
                "flat__bk_category": "200,200",
                "flat__bk_set_desc": "测试,测试2",
                "flat__bk_uniq_id": "123,1234",
                "flat__bk_alias_name": "测试,测试2",
                "flat__bk_service_status": "1,1",
                "flat__bk_open_time": "2020-09-12 16：58,2020-09-12 16：00",
                "flat__bk_capacity": "1,1",
                "flat__description": "测试group,测试group2",
                "flat__bk_world_id": "321,4321",
                "flat__bk_svc_name": "测试group23,测试group234",
                "flat__bk_customer": "运维,运维2",
                "flat__bk_operation_state": "1,1",
                "flat__bk_enable_relate_webplat": "77,772",
                "flat__bk_is_gcs": "False,False",
                "flat__bk_outer_source": "1.1.1.1,2.2.2.2",
                "flat__bk_set_idc": "21,212",
                "flat__bk_system": "测试系统,测试系统2",
                "flat__bk_platform": "测试平台,测试平台2",
                "flat__bk_chn_name": "测试,测试"
            }
        )
        self.input_output_fail_return = SetGroupInfo(
            {
                "bk_set_id": [],
                "bk_set_name": [],
                "bk_set_env": [],
                "bk_category": [],
                "bk_set_desc": [],
                "bk_uniq_id": [],
                "bk_alias_name": [],
                "bk_service_status": [],
                "bk_open_time": [],
                "bk_capacity": [],
                "description": [],
                "bk_world_id": [],
                "bk_svc_name": [],
                "bk_customer": [],
                "bk_operation_state": [],
                "bk_enable_relate_webplat": [],
                "bk_is_gcs": [],
                "bk_outer_source": [],
                "bk_set_idc": [],
                "bk_system": [],
                "bk_platform": [],
                "bk_chn_name": [],
                "flat__bk_set_id": "",
                "flat__bk_set_name": "",
                "flat__bk_set_env": "",
                "flat__bk_category": "",
                "flat__bk_set_desc": "",
                "flat__bk_uniq_id": "",
                "flat__bk_alias_name": "",
                "flat__bk_service_status": "",
                "flat__bk_open_time": "",
                "flat__bk_capacity": "",
                "flat__description": "",
                "flat__bk_world_id": "",
                "flat__bk_svc_name": "",
                "flat__bk_customer": "",
                "flat__bk_operation_state": "",
                "flat__bk_enable_relate_webplat": "",
                "flat__bk_is_gcs": "",
                "flat__bk_outer_source": "",
                "flat__bk_set_idc": "",
                "flat__bk_system": "",
                "flat__bk_platform": "",
                "flat__bk_chn_name": ""
            }
        )

    @patch(GET_CLIENT_BY_USER, return_value=INPUT_OUTPUT_SUCCESS_CLIENT)
    def test_input_output_success_case(self, mock_get_client_by_user_return):
        """
        整个变量的输入输出正确的测试用例
        """
        set_group_selector = VarSetGroupSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        self.SetGroupInfoEqual(set_group_selector.get_value(), self.input_output_success_return)

    @patch(GET_CLIENT_BY_USER, return_value=GET_GROUP_INFO_FAIL_CLIENT)
    def test_get_module_info_fail_case(self, mock_get_client_by_user_return):
        """
        获取模块信息失败的测试用例
        """
        set_group_selector = VarSetGroupSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        self.SetGroupInfoEqual(set_group_selector.get_value(), self.input_output_fail_return)

    @patch(GET_CLIENT_BY_USER, return_value=MULTI_INPUT_OUTPUT_CLIENT)
    def test_multi_modules_success_case(self, mock_get_client_by_user_return):
        """
        多模块返回成功的测试用例
        """
        set_group_selector = VarSetGroupSelector(
            pipeline_data=self.pipeline_data, value=self.multi_value, name="test", context={}
        )
        self.SetGroupInfoEqual(set_group_selector.get_value(), self.multi_output_success_return)

    def SetGroupInfoEqual(self, first_inst, second_inst):
        """
        自定义断言：用于判断两个对象的属性值是否相等
        """
        set_field = [
            "bk_set_id",
            "bk_set_name",
            "bk_set_env",
            "bk_category",
            "bk_set_desc",
            "bk_uniq_id",
            "bk_alias_name",
            "bk_service_status",
            "bk_open_time",
            "bk_capacity",
            "description",
            "bk_world_id",
            "bk_svc_name",
            "bk_customer",
            "bk_operation_state",
            "bk_enable_relate_webplat",
            "bk_is_gcs",
            "bk_outer_source",
            "bk_set_idc",
            "bk_system",
            "bk_platform",
            "bk_chn_name"
        ]
        for _field in set_field:
            flat_field_name = "flat__{}".format(_field)
            assert first_inst.__getattribute__(_field) == second_inst.__getattribute__(_field)
            assert first_inst.__getattribute__(flat_field_name) == second_inst.__getattribute__(flat_field_name)

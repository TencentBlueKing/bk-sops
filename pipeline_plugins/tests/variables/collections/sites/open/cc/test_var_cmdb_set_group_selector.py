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

from mock import MagicMock, patch

from django.test import TestCase

from gcloud.exceptions import ApiRequestError
from pipeline_plugins.variables.collections.sites.open.cmdb.var_set_group_selector import (
    VarSetGroupSelector,
    SetGroupInfo,
)

GET_CLIENT_BY_USER = "pipeline_plugins.variables.collections.sites.open.cmdb.var_set_group_selector.get_client_by_user"


class MockClient(object):
    def __init__(self, execute_dynamic_group_return=None, search_object_attribute_return=None):
        self.cc = MagicMock()
        self.cc.execute_dynamic_group = MagicMock(return_value=execute_dynamic_group_return)
        self.cc.search_object_attribute = MagicMock(side_effect=search_object_attribute_return)


set_field = [
    "bk_set_id",
    "bk_set_name",
    "bk_set_desc",
    "bk_set_env",
    "bk_service_status",
    "description",
    "bk_capacity",
    "aaa",
]


def search_object_attribute(*args, **kwargs):
    result = {
        "code": 0,
        "result": True,
        "message": "success",
        "data": [
            {"bk_property_id": "bk_set_name"},
            {"bk_property_id": "bk_set_desc"},
            {"bk_property_id": "bk_set_env"},
            {"bk_property_id": "bk_service_status"},
            {"bk_property_id": "description"},
            {"bk_property_id": "bk_capacity"},
            {"bk_property_id": "aaa"},
        ],
    }
    return result


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
                    "bk_set_desc": "测试",
                    "bk_service_status": "1",
                    "bk_capacity": "1",
                    "description": "测试group",
                    "aaa": "321",
                }
            ],
        },
    },
    search_object_attribute_return=search_object_attribute,
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
                    "bk_set_desc": "测试",
                    "bk_service_status": "1",
                    "bk_capacity": "1",
                    "description": "测试group",
                    "aaa": "321",
                },
                {
                    "bk_obj_id": "set2",
                    "bk_set_id": "1234",
                    "bk_set_name": "set1234",
                    "bk_set_env": "3",
                    "bk_set_desc": "测试2",
                    "bk_service_status": "1",
                    "bk_capacity": "1",
                    "description": "测试group2",
                    "aaa": "333",
                },
            ],
        },
    },
    search_object_attribute_return=search_object_attribute,
)

GET_GROUP_INFO_FAIL_CLIENT = MockClient(
    execute_dynamic_group_return={"result": False}, search_object_attribute_return=search_object_attribute
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
                "bk_set_desc": ["测试"],
                "bk_set_env": ["3"],
                "bk_service_status": ["1"],
                "description": ["测试group"],
                "bk_capacity": ["1"],
                "aaa": ["321"],
                "flat__bk_set_id": "123",
                "flat__bk_set_name": "set123",
                "flat__bk_set_desc": "测试",
                "flat__bk_set_env": "3",
                "flat__bk_service_status": "1",
                "flat__description": "测试group",
                "flat__bk_capacity": "1",
                "flat__aaa": "321",
            },
            set_field,
        )
        self.multi_output_success_return = SetGroupInfo(
            {
                "bk_set_id": ["123", "1234"],
                "bk_set_name": ["set123", "set1234"],
                "bk_set_env": ["3", "3"],
                "bk_set_desc": ["测试", "测试2"],
                "bk_service_status": ["1", "1"],
                "bk_capacity": ["1", "1"],
                "description": ["测试group", "测试group2"],
                "aaa": ["321", "333"],
                "flat__bk_set_id": "123,1234",
                "flat__bk_set_name": "set123,set1234",
                "flat__bk_set_env": "3,3",
                "flat__bk_set_desc": "测试,测试2",
                "flat__bk_service_status": "1,1",
                "flat__bk_capacity": "1,1",
                "flat__description": "测试group,测试group2",
                "flat__aaa": "321,333",
            },
            set_field,
        )
        self.input_output_fail_return = SetGroupInfo(
            {
                "bk_set_id": [],
                "bk_set_name": [],
                "bk_set_env": [],
                "bk_set_desc": [],
                "bk_service_status": [],
                "bk_capacity": [],
                "description": [],
                "aaa": [],
                "flat__bk_set_id": "",
                "flat__bk_set_name": "",
                "flat__bk_set_env": "",
                "flat__bk_set_desc": "",
                "flat__bk_service_status": "",
                "flat__bk_capacity": "",
                "flat__description": "",
                "flat__aaa": "",
            },
            set_field,
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
            pipeline_data=self.pipeline_data, value=self.value, name="test2", context={}
        )
        with self.assertRaises(ApiRequestError) as context:
            set_group_selector.get_value()

        self.assertTrue("ApiRequestError" in str(context.exception))

    @patch(GET_CLIENT_BY_USER, return_value=MULTI_INPUT_OUTPUT_CLIENT)
    def test_multi_modules_success_case(self, mock_get_client_by_user_return):
        """
        多模块返回成功的测试用例
        """
        set_group_selector = VarSetGroupSelector(
            pipeline_data=self.pipeline_data, value=self.multi_value, name="test3", context={}
        )
        self.SetGroupInfoEqual(set_group_selector.get_value(), self.multi_output_success_return)

    def SetGroupInfoEqual(self, first_inst, second_inst):
        """
        自定义断言：用于判断两个对象的属性值是否相等
        """
        for _field in set_field:
            flat_field_name = "flat__{}".format(_field)
            assert first_inst.__getattribute__(_field) == second_inst.__getattribute__(_field)
            assert first_inst.__getattribute__(flat_field_name) == second_inst.__getattribute__(flat_field_name)

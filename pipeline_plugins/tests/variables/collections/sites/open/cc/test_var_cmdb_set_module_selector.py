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
from unittest.util import safe_repr

from mock import MagicMock, patch

from django.test import TestCase

from gcloud.exceptions import ApiRequestError
from pipeline_plugins.variables.collections.sites.open.cmdb.var_set_module_selector import (
    VarSetModuleSelector,
    SetModuleInfo,
)

GET_CLIENT_BY_USERNAME = ("pipeline_plugins.variables.collections.sites.open.cmdb.var_set_module_selector"
                          ".get_client_by_username")


class MockClient(object):
    def __init__(self, search_set_return=None, search_module_return=None):
        self.api = MagicMock()
        self.api.search_set = MagicMock(return_value=search_set_return)
        self.api.search_module = MagicMock(return_value=search_module_return)


INPUT_OUTPUT_SUCCESS_CLIENT = MockClient(
    search_set_return={"result": True, "data": {"info": [{"bk_set_name": "set"}]}},
    search_module_return={
        "result": True,
        "data": {"info": [{"bk_module_name": "module", "bk_module_id": 789}], "count": 1},
    },
)

GET_SET_INFO_FAIL_CLIENT = MockClient(
    search_set_return={"result": False},
    search_module_return={
        "result": True,
        "data": {"info": [{"bk_module_name": "module", "bk_module_id": 789}], "count": 1},
    },
)

GET_MODULE_INFO_FAIL_CLIENT = MockClient(
    search_set_return={"result": True, "data": {"info": [{"bk_set_name": "set"}]}},
    search_module_return={"result": False},
)

MULTI_MODULES_SUCCESS_CLIENT = MockClient(
    search_set_return={"result": True, "data": {"info": [{"bk_set_name": "set"}]}},
    search_module_return={
        "result": True,
        "data": {
            "count": 2,
            "info": [
                {"bk_module_name": "module1", "bk_module_id": 678},
                {"bk_module_name": "module2", "bk_module_id": 789},
            ],
        },
    },
)


class VarSetModuleSelectorTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "test"
        self.value = {"bk_set_id": "456", "bk_module_id": [789]}
        self.multi_modules_value = {"bk_set_id": "456", "bk_module_id": [678, 789]}

        self.pipeline_data = {
            "executor": "admin",
            "biz_cc_id": "123",
            "tenant_id": "test",
        }
        self.input_output_success_return = SetModuleInfo(
            {
                "set_name": "set",
                "set_id": 456,
                "module_name": ["module"],
                "module_id": [789],
                "flat__module_id": "789",
                "flat__module_name": "module",
            }
        )
        self.get_set_info_fail_return = SetModuleInfo(
            {
                "set_name": "",
                "set_id": 456,
                "module_name": ["module"],
                "module_id": [789],
                "flat__module_id": "789",
                "flat__module_name": "module",
            }
        )
        self.get_module_info_fail_return = SetModuleInfo(
            {
                "set_name": "set",
                "set_id": 456,
                "module_name": [],
                "module_id": [789],
                "flat__module_id": "789",
                "flat__module_name": "",
            }
        )

        self.multi_modules_success_return = SetModuleInfo(
            {
                "set_name": "set",
                "set_id": 456,
                "module_name": ["module1", "module2"],
                "module_id": [678, 789],
                "flat__module_name": "module1,module2",
                "flat__module_id": "678,789",
            }
        )

    @patch(GET_CLIENT_BY_USERNAME, return_value=INPUT_OUTPUT_SUCCESS_CLIENT)
    def test_input_output_success_case(self, mock_get_client_by_user_return):
        """
        整个变量的输入输出正确的测试用例
        """
        set_module_selector = VarSetModuleSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        self.SetModuleInfoEqual(set_module_selector.get_value(), self.input_output_success_return)

    @patch(GET_CLIENT_BY_USERNAME, return_value=GET_SET_INFO_FAIL_CLIENT)
    def test_get_set_info_fail_case(self, mock_get_client_by_user_return):
        """
        获取集群信息失败的测试用例
        """
        set_module_selector = VarSetModuleSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        with self.assertRaises(ApiRequestError) as context:
            set_module_selector.get_value()

        self.assertTrue("ApiRequestError" in str(context.exception))

    @patch(GET_CLIENT_BY_USERNAME, return_value=GET_MODULE_INFO_FAIL_CLIENT)
    def test_get_module_info_fail_case(self, mock_get_client_by_user_return):
        """
        获取模块信息失败的测试用例
        """
        set_module_selector = VarSetModuleSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        with self.assertRaises(ApiRequestError) as context:
            set_module_selector.get_value()

        self.assertTrue("ApiRequestError" in str(context.exception))

    @patch(GET_CLIENT_BY_USERNAME, return_value=MULTI_MODULES_SUCCESS_CLIENT)
    def test_multi_modules_success_case(self, mock_get_client_by_user_return):
        """
        多模块返回成功的测试用例
        """
        set_module_selector = VarSetModuleSelector(
            pipeline_data=self.pipeline_data, value=self.multi_modules_value, name="test", context={}
        )
        self.SetModuleInfoEqual(set_module_selector.get_value(), self.multi_modules_success_return)

    def SetModuleInfoEqual(self, first_inst, second_inst):
        """
        自定义断言：用于判断两个对象的属性值是否相等
        """
        if not (
            first_inst.set_name == second_inst.set_name
            and first_inst.set_id == second_inst.set_id
            and first_inst.module_name == second_inst.module_name
            and first_inst.module_id == second_inst.module_id
            and first_inst.flat__module_id == second_inst.flat__module_id
            and first_inst.flat__module_name == second_inst.flat__module_name
        ):
            msg = self._formatMessage("%s == %s" % (safe_repr(first_inst), safe_repr(second_inst)))
            raise self.failureException(msg)

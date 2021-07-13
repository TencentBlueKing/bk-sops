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
from functools import reduce

from unittest.util import safe_repr
from mock import MagicMock, patch
from django.test import TestCase

from gcloud.exceptions import ApiRequestError
from pipeline_plugins.variables.collections.sites.open.cmdb.var_set_filter_selector import VarSetFilterSelector, SetInfo

GET_CLIENT_BY_USER = "pipeline_plugins.variables.collections.sites.open.cmdb.var_set_filter_selector.get_client_by_user"


class MockClient(object):
    def __init__(self, search_set_return=None, search_module_return=None):
        self.cc = MagicMock()
        self.cc.search_set = MagicMock(return_value=search_set_return)
        self.cc.search_module = MagicMock(return_value=search_module_return)


INPUT_OUTPUT_SUCCESS_CLIENT = MockClient(
    search_set_return={"result": True, "data": {"info": [{"bk_set_name": "set", "bk_set_id": 1}]}},
)

GET_SET_INFO_FAIL_CLIENT = MockClient(
    search_set_return={"result": False}, search_module_return={"result": False, "data": None},
)


class VarSetFilterSelectorTestCase(TestCase):
    def setUp(self):
        self.value = {"bk_obj_id": "bk_service_status", "bk_module_id": "1"}
        self.multi_modules_value = {"bk_set_id": "456", "bk_module_id": [678, 789]}

        self.pipeline_data = {
            "executor": "admin",
            "biz_cc_id": "2",
        }
        self.input_output_success_return = SetInfo(
            [{"bk_set_name": "set", "bk_set_id": 1}], {"bk_set_name", "bk_set_id"}
        )

        self.get_set_info_fail_return = SetInfo([], set())

    @patch(GET_CLIENT_BY_USER, return_value=INPUT_OUTPUT_SUCCESS_CLIENT)
    def test_input_output_success_case(self, mock_get_client_by_user_return):
        """
        整个变量的输入输出正确的测试用例
        """
        set_module_selector = VarSetFilterSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        self.SetInfoEqual(set_module_selector.get_value(), self.input_output_success_return)

    @patch(GET_CLIENT_BY_USER, return_value=GET_SET_INFO_FAIL_CLIENT)
    def test_get_set_info_fail_case(self, mock_get_client_by_user_return):
        """
        获取集群信息失败的测试用例
        """
        VarSetFilterSelector(pipeline_data=self.pipeline_data, value=self.value, name="test", context={})
        self.assertRaises(ApiRequestError)

    @staticmethod
    def _get_set_attributes(set_infos):
        if not set_infos:
            return set()
        return reduce(set.intersection, [set(info.keys()) for info in set_infos])

    def SetInfoEqual(self, first_inst, second_inst):
        """
        自定义断言：用于判断两个对象的属性值是否相等
        """
        first_attrs = self._get_set_attributes(first_inst.bk_sets)
        second_attrs = self._get_set_attributes(second_inst.bk_sets)
        if first_attrs != second_attrs:
            msg = self._formatMessage("%s == %s" % (safe_repr(first_inst), safe_repr(second_inst)))
            raise self.failureException(msg)
        for attr in first_attrs:
            if getattr(first_inst, attr) != getattr(second_inst, attr):
                msg = self._formatMessage("%s == %s" % (safe_repr(first_inst), safe_repr(second_inst)))
                raise self.failureException(msg)

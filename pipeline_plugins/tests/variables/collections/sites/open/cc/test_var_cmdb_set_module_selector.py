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
from unittest.util import safe_repr

from mock import MagicMock, patch

from django.test import TestCase

from pipeline_plugins.variables.collections.sites.open.cmdb.var_set_module_selector import (
    VarSetModuleSelector,
    SetModuleInfo,
)

GET_CLIENT_BY_USER = "pipeline_plugins.variables.collections.sites.open.cmdb.var_set_module_selector.get_client_by_user"


class MockClient(object):
    def __init__(self, search_set_return=None, search_module_return=None):
        self.cc = MagicMock()
        self.cc.search_set = MagicMock(return_value=search_set_return)
        self.cc.search_module = MagicMock(return_value=search_module_return)


GET_CLIENT_BY_USER_RETURN = MockClient(
    search_set_return={"result": True, "data": {"info": [{"bk_set_name": "set"}]}},
    search_module_return={"result": True, "data": {"info": [{"bk_module_name": "module"}]}},
)


class VarSetModuleSelectorTestCase(TestCase):
    def setUp(self):
        self.value = {"bk_set_id": "456", "bk_module_id": "789"}
        self.pipeline_data = {
            "executor": "admin",
            "biz_cc_id": "123",
        }
        self.get_value_return = SetModuleInfo({"set": "set", "set_id": 456, "module": "module", "module_id": 789})

    @patch(GET_CLIENT_BY_USER, return_value=GET_CLIENT_BY_USER_RETURN)
    def test_get_value(self, mock_get_client_by_user_return):
        set_module_selector = VarSetModuleSelector(
            pipeline_data=self.pipeline_data, value=self.value, name="test", context={}
        )
        self.assertInstEqual(set_module_selector.get_value(), self.get_value_return)

    def assertInstEqual(self, first_inst, second_inst):
        """自定义断言：用于判断两个对象的属性值是否相等
        """
        if not (
            first_inst.set == second_inst.set
            and first_inst.set_id == second_inst.set_id
            and first_inst.module == second_inst.module
            and first_inst.module_id == second_inst.module_id
        ):
            msg = self._formatMessage("%s == %s" % (safe_repr(first_inst), safe_repr(second_inst)))
            raise self.failureException(msg)

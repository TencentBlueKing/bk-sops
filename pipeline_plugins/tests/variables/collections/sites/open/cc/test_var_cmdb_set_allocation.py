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

from mock import MagicMock, patch
from django.test import TestCase

from pipeline_plugins.variables.collections.sites.open.cc import VarCmdbSetAllocation


class VarCmdbSetAllocationTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "test"
        self.name = "name_token"
        self.value = {
            "separator": ";",
            "data": [
                {
                    "__module": [{"key": "module_a", "value": ["1.1.1.1"]}],
                    "bk_set_name": "test",
                    "bk_set_desc": "description",
                    "test_attr": "test_attr",
                },
                {
                    "__module": [
                        {"key": "module_b", "value": ["2.2.2.2"]},
                        {"key": "module_c", "value": ["1.2.3.4", "2.3.4.5"]},
                    ],
                    "bk_set_name": "test2",
                    "bk_set_desc": "description2",
                    "test_attr": "test_attr2",
                },
            ],
        }
        self.context = {}
        self.pipeline_data = {"tenant_id": self.tenant_id}

    def test_get_value_with_separator(self):
        set_allocation = VarCmdbSetAllocation(self.name, self.value, self.context, self.pipeline_data)
        set_detail_data = set_allocation.get_value()

        self.assertEqual(set_detail_data.set_count, 2)
        self.assertEqual(set_detail_data.flat__bk_set_name, "test;test2")
        self.assertEqual(
            set_detail_data._module, [{"module_a": "1.1.1.1"}, {"module_b": "2.2.2.2", "module_c": "1.2.3.4;2.3.4.5"}]
        )
        self.assertEqual(set_detail_data.flat__verbose_ip_list, "1.1.1.1;2.2.2.2;1.2.3.4;2.3.4.5")
        self.assertEqual(
            set_detail_data.flat__verbose_ip_module_list, "test>module_a;test2>module_b;test2>module_c;test2>module_c"
        )

    def test_get_value_without_separator(self):
        self.value.pop("separator")
        set_allocation = VarCmdbSetAllocation(self.name, self.value, self.context, self.pipeline_data)
        set_detail_data = set_allocation.get_value()

        self.assertEqual(set_detail_data.set_count, 2)
        self.assertEqual(set_detail_data.flat__bk_set_name, "test,test2")
        self.assertEqual(
            set_detail_data._module, [{"module_a": "1.1.1.1"}, {"module_b": "2.2.2.2", "module_c": "1.2.3.4,2.3.4.5"}]
        )
        self.assertEqual(set_detail_data.flat__verbose_ip_list, "1.1.1.1,2.2.2.2,1.2.3.4,2.3.4.5")
        self.assertEqual(
            set_detail_data.flat__verbose_ip_module_list, "test>module_a,test2>module_b,test2>module_c,test2>module_c"
        )

    def test_self_explain__search_object_attribute_success(self):
        client = MagicMock()
        client.api.search_object_attribute = MagicMock(
            return_value={
                "result": True,
                "message": "success",
                "data": [
                    {"editable": True, "bk_property_id": "set_name", "bk_property_name": "bk_name_name"},
                    {"editable": False, "bk_property_id": "set_id", "bk_property_name": "set_id_name"},
                    {"editable": True, "bk_property_id": "set_desc", "bk_property_name": "set_desc_name"},
                ],
            }
        )

        with patch(
                "pipeline_plugins.variables.collections.sites.open.cc.get_client_by_username",
                MagicMock(return_value=client)
        ):
            explain = VarCmdbSetAllocation.self_explain(bk_biz_id=1, tenant_id=self.tenant_id)

        client.api.search_object_attribute.assert_called_once_with(
            {"bk_obj_id": "set", "bk_biz_id": 1},
            headers={"X-Bk-Tenant-Id": self.tenant_id},
        )
        self.assertEqual(
            explain,
            {
                "tag": "var_cmdb_resource_allocation.set_allocation",
                "fields": [
                    {"key": "${KEY}", "type": "object", "description": "集群资源筛选结果对象"},
                    {"key": "${KEY.set_count}", "type": "int", "description": "新增集群数量"},
                    {"key": "${KEY._module}", "type": "list", "description": "集群下的模块信息列表，元素类型为字典，键为模块名，值为模块下的主机列"},
                    {"key": "${KEY.flat__ip_list}", "type": "string", "description": "本次操作创建的所有集群下的主机（去重后），用 ',' 连接"},
                    {
                        "key": "${KEY.flat__verbose_ip_list}",
                        "type": "string",
                        "description": "返回的是本次操作创建的所有集群下的主机（未去重），用 ',' 连接",
                    },
                    {
                        "key": "${KEY.flat__verbose_ip_module_list}",
                        "type": "string",
                        "description": "本次操作创建的所有模块名称，格式为set_name>module_name，用 ',' 连接",
                    },
                    {"key": "${KEY.set_name}", "type": "list", "description": "集群属性(bk_name_name)列表"},
                    {"key": "${KEY.flat__set_name}", "type": "string", "description": "集群属性(bk_name_name)列表，以,分隔"},
                    {"key": "${KEY.set_desc}", "type": "list", "description": "集群属性(set_desc_name)列表"},
                    {"key": "${KEY.flat__set_desc}", "type": "string", "description": "集群属性(set_desc_name)列表，以,分隔"},
                ],
            },
        )

    def test_self_explain__search_object_attribute_fail(self):
        client = MagicMock()
        client.api.search_object_attribute = MagicMock(return_value={"result": False, "message": "fail", "data": []})

        with patch(
                "pipeline_plugins.variables.collections.sites.open.cc.get_client_by_username",
                MagicMock(return_value=client)
        ):
            explain = VarCmdbSetAllocation.self_explain(bk_biz_id=1, tenant_id=self.tenant_id)

        client.api.search_object_attribute.assert_called_once_with(
            {"bk_obj_id": "set", "bk_biz_id": 1},
            headers={"X-Bk-Tenant-Id": self.tenant_id},
        )
        self.assertEqual(
            explain,
            {
                "tag": "var_cmdb_resource_allocation.set_allocation",
                "fields": [
                    {"key": "${KEY}", "type": "object", "description": "集群资源筛选结果对象"},
                    {"key": "${KEY.set_count}", "type": "int", "description": "新增集群数量"},
                    {"key": "${KEY._module}", "type": "list", "description": "集群下的模块信息列表，元素类型为字典，键为模块名，值为模块下的主机列"},
                    {"key": "${KEY.flat__ip_list}", "type": "string", "description": "本次操作创建的所有集群下的主机（去重后），用 ',' 连接"},
                    {
                        "key": "${KEY.flat__verbose_ip_list}",
                        "type": "string",
                        "description": "返回的是本次操作创建的所有集群下的主机（未去重），用 ',' 连接",
                    },
                    {
                        "key": "${KEY.flat__verbose_ip_module_list}",
                        "type": "string",
                        "description": "本次操作创建的所有模块名称，格式为set_name>module_name，用 ',' 连接",
                    },
                ],
            },
        )

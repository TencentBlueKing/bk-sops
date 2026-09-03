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
from django.test import TestCase

from packages.bkapi.bk_nodemgr.client import (
    Client,
    Group,
    NodemgrRequestContextBuilder,
)


class NodemgrRequestContextBuilderTestCase(TestCase):
    """NodemgrRequestContextBuilder.build_data: 空 dict 也必须作为 body 下发"""

    def setUp(self):
        self.builder = NodemgrRequestContextBuilder()

    def test_data_none_does_nothing(self):
        context = {"method": "POST"}
        self.builder.build_data(context, data=None)
        self.assertNotIn("json", context)
        self.assertNotIn("params", context)

    def test_empty_dict_post_becomes_json(self):
        """父类用 `if not data` 会漏掉空 dict; 此处必须保留空 body"""
        context = {"method": "POST"}
        self.builder.build_data(context, data={})
        self.assertEqual(context["json"], {})

    def test_non_empty_post_becomes_json(self):
        context = {"method": "POST"}
        self.builder.build_data(context, data={"a": 1})
        self.assertEqual(context["json"], {"a": 1})

    def test_get_merges_params(self):
        context = {"method": "GET", "params": {"x": 1}}
        self.builder.build_data(context, data={"a": 1})
        self.assertEqual(context["params"], {"a": 1, "x": 1})


class NodemgrSdkClientTestCase(TestCase):
    """SDK Client / Group 的元信息与资源路径"""

    def test_client_api_name_and_build_class(self):
        self.assertEqual(Client._api_name, "bk-nodemgr")
        self.assertEqual(Client._build_class, NodemgrRequestContextBuilder)

    def test_resource_paths(self):
        group = Group()
        # 关键路径参数形式 {node_role} 与拼写正确的 networkunit_recommend
        cases = {
            "networkarea_list": ("POST", "/api/v3/topo/networkarea/list"),
            "networkunit_list": ("POST", "/api/v3/topo/networkunit/list/brief"),
            "host_list": ("POST", "/api/v3/topo/host/list"),
            "networkunit_recommend": ("POST", "/api/v3/topo/networkunit/recommend_by_network_segment"),
            "package_list": ("POST", "/api/v3/package/release/{node_role}/list/brief"),
            "package_distinct": ("POST", "/api/v3/package/release/{node_role}/distinct"),
            "public_key_get": ("POST", "/api/v3/cipher/rsa/get_public_key"),
            "node_install_check": ("POST", "/api/v3/node/{node_role}/install_check"),
            "node_install": ("POST", "/api/v3/node/{node_role}/install"),
            "node_upgrade": ("POST", "/api/v3/node/{node_role}/upgrade"),
            "node_restart": ("POST", "/api/v3/node/{node_role}/restart"),
            "node_reconfig": ("POST", "/api/v3/node/{node_role}/reconfig"),
            "node_uninstall": ("POST", "/api/v3/node/{node_role}/uninstall"),
            "plugin_install": ("POST", "/api/v3/plugin/install"),
            "plugin_uninstall": ("POST", "/api/v3/plugin/uninstall"),
            "plugin_list": ("POST", "/api/v3/plugin/list"),
            "node_workflow_operation_list": ("POST", "/api/v3/node/workflow/operation/list"),
            "plugin_workflow_operation_list": ("POST", "/api/v3/plugin/workflow/operation/list"),
            "node_workflow_operation_instance_log_get": ("POST", "/api/v3/node/workflow/operation/instance/log/get"),
            "plugin_workflow_operation_instance_log_get": (
                "POST",
                "/api/v3/plugin/workflow/operation/instance/log/get",
            ),
        }
        for name, (method, path) in cases.items():
            operation = getattr(group, name)
            self.assertEqual(operation.method, method, name)
            self.assertEqual(operation.path, path, name)

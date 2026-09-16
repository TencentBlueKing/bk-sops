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
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from api.collections.nodemgr import BKNodemgrClient

ENDPOINT_TMPL = "http://bkapi.test/api/{api_name}"


@override_settings(
    APP_CODE="test_app",
    SECRET_KEY="test_secret",
    BK_API_URL_TMPL=ENDPOINT_TMPL,
)
class BKNodemgrClientEndpointTestCase(TestCase):
    """BKNodemgrClient 的 endpoint 解析与 header 注入"""

    @patch("api.collections.nodemgr.translation.get_language", return_value="zh-cn")
    def test_endpoint_resolution(self, _):
        client = BKNodemgrClient(username="user1", tenant_id="tenant-1", stage="prod")
        self.assertEqual(client._get_endpoint(), "http://bkapi.test/api/bk-nodemgr/prod")

    def test_missing_endpoint_raises(self):
        with override_settings(BK_API_URL_TMPL=""):
            with patch("api.collections.nodemgr.env.BK_APIGW_URL_TMPL", ""):
                with self.assertRaises(RuntimeError):
                    BKNodemgrClient(username="user1")

    @patch("api.collections.nodemgr.translation.get_language", return_value="zh-cn")
    def test_auth_tenant_language_headers(self, _):
        client = BKNodemgrClient(username="user1", tenant_id="tenant-1", stage="prod")

        # 认证信息: app code/secret + username
        self.assertEqual(
            client.session.auth.auth,
            {"bk_app_code": "test_app", "bk_app_secret": "test_secret", "bk_username": "user1"},
        )
        # 多租户与语言 header
        self.assertEqual(client.session.headers["X-Bk-Tenant-Id"], "tenant-1")
        self.assertEqual(client.session.headers["blueking-language"], "zh-cn")

    @patch("api.collections.nodemgr.translation.get_language", return_value="zh-cn")
    def test_no_username_no_tenant(self, _):
        client = BKNodemgrClient(stage="prod")
        # 未传 username 时不注入 bk_username
        self.assertNotIn("bk_username", client.session.auth.auth)
        # 未传 tenant_id 时不注入租户头
        self.assertNotIn("X-Bk-Tenant-Id", client.session.headers)
        # 语言头仍然注入
        self.assertEqual(client.session.headers["blueking-language"], "zh-cn")


@override_settings(
    APP_CODE="test_app",
    SECRET_KEY="test_secret",
    BK_API_URL_TMPL=ENDPOINT_TMPL,
)
class BKNodemgrClientMethodsTestCase(TestCase):
    """BKNodemgrClient 各 facade 方法的请求体构造"""

    def _make_client(self):
        client = BKNodemgrClient(username="user1", tenant_id="tenant-1", stage="prod")
        client.api = MagicMock()
        return client

    def test_networkarea_list(self):
        client = self._make_client()
        client.networkarea_list(offset=10, limit=20)
        client.api.networkarea_list.assert_called_once_with(
            data={"page": {"offset": 10, "limit": 20}}
        )

    def test_networkunit_list(self):
        client = self._make_client()
        client.networkunit_list(networkarea_id=7, offset=0, limit=100)
        client.api.networkunit_list.assert_called_once_with(
            data={
                "page": {"offset": 0, "limit": 100},
                "exact_include_conditions": {"bk_networkarea_id": [7]},
            }
        )

    def test_host_list(self):
        client = self._make_client()
        client.host_list(
            biz_id=2, networkarea_id=3, ipv4_list=["1.1.1.1"], ipv6_list=["fe80::1"], offset=1, limit=10
        )
        client.api.host_list.assert_called_once_with(
            data={
                "page": {"offset": 1, "limit": 10},
                "exact_include_conditions": {"bk_biz_id": [2], "bk_networkarea_id": [3]},
                "fuzzy_include_conditions": {
                    "bk_host_innerip": ["1.1.1.1"],
                    "bk_host_innerip_v6": ["fe80::1"],
                },
            }
        )

    def test_host_list_default_empty_lists(self):
        client = self._make_client()
        client.host_list(biz_id=2, networkarea_id=3)
        _, kwargs = client.api.host_list.call_args
        self.assertEqual(
            kwargs["data"]["fuzzy_include_conditions"],
            {"bk_host_innerip": [], "bk_host_innerip_v6": []},
        )

    def test_package_list_with_plugin_name(self):
        client = self._make_client()
        client.package_list(node_role="plugin", plugin_pkg_name="bkmonitorbeat", offset=5, limit=50)
        client.api.package_list.assert_called_once_with(
            data={
                "page": {"offset": 5, "limit": 50},
                "generation": 2,
                "exact_include_conditions": {"enabled": [True], "name": ["bkmonitorbeat"]},
            },
            path_params={"node_role": "plugin"},
        )

    def test_package_list_without_plugin_name(self):
        client = self._make_client()
        client.package_list(node_role="agent")
        _, kwargs = client.api.package_list.call_args
        self.assertEqual(kwargs["data"]["exact_include_conditions"]["name"], [])
        self.assertEqual(kwargs["path_params"], {"node_role": "agent"})

    def test_package_distinct(self):
        client = self._make_client()
        client.package_distinct(node_role="proxy")
        client.api.package_distinct.assert_called_once_with(
            data={
                "generation": 2,
                "exact_include_conditions": {"enabled": [True]},
                "distinct_field": {"os_type": True},
            },
            path_params={"node_role": "proxy"},
        )

    def test_public_key_get(self):
        client = self._make_client()
        client.public_key_get()
        client.api.public_key_get.assert_called_once_with(data={})

    def test_networkunit_recommand(self):
        client = self._make_client()
        hosts = [{"bk_networkarea_id": 0, "ip": "1.1.1.1"}]
        client.networkunit_recommand(hosts=hosts)
        client.api.networkunit_recommend.assert_called_once_with(data={"items": hosts})

    def test_networkunit_recommand_default_empty(self):
        client = self._make_client()
        client.networkunit_recommand()
        client.api.networkunit_recommend.assert_called_once_with(data={"items": []})

    def test_node_install_check(self):
        client = self._make_client()
        client.node_install_check(hosts=[{"bk_biz_id": 2}], node_role="proxy")
        client.api.node_install_check.assert_called_once_with(
            data={"host": [{"bk_biz_id": 2}]}, path_params={"node_role": "proxy"}
        )

    def test_node_install(self):
        client = self._make_client()
        client.node_install(hosts=[{"bk_host_id": 1}], node_role="agent")
        client.api.node_install.assert_called_once_with(
            data={"host": [{"bk_host_id": 1}], "target_version": [], "is_manual": False},
            path_params={"node_role": "agent"},
        )

    def test_node_upgrade(self):
        client = self._make_client()
        client.node_upgrade(hosts=[{"bk_host_id": 1}], node_role="proxy")
        client.api.node_upgrade.assert_called_once_with(
            data={"host": [{"bk_host_id": 1}]}, path_params={"node_role": "proxy"}
        )

    def test_node_restart(self):
        client = self._make_client()
        client.node_restart(hosts=[{"bk_host_id": 1}], node_role="agent")
        client.api.node_restart.assert_called_once_with(
            data={"host": [{"bk_host_id": 1}]}, path_params={"node_role": "agent"}
        )

    def test_node_reconfig(self):
        client = self._make_client()
        client.node_reconfig(hosts=[{"bk_host_id": 1}], node_role="agent")
        client.api.node_reconfig.assert_called_once_with(
            data={"host": [{"bk_host_id": 1}]}, path_params={"node_role": "agent"}
        )

    def test_node_uninstall(self):
        client = self._make_client()
        client.node_uninstall(hosts=[{"bk_host_id": 1}], node_role="proxy")
        client.api.node_uninstall.assert_called_once_with(
            data={"host": [{"bk_host_id": 1}]}, path_params={"node_role": "proxy"}
        )

    def test_plugin_install(self):
        client = self._make_client()
        plugins = [{"bk_host_id": 1, "plugin_name": "bkmonitorbeat"}]
        client.plugin_install(plugins=plugins)
        client.api.plugin_install.assert_called_once_with(data={"plugin": plugins})

    def test_plugin_uninstall(self):
        client = self._make_client()
        plugins = [{"bk_host_id": 1, "plugin_name": "bkmonitorbeat"}]
        client.plugin_uninstall(plugins=plugins)
        client.api.plugin_uninstall.assert_called_once_with(data={"plugin": plugins})

    def test_plugin_list(self):
        client = self._make_client()
        client.plugin_list(biz_id=[2, 3], offset=0, limit=500)
        client.api.plugin_list.assert_called_once_with(
            data={
                "page": {"offset": 0, "limit": 500},
                "exact_include_conditions": {"group": ["default"], "visible_biz_ids": [2, 3]},
            }
        )

    def test_plugin_list_defaults(self):
        client = self._make_client()
        client.plugin_list()
        _, kwargs = client.api.plugin_list.call_args
        self.assertEqual(
            kwargs["data"]["exact_include_conditions"],
            {"group": ["default"], "visible_biz_ids": []},
        )

    def test_node_workflow_operation_list(self):
        client = self._make_client()
        client.node_workflow_operation_list(workflow_id="wf-1", page={"offset": 10})
        client.api.node_workflow_operation_list.assert_called_once_with(
            data={"workflow_id": "wf-1", "only_count": False, "page": {"offset": 10, "limit": 500}}
        )

    def test_plugin_workflow_operation_list(self):
        client = self._make_client()
        client.plugin_workflow_operation_list(workflow_id="wf-2")
        client.api.plugin_workflow_operation_list.assert_called_once_with(
            data={"workflow_id": "wf-2", "only_count": False, "page": {"offset": 0, "limit": 500}}
        )

    def test_node_workflow_operation_instance_log_get(self):
        client = self._make_client()
        client.node_workflow_operation_instance_log_get(oper_inst_id=99)
        client.api.node_workflow_operation_instance_log_get.assert_called_once_with(
            data={"oper_inst_id": 99}
        )

    def test_plugin_workflow_operation_instance_log_get(self):
        client = self._make_client()
        client.plugin_workflow_operation_instance_log_get(oper_inst_id=100)
        client.api.plugin_workflow_operation_instance_log_get.assert_called_once_with(
            data={"oper_inst_id": 100}
        )

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

from django.test import TestCase
import ujson as json

import env
from pipeline_plugins.components.query.sites.open import nodemgr as nodemgr_view

CLIENT_TARGET = "pipeline_plugins.components.query.sites.open.nodemgr.BKNodemgrClient"
HANDLE_API_ERROR = "pipeline_plugins.components.query.sites.open.nodemgr.handle_api_error"


def _make_request(username="tester", tenant_id="tenant-1"):
    request = MagicMock()
    request.user.username = username
    request.user.tenant_id = tenant_id
    return request


class GetLoginInfoTestCase(TestCase):
    def test_invalid_env_falls_back_to_default(self):
        with patch.object(env, "BK_NODEMGR_DEFAULT_LOGIN_INFO", "not-a-json"):
            result = nodemgr_view.get_login_info()
        self.assertEqual(result, nodemgr_view.NODEMGR_DEFAULT_LOGIN_INFO)
        self.assertIn("linux", result)


class NodemgrQueryViewTestCase(TestCase):
    def _mock_client(self, **methods):
        client = MagicMock()
        for name, value in methods.items():
            setattr(client, name, MagicMock(return_value=value))
        return client

    def test_nodemgr_get_networkarea_success(self):
        client = self._mock_client(
            networkarea_list={
                "code": 0,
                "data": {
                    "items": [
                        {"bk_networkarea_id": 2, "bk_networkarea_name": "area2"},
                        {"bk_networkarea_id": 1, "bk_networkarea_name": "area1"},
                    ]
                },
            }
        )
        with patch(CLIENT_TARGET, return_value=client):
            response = nodemgr_view.nodemgr_get_networkarea(_make_request())
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        # 按 id 排序
        self.assertEqual([item["id"] for item in data["data"]], [1, 2])
        self.assertEqual(data["data"][0]["text"], "[1] area1")

    def test_nodemgr_get_networkarea_pagination(self):
        """覆盖 offset += limit 的分页分支"""
        client = self._mock_client()
        client.networkarea_list = MagicMock(
            side_effect=[
                {
                    "code": 0,
                    "data": {
                        "items": [
                            {"bk_networkarea_id": i, "bk_networkarea_name": f"area{i}"}
                            for i in range(1000)
                        ]
                    },
                },
                {
                    "code": 0,
                    "data": {
                        "items": [{"bk_networkarea_id": 1001, "bk_networkarea_name": "area1001"}]
                    },
                },
            ]
        )
        with patch(CLIENT_TARGET, return_value=client):
            response = nodemgr_view.nodemgr_get_networkarea(_make_request())
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual(len(data["data"]), 1001)
        self.assertEqual(client.networkarea_list.call_count, 2)
        # 第二次 offset 应为 1000
        self.assertEqual(client.networkarea_list.call_args_list[1][1]["offset"], 1000)

    def test_nodemgr_get_networkarea_error(self):
        client = self._mock_client(networkarea_list={"code": 500, "message": "boom"})
        with patch(CLIENT_TARGET, return_value=client), \
             patch(HANDLE_API_ERROR, return_value="handled error"):
            response = nodemgr_view.nodemgr_get_networkarea(_make_request())
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], 500)
        self.assertEqual(data["message"], "handled error")

    def test_nodemgr_get_networkunit_success(self):
        client = self._mock_client(
            networkunit_list={
                "code": 0,
                "data": {
                    "items": [{"bk_networkunit_id": 5, "bk_networkunit_name": "unit5"}]
                },
            }
        )
        with patch(CLIENT_TARGET, return_value=client):
            response = nodemgr_view.nodemgr_get_networkunit(_make_request(), networkarea_id="3")
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual(data["data"][0]["id"], 5)
        client.networkunit_list.assert_called_once_with(networkarea_id=3, offset=0, limit=1000)

    def test_nodemgr_get_os_type_success(self):
        client = self._mock_client(
            package_distinct={"code": 0, "data": {"os_type": ["linux", "windows"]}}
        )
        with patch(CLIENT_TARGET, return_value=client), \
             patch.object(env, "BK_NODEMGR_DEFAULT_LOGIN_INFO", ""):
            response = nodemgr_view.nodemgr_get_os_type(_make_request(), node_role="agent")
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual([item["value"] for item in data["data"]], ["linux", "windows"])
        # default_info 兜底使用默认登录信息
        self.assertEqual(data["data"][0]["default_info"]["user"], "root")

    def test_nodemgr_get_release_version_success(self):
        client = self._mock_client(
            package_list={
                "code": 0,
                "data": {"items": [{"version": "1.0.0"}, {"version": "2.0.0"}, {"version": "1.0.0"}]},
            }
        )
        with patch(CLIENT_TARGET, return_value=client):
            response = nodemgr_view.nodemgr_get_release_version(_make_request(), node_role="agent")
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        # 去重 + 倒序
        self.assertEqual([item["value"] for item in data["data"]], ["2.0.0", "1.0.0"])

    def test_nodemgr_get_plugin_success(self):
        client = self._mock_client(
            plugin_list={"code": 0, "data": {"items": [{"name": "bkmonitorbeat", "id": 1}]}}
        )
        with patch(CLIENT_TARGET, return_value=client):
            response = nodemgr_view.nodemgr_get_plugin(_make_request(), biz_id="2")
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual(data["data"][0]["value"], "bkmonitorbeat")
        client.plugin_list.assert_called_once_with(biz_id=[2], offset=0, limit=500)

    def test_nodemgr_get_plugin_version_success(self):
        client = self._mock_client(
            package_list={
                "code": 0,
                "data": {"items": [{"version": "1.0.0"}, {"version": "1.1.0"}]},
            }
        )
        with patch(CLIENT_TARGET, return_value=client):
            response = nodemgr_view.nodemgr_get_plugin_version(
                _make_request(), plugin_pkg_name="bkmonitorbeat"
            )
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertEqual([item["value"] for item in data["data"]], ["1.1.0", "1.0.0"])
        client.package_list.assert_called_once_with(
            node_role="plugin", offset=0, limit=1000, plugin_pkg_name="bkmonitorbeat"
        )

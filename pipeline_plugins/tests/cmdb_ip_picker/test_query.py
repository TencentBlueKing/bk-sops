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

import json

from django.test import RequestFactory, TestCase
from mock import MagicMock, Mock, patch

from pipeline_plugins.cmdb_ip_picker.query import (
    cmdb_get_mainline_object_topo,
    cmdb_search_dynamic_group,
    cmdb_search_host,
    cmdb_search_topo_tree,
    format_agent_ip,
)


class FormatAgentIpTestCase(TestCase):
    """测试 format_agent_ip 函数"""

    def test_format_agent_ip_success(self):
        """测试成功格式化agent IP数据"""
        data = [
            {"bk_host_id": 1, "bk_host_innerip": "10.0.0.1"},
            {"bk_host_id": 2, "bk_host_innerip": "10.0.0.2"},
            {"bk_host_id": 3, "bk_host_innerip": "10.0.0.3"},
        ]
        bk_biz_id = 2

        result = format_agent_ip(data, bk_biz_id=bk_biz_id)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], {"host_id": 1, "meta": {"bk_biz_id": 2, "scope_type": "biz", "scope_id": 2}})
        self.assertEqual(result[1]["host_id"], 2)
        self.assertEqual(result[2]["host_id"], 3)

    def test_format_agent_ip_empty_data(self):
        """测试空数据"""
        result = format_agent_ip([], bk_biz_id=2)
        self.assertEqual(result, [])


class CmdbSearchTopoTreeTestCase(TestCase):
    """测试 cmdb_search_topo_tree 函数"""

    def setUp(self):
        self.factory = RequestFactory()
        self.username = "test_user"
        self.biz_cc_id = 2
        self.tenant_id = "system"

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_cmdb_topo_tree")
    def test_cmdb_search_topo_tree_success(self, mock_get_topo):
        """测试成功获取拓扑树"""
        mock_topo_data = {
            "result": True,
            "data": [
                {
                    "bk_inst_id": 2,
                    "bk_inst_name": "业务1",
                    "bk_obj_id": "biz",
                    "child": [{"bk_inst_id": 3, "bk_inst_name": "空闲机池", "bk_obj_id": "set", "child": []}],
                }
            ],
            "message": "",
        }
        mock_get_topo.return_value = mock_topo_data

        request = self.factory.get(f"/pipeline/cmdb_search_topo_tree/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_topo_tree(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        self.assertEqual(response_data["data"], mock_topo_data["data"])
        mock_get_topo.assert_called_once_with(self.tenant_id, self.username, self.biz_cc_id)

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_cmdb_topo_tree")
    def test_cmdb_search_topo_tree_failure(self, mock_get_topo):
        """测试获取拓扑树失败"""
        mock_topo_data = {"result": False, "data": [], "message": "获取拓扑树失败"}
        mock_get_topo.return_value = mock_topo_data

        request = self.factory.get(f"/pipeline/cmdb_search_topo_tree/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_topo_tree(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["result"])
        self.assertEqual(response_data["message"], "获取拓扑树失败")


class CmdbGetMainlineObjectTopoTestCase(TestCase):
    """测试 cmdb_get_mainline_object_topo 函数"""

    def setUp(self):
        self.factory = RequestFactory()
        self.username = "test_user"
        self.biz_cc_id = 2
        self.tenant_id = "system"

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_get_mainline_object_topo_success(self, mock_get_client):
        """测试成功获取主线拓扑模型"""
        mock_topo_data = [
            {"bk_obj_id": "biz", "bk_obj_name": "业务"},
            {"bk_obj_id": "set", "bk_obj_name": "集群"},
            {"bk_obj_id": "module", "bk_obj_name": "模块"},
            {"bk_obj_id": "host", "bk_obj_name": "主机"},
        ]

        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo.return_value = {
            "result": True,
            "code": 0,
            "data": mock_topo_data,
            "message": "",
        }
        mock_get_client.return_value = mock_client

        request = self.factory.get(f"/pipeline/cmdb_get_mainline_object_topo/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_get_mainline_object_topo(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])

        # 验证host被修改为IP
        host_obj = [obj for obj in response_data["data"] if obj["bk_obj_id"] == "host"][0]
        self.assertEqual(host_obj["bk_obj_name"], "IP")

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_get_mainline_object_topo_failure(self, mock_get_client):
        """测试获取主线拓扑模型失败"""
        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo.return_value = {
            "result": False,
            "code": 500,
            "data": [],
            "message": "API调用失败",
        }
        mock_get_client.return_value = mock_client

        request = self.factory.get(f"/pipeline/cmdb_get_mainline_object_topo/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_get_mainline_object_topo(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.logger")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_get_mainline_object_topo_auth_fail(self, mock_get_client, mock_logger):
        """测试权限验证失败"""
        from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE

        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo.return_value = {
            "result": False,
            "code": HTTP_AUTH_FORBIDDEN_CODE,
            "data": [],
            "message": "权限不足",
            "permission": [],
        }
        mock_get_client.return_value = mock_client

        request = self.factory.get(f"/pipeline/cmdb_get_mainline_object_topo/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        from iam.exceptions import RawAuthFailedException

        with self.assertRaises(RawAuthFailedException):
            cmdb_get_mainline_object_topo(request, self.biz_cc_id)


class CmdbSearchDynamicGroupTestCase(TestCase):
    """测试 cmdb_search_dynamic_group 函数"""

    def setUp(self):
        self.factory = RequestFactory()
        self.username = "test_user"
        self.biz_cc_id = 2
        self.tenant_id = "system"

    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_request")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_dynamic_group_success(self, mock_get_client, mock_batch_request):
        """测试成功查询动态分组"""
        mock_dynamic_groups = [
            {"id": "group1", "name": "动态分组1", "bk_obj_id": "host", "create_user": "admin"},
            {"id": "group2", "name": "动态分组2", "bk_obj_id": "host", "create_user": "user1"},
            {"id": "group3", "name": "动态分组3", "bk_obj_id": "set", "create_user": "user2"},  # 非host类型，应该被过滤
        ]

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_batch_request.return_value = mock_dynamic_groups

        request = self.factory.get(f"/pipeline/cmdb_search_dynamic_group/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_dynamic_group(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])

        # 验证只返回host类型的动态分组
        self.assertEqual(response_data["data"]["count"], 2)
        self.assertEqual(len(response_data["data"]["info"]), 2)

        # 验证数据格式
        first_group = response_data["data"]["info"][0]
        self.assertIn("id", first_group)
        self.assertIn("name", first_group)
        self.assertIn("create_user", first_group)

    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_request")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_dynamic_group_empty(self, mock_get_client, mock_batch_request):
        """测试查询动态分组返回空结果"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_batch_request.return_value = []

        request = self.factory.get(f"/pipeline/cmdb_search_dynamic_group/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_dynamic_group(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        self.assertEqual(response_data["data"]["count"], 0)
        self.assertEqual(len(response_data["data"]["info"]), 0)

    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_request")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_dynamic_group_only_host_type(self, mock_get_client, mock_batch_request):
        """测试只返回host类型的动态分组"""
        mock_dynamic_groups = [
            {"id": "group1", "name": "set分组", "bk_obj_id": "set", "create_user": "admin"},
            {"id": "group2", "name": "module分组", "bk_obj_id": "module", "create_user": "admin"},
        ]

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_batch_request.return_value = mock_dynamic_groups

        request = self.factory.get(f"/pipeline/cmdb_search_dynamic_group/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_dynamic_group(request, self.biz_cc_id)

        response_data = json.loads(response.content)
        # 所有分组都不是host类型，返回空
        self.assertEqual(response_data["data"]["count"], 0)


class CmdbSearchHostTestCase(TestCase):
    """测试 cmdb_search_host 函数"""

    def setUp(self):
        self.factory = RequestFactory()
        self.username = "test_user"
        self.biz_cc_id = 2
        self.tenant_id = "system"

    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_basic_success(self, mock_get_client, mock_cmdb):
        """测试基本的主机查询成功"""
        # 模拟 CMDB 客户端
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        # 模拟主机信息
        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_name": "host2", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.2"},
                "set": [],
                "module": [],
            },
        ]

        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        self.assertEqual(len(response_data["data"]), 2)
        self.assertEqual(response_data["data"][0]["bk_host_id"], 1)

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_cloud_area_failed(self, mock_get_client):
        """测试查询云区域失败"""
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {"result": False, "code": 500, "message": "查询云区域失败"}
        mock_get_client.return_value = mock_client

        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_topo_filter(self, mock_get_client, mock_cmdb, mock_get_topo):
        """测试带拓扑过滤的主机查询"""
        # 模拟 CMDB 客户端
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        # 模拟拓扑树
        mock_get_topo.return_value = {
            "result": True,
            "data": [
                {
                    "bk_inst_id": 2,
                    "bk_inst_name": "业务1",
                    "bk_obj_id": "biz",
                    "child": [
                        {
                            "bk_inst_id": 3,
                            "bk_inst_name": "集群1",
                            "bk_obj_id": "set",
                            "child": [{"bk_inst_id": 5, "bk_inst_name": "模块1", "bk_obj_id": "module", "child": []}],
                        }
                    ],
                }
            ],
        }

        # 模拟主机信息
        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [{"bk_module_id": 5}],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_name": "host2", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.2"},
                "set": [],
                "module": [{"bk_module_id": 6}],  # 不在拓扑过滤范围内
            },
        ]

        topo_param = json.dumps([{"bk_obj_id": "module", "bk_inst_id": 5}])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?topo={topo_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        # 应该只返回模块ID为5的主机
        self.assertEqual(len(response_data["data"]), 1)
        self.assertEqual(response_data["data"][0]["bk_host_id"], 1)

    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_cloud_field(self, mock_get_client, mock_cmdb):
        """测试查询包含云区域字段的主机"""
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}, {"bk_cloud_id": 1, "bk_cloud_name": "腾讯云"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_name": "host2", "bk_cloud_id": 1, "bk_host_innerip": "10.0.0.2"},
                "set": [],
                "module": [],
            },
        ]

        fields_param = json.dumps(["cloud"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        self.assertEqual(len(response_data["data"]), 2)
        # 验证云区域信息
        self.assertIn("cloud", response_data["data"][0])
        self.assertEqual(response_data["data"][0]["cloud"][0]["bk_inst_name"], "默认区域")
        self.assertEqual(response_data["data"][1]["cloud"][0]["bk_inst_name"], "腾讯云")

    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_set_module_fields(self, mock_get_client, mock_cmdb):
        """测试查询包含集群和模块字段的主机"""
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [{"bk_set_id": 1, "bk_set_name": "集群1"}],
                "module": [{"bk_module_id": 2, "bk_module_name": "模块1"}],
            }
        ]

        fields_param = json.dumps(["set", "module"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        # 验证包含set和module信息
        self.assertIn("set", response_data["data"][0])
        self.assertIn("module", response_data["data"][0])
        self.assertEqual(response_data["data"][0]["set"][0]["bk_set_name"], "集群1")
        self.assertEqual(response_data["data"][0]["module"][0]["bk_module_name"], "模块1")

    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_empty_result(self, mock_get_client, mock_cmdb):
        """测试主机查询返回空结果"""
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {"result": True, "code": 0, "data": {"info": []}}
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = []

        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        self.assertEqual(len(response_data["data"]), 0)

    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_gse_agent_status_ipv6")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_agent_ipv6(self, mock_get_client, mock_cmdb, mock_get_agent_status, mock_settings):
        """测试查询包含agent字段的主机（IPV6模式）"""
        mock_settings.ENABLE_IPV6 = True
        mock_settings.ENABLE_GSE_V2 = False
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {
                    "bk_host_id": 1,
                    "bk_host_name": "host1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "10.0.0.1",
                    "bk_agent_id": "0:10.0.0.1",
                },
                "set": [],
                "module": [],
            },
            {
                "host": {
                    "bk_host_id": 2,
                    "bk_host_name": "host2",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "10.0.0.2",
                    "bk_agent_id": "0:10.0.0.2",
                },
                "set": [],
                "module": [],
            },
        ]

        # 模拟 agent 状态
        mock_get_agent_status.return_value = {"0:10.0.0.1": 1, "0:10.0.0.2": 0}  # 在线  # 离线

        fields_param = json.dumps(["agent"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        # 验证agent状态
        self.assertEqual(response_data["data"][0]["agent"], 1)
        self.assertEqual(response_data["data"][1]["agent"], 0)

    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_gse_agent_status_ipv6")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_agent_ipv6_no_agent_id(
        self, mock_get_client, mock_cmdb, mock_get_agent_status, mock_settings
    ):
        """测试查询包含agent字段的主机（IPV6模式，无agent_id）"""
        mock_settings.ENABLE_IPV6 = True
        mock_settings.ENABLE_GSE_V2 = False
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {
                    "bk_host_id": 1,
                    "bk_host_name": "host1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "10.0.0.1"
                    # 没有 bk_agent_id
                },
                "set": [],
                "module": [],
            },
            {
                "host": {
                    "bk_host_id": 2,
                    "bk_host_name": "host2",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": ""  # 没有ipv4地址
                    # 没有 bk_agent_id
                },
                "set": [],
                "module": [],
            },
        ]

        # 模拟 agent 状态
        mock_get_agent_status.return_value = {"0:10.0.0.1": 1}

        fields_param = json.dumps(["agent"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        # 第一个主机有ip，应该返回agent状态
        self.assertEqual(response_data["data"][0]["agent"], 1)
        # 第二个主机没有ip也没有agent_id，应该是-1（未知）
        self.assertEqual(response_data["data"][1]["agent"], -1)

    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_gse_agent_status_ipv6")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_agent_ipv6_error(
        self, mock_get_client, mock_cmdb, mock_get_agent_status, mock_settings
    ):
        """测试查询agent状态失败（IPV6模式）"""
        mock_settings.ENABLE_IPV6 = True
        mock_settings.ENABLE_GSE_V2 = False
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {
                    "bk_host_id": 1,
                    "bk_host_name": "host1",
                    "bk_cloud_id": 0,
                    "bk_host_innerip": "10.0.0.1",
                    "bk_agent_id": "0:10.0.0.1",
                },
                "set": [],
                "module": [],
            }
        ]

        # 模拟 agent 状态查询失败
        mock_get_agent_status.side_effect = Exception("GSE查询失败")

        fields_param = json.dumps(["agent"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.query.format_agent_data")
    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_execute_func")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_nodeman_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_agent_nodeman(
        self,
        mock_get_client,
        mock_cmdb,
        mock_get_nodeman_client,
        mock_batch_execute,
        mock_format_agent_data,
        mock_settings,
    ):
        """测试查询包含agent字段的主机（节点管理模式）"""
        mock_settings.ENABLE_IPV6 = False
        mock_settings.ENABLE_GSE_V2 = False
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_name": "host2", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.2"},
                "set": [],
                "module": [],
            },
        ]

        # 模拟节点管理客户端
        mock_nodeman_client = MagicMock()
        mock_get_nodeman_client.return_value = mock_nodeman_client

        # 模拟批量执行结果
        mock_batch_execute.return_value = [
            {
                "result": {
                    "result": True,
                    "data": [{"bk_host_id": 1, "bk_agent_alive": 1}, {"bk_host_id": 2, "bk_agent_alive": 0}],
                }
            }
        ]

        # 模拟格式化agent数据
        mock_format_agent_data.return_value = {"0:10.0.0.1": {"bk_agent_alive": 1}, "0:10.0.0.2": {"bk_agent_alive": 0}}

        fields_param = json.dumps(["agent"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        # 验证agent状态
        self.assertEqual(response_data["data"][0]["agent"], 1)
        self.assertEqual(response_data["data"][1]["agent"], 0)

    @patch("pipeline_plugins.cmdb_ip_picker.query.settings")
    @patch("pipeline_plugins.cmdb_ip_picker.query.batch_execute_func")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_nodeman_client_by_username")
    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_agent_nodeman_error(
        self, mock_get_client, mock_cmdb, mock_get_nodeman_client, mock_batch_execute, mock_settings
    ):
        """测试节点管理查询agent失败"""
        mock_settings.ENABLE_IPV6 = False
        mock_settings.ENABLE_GSE_V2 = False
        mock_settings.BK_APIGW_STAGE_NAME = "prod"

        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [],
            }
        ]

        mock_nodeman_client = MagicMock()
        mock_get_nodeman_client.return_value = mock_nodeman_client

        # 模拟节点管理查询失败
        mock_batch_execute.return_value = [{"result": {"result": False, "message": "节点管理查询失败"}}]

        fields_param = json.dumps(["agent"])
        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?fields={fields_param}")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["result"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_host_lock(self, mock_get_client, mock_cmdb):
        """测试查询包含主机锁定状态"""
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_client.api.search_host_lock.return_value = {"result": True, "code": 0, "data": {"1": True, "2": False}}
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [],
            },
            {
                "host": {"bk_host_id": 2, "bk_host_name": "host2", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.2"},
                "set": [],
                "module": [],
            },
        ]

        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?search_host_lock=1")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data["result"])
        # 验证主机锁定状态
        self.assertTrue(response_data["data"][0]["bk_host_lock_status"])
        self.assertFalse(response_data["data"][1]["bk_host_lock_status"])

    @patch("pipeline_plugins.cmdb_ip_picker.query.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.query.get_client_by_username")
    def test_cmdb_search_host_with_host_lock_error(self, mock_get_client, mock_cmdb):
        """测试查询主机锁定状态失败"""
        mock_client = MagicMock()
        mock_client.api.search_cloud_area.return_value = {
            "result": True,
            "code": 0,
            "data": {"info": [{"bk_cloud_id": 0, "bk_cloud_name": "默认区域"}]},
        }
        mock_client.api.search_host_lock.return_value = {"result": False, "code": 500, "message": "查询主机锁定状态失败"}
        mock_get_client.return_value = mock_client

        mock_cmdb.get_business_host_topo.return_value = [
            {
                "host": {"bk_host_id": 1, "bk_host_name": "host1", "bk_cloud_id": 0, "bk_host_innerip": "10.0.0.1"},
                "set": [],
                "module": [],
            }
        ]

        request = self.factory.get(f"/pipeline/cmdb_search_host/{self.biz_cc_id}/?search_host_lock=1")
        request.user = Mock(username=self.username, tenant_id=self.tenant_id)

        response = cmdb_search_host(request, self.biz_cc_id)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["result"])

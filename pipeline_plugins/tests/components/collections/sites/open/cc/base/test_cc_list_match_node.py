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

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.components.collections.sites.open.cc.base import (
    BkObjType,
    cc_list_match_node_inst_id,
    cc_list_select_node_inst_id,
)


class CCListMatchNodeInstIdTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "system"
        self.executor = "executor_token"
        self.biz_cc_id = 2

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__search_biz_inst_topo_fail(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(return_value={"result": False, "message": "search topo error"})
        mock_get_client.return_value = mock_client

        path_list = [["blueking", "job"]]
        result = cc_list_match_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, path_list)

        self.assertFalse(result["result"])
        self.assertIn("search topo error", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__path_not_match(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "bk_inst_id": 2,
                        "bk_inst_name": "blueking",
                        "bk_obj_id": "biz",
                        "child": [
                            {
                                "bk_inst_id": 3,
                                "bk_inst_name": "job",
                                "bk_obj_id": "set",
                                "child": [],
                            }
                        ],
                    }
                ],
            }
        )
        mock_get_client.return_value = mock_client

        path_list = [["blueking", "nonexistent"]]
        result = cc_list_match_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, path_list)

        self.assertFalse(result["result"])
        self.assertIn("拓扑路径", result["message"])
        self.assertIn("不存在", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__single_path_match(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "bk_inst_id": 2,
                        "bk_inst_name": "blueking",
                        "bk_obj_id": "biz",
                        "child": [
                            {
                                "bk_inst_id": 3,
                                "bk_inst_name": "job",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "bk_inst_id": 5,
                                        "bk_inst_name": "module1",
                                        "bk_obj_id": "module",
                                        "child": [],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        )
        mock_get_client.return_value = mock_client

        path_list = [["blueking", "job", "module1"]]
        result = cc_list_match_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, path_list)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], [5])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__multiple_paths_match(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "bk_inst_id": 2,
                        "bk_inst_name": "blueking",
                        "bk_obj_id": "biz",
                        "child": [
                            {
                                "bk_inst_id": 3,
                                "bk_inst_name": "set1",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "bk_inst_id": 5,
                                        "bk_inst_name": "module1",
                                        "bk_obj_id": "module",
                                        "child": [],
                                    }
                                ],
                            },
                            {
                                "bk_inst_id": 4,
                                "bk_inst_name": "set2",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "bk_inst_id": 6,
                                        "bk_inst_name": "module2",
                                        "bk_obj_id": "module",
                                        "child": [],
                                    }
                                ],
                            },
                        ],
                    }
                ],
            }
        )
        mock_get_client.return_value = mock_client

        path_list = [["blueking", "set1", "module1"], ["blueking", "set2"]]
        result = cc_list_match_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, path_list)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], [5, 4])


class CCListSelectNodeInstIdTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "system"
        self.executor = "executor_token"
        self.biz_cc_id = 2

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__invalid_bk_obj_type(self, mock_get_client):
        # Create a mock object with invalid name attribute
        mock_obj_type = MagicMock()
        mock_obj_type.name = "INVALID_TYPE"
        mock_obj_type.value = 999

        path_text = "blueking > job"
        result = cc_list_select_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, mock_obj_type, path_text)

        self.assertFalse(result["result"])
        self.assertIn("拓扑路径", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__get_mainline_object_topo_fail(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo = MagicMock(
            return_value={"result": False, "message": "get mainline error"}
        )
        mock_get_client.return_value = mock_client

        path_text = "blueking > job"
        result = cc_list_select_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, BkObjType.SET, path_text)

        self.assertFalse(result["result"])
        self.assertIn("get mainline error", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_list_match_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__path_depth_mismatch(self, mock_get_client, mock_cc_list_match):
        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {"bk_obj_id": "biz"},
                    {"bk_obj_id": "set"},
                    {"bk_obj_id": "module"},
                    {"bk_obj_id": "host"},
                ],
            }
        )
        mock_get_client.return_value = mock_client

        # SET depth = 2, should have 2 levels, but we give 3
        path_text = "a > b > c"
        result = cc_list_select_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, BkObjType.SET, path_text)

        self.assertFalse(result["result"])
        self.assertIn("不匹配", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_list_match_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__normal_match(self, mock_get_client, mock_cc_list_match):
        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {"bk_obj_id": "biz"},
                    {"bk_obj_id": "set"},
                    {"bk_obj_id": "module"},
                    {"bk_obj_id": "host"},
                ],
            }
        )
        mock_get_client.return_value = mock_client
        mock_cc_list_match.return_value = {"result": True, "data": [10, 20]}

        # SET depth = 2, should have 2 levels
        path_text = "blueking > set1\nblueking > set2"
        result = cc_list_select_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, BkObjType.SET, path_text)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], [10, 20])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_list_match_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__auto_complete_biz_name(self, mock_get_client, mock_cc_list_match):
        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {"bk_obj_id": "biz"},
                    {"bk_obj_id": "set"},
                    {"bk_obj_id": "module"},
                    {"bk_obj_id": "host"},
                ],
            }
        )
        mock_get_client.return_value = mock_client
        mock_cc_list_match.return_value = {"result": True, "data": [10]}

        # SET depth = 2, give 1 level, auto complete with biz name
        path_text = "set1"
        result = cc_list_select_node_inst_id(
            self.tenant_id, self.executor, self.biz_cc_id, BkObjType.SET, path_text, auto_complete_biz_name="blueking"
        )

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], [10])
        # Should call with auto-completed path
        mock_cc_list_match.assert_called_once()
        called_path_list = mock_cc_list_match.call_args[0][3]
        self.assertEqual(called_path_list, [["blueking", "set1"]])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.cc_list_match_node_inst_id")
    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__match_node_fail(self, mock_get_client, mock_cc_list_match):
        mock_client = MagicMock()
        mock_client.api.get_mainline_object_topo = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {"bk_obj_id": "biz"},
                    {"bk_obj_id": "set"},
                    {"bk_obj_id": "module"},
                    {"bk_obj_id": "host"},
                ],
            }
        )
        mock_get_client.return_value = mock_client
        mock_cc_list_match.return_value = {"result": False, "message": "match failed"}

        path_text = "blueking > set1"
        result = cc_list_select_node_inst_id(self.tenant_id, self.executor, self.biz_cc_id, BkObjType.SET, path_text)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "match failed")

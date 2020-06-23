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

from mock import patch

from django.test import TestCase

from pipeline_plugins.cmdb_ip_picker.utils import get_cmdb_topo_tree


def mock_get_client_by_user(username):
    class MockCC(object):
        def __init__(self, success):
            self.success = success

        def search_biz_inst_topo(self, kwargs):
            return {
                "result": self.success,
                "data": [
                    {
                        "default": 0,
                        "bk_obj_name": "业务",
                        "bk_obj_id": "biz",
                        "child": [
                            {
                                "default": 0,
                                "bk_obj_name": "集群",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "default": 0,
                                        "bk_obj_name": "模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 5,
                                        "bk_inst_name": "test1",
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": "模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 6,
                                        "bk_inst_name": "test2",
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": "模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 7,
                                        "bk_inst_name": "test3",
                                    },
                                ],
                                "bk_inst_id": 3,
                                "bk_inst_name": "set2",
                            },
                            {
                                "default": 0,
                                "bk_obj_name": "集群",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "default": 0,
                                        "bk_obj_name": "模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 8,
                                        "bk_inst_name": "test1",
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": "模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 9,
                                        "bk_inst_name": "test2",
                                    },
                                ],
                                "bk_inst_id": 4,
                                "bk_inst_name": "set3",
                            },
                        ],
                        "bk_inst_id": 2,
                        "bk_inst_name": "蓝鲸",
                    }
                ],
                "message": "error",
            }

        def get_biz_internal_module(self, kwargs):
            return {
                "result": self.success,
                "data": {
                    "bk_set_id": 2,
                    "bk_set_name": "空闲机池",
                    "module": [
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_module_id": 3,
                            "bk_obj_name": "模块",
                            "bk_module_name": "空闲机",
                        },
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_module_id": 4,
                            "bk_obj_name": "模块",
                            "bk_module_name": "故障机",
                        },
                    ],
                },
                "message": "error",
            }

    class MockClient(object):
        def __init__(self, success):
            self.cc = MockCC(success)

    return MockClient(mock_get_client_by_user.success)


class GetCMDBTopoTreeTestCase(TestCase):
    def setUp(self):
        self.topo_tree = {
            "default": 0,
            "bk_obj_name": "业务",
            "bk_obj_id": "biz",
            "child": [
                {
                    "default": 1,
                    "bk_obj_name": "集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_inst_id": 3,
                            "bk_obj_name": "模块",
                            "bk_inst_name": "空闲机",
                        },
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_inst_id": 4,
                            "bk_obj_name": "模块",
                            "bk_inst_name": "故障机",
                        },
                    ],
                    "bk_inst_id": 2,
                    "bk_inst_name": "空闲机池",
                },
                {
                    "default": 0,
                    "bk_obj_name": "集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 5,
                            "bk_inst_name": "test1",
                        },
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 6,
                            "bk_inst_name": "test2",
                        },
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 7,
                            "bk_inst_name": "test3",
                        },
                    ],
                    "bk_inst_id": 3,
                    "bk_inst_name": "set2",
                },
                {
                    "default": 0,
                    "bk_obj_name": "集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 8,
                            "bk_inst_name": "test1",
                        },
                        {
                            "default": 0,
                            "bk_obj_name": "模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 9,
                            "bk_inst_name": "test2",
                        },
                    ],
                    "bk_inst_id": 4,
                    "bk_inst_name": "set3",
                },
            ],
            "bk_inst_id": 2,
            "bk_inst_name": "蓝鲸",
        }

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user", mock_get_client_by_user)
    def test__normal(self):
        mock_get_client_by_user.success = True
        topo_tree = get_cmdb_topo_tree("admin", "2", "")
        self.assertTrue(topo_tree["result"])
        self.assertEqual(topo_tree["data"][0], self.topo_tree)

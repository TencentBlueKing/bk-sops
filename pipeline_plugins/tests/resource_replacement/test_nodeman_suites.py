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

from copy import deepcopy

from django.test import TestCase

from pipeline_plugins.resource_replacement import base, suites

from . import base as local_base


class NodemanPluginOperateSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "nodeman_plugin_operate",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "nodeman_host_os_type": {"hook": False, "need_render": True, "value": "linux"},
            "nodeman_host_info": {
                "hook": False,
                "need_render": True,
                "value": {
                    "nodeman_host_input_type": "host_ip",
                    "nodeman_bk_cloud_id": 3,
                    "nodeman_host_ip": "127.0.0.1",
                    "nodeman_host_id": "",
                },
            },
            "nodeman_plugin_operate": {
                "hook": False,
                "need_render": True,
                "value": {
                    "nodeman_op_type": "MAIN_INSTALL_PLUGIN",
                    "nodeman_plugin_type": "official",
                    "nodeman_plugin": "basereport",
                    "nodeman_plugin_version": "10.8.51",
                    "install_config": [],
                },
            },
        },
        "version": "v1.0",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.NodemanPluginOperateSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            10003,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["nodeman_host_info"][
                "value"
            ]["nodeman_bk_cloud_id"],
        )


class NodemanCreateTaskV1SuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "nodeman_create_task",
        "data": {
            "bk_biz_id": {"hook": False, "need_render": True, "value": 2},
            "nodeman_op_target": {
                "hook": False,
                "need_render": True,
                "value": {"nodeman_bk_cloud_id": 3, "nodeman_node_type": "AGENT"},
            },
            "nodeman_op_info": {
                "hook": False,
                "need_render": True,
                "value": {
                    "nodeman_op_type": "INSTALL",
                    "nodeman_ap_id": 2,
                    "nodeman_hosts": [
                        {
                            "inner_ip": "127.0.0.1",
                        }
                    ],
                    "nodeman_ip_str": "",
                },
            },
        },
        "version": "v2.0",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.NodemanCreateTaskSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["bk_biz_id"]["value"],
        )
        self.assertEqual(
            10003,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["nodeman_op_target"][
                "value"
            ]["nodeman_bk_cloud_id"],
        )


class NodemanCreateTaskV3SuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "nodeman_create_task",
        "data": {
            "bk_biz_id": {"hook": False, "need_render": True, "value": 2},
            "nodeman_node_type": {"hook": False, "need_render": True, "value": "AGENT"},
            "nodeman_op_info": {
                "hook": False,
                "need_render": True,
                "value": {
                    "nodeman_op_type": "INSTALL",
                    "nodeman_hosts": [
                        {
                            "nodeman_bk_cloud_id": 2,
                            "nodeman_ap_id": 3,
                            "inner_ip": "127.0.0.1",
                        },
                        {
                            "nodeman_bk_cloud_id": 0,
                            "nodeman_ap_id": 3,
                            "inner_ip": "127.0.0.1",
                        },
                    ],
                    "nodeman_other_hosts": [],
                },
            },
        },
        "version": "v3.0",
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.NodemanCreateTaskSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            1002,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["bk_biz_id"]["value"],
        )
        self.assertEqual(
            [
                {
                    "nodeman_bk_cloud_id": 10002,
                    "nodeman_ap_id": 3,
                    "inner_ip": "127.0.0.1",
                },
                {
                    "nodeman_bk_cloud_id": 0,
                    "nodeman_ap_id": 3,
                    "inner_ip": "127.0.0.1",
                },
            ],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["nodeman_op_info"]["value"][
                "nodeman_hosts"
            ],
        )

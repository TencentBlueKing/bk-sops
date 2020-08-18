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

from django.test import TestCase

from pipeline_web.plugin_management.utils import find_deprecated_plugins_in_spread_tree
from pipeline_web.plugin_management.models import DeprecatedPlugin

TEST_TREE = {
    "name": "通知升级测试",
    "activities": {
        "1": {
            "type": "ServiceActivity",
            "id": "1",
            "name": "act_1",
            "component": {"code": "bk_notify", "data": {}, "version": "legacy"},
        },
        "2": {
            "type": "ServiceActivity",
            "id": "2",
            "name": "act_2",
            "component": {"code": "bk_notify", "data": {}, "version": "v1.0"},
        },
        "3": {  # node without version
            "type": "ServiceActivity",
            "id": "3",
            "name": "act_3",
            "component": {"code": "bk_job", "data": {}},
        },
        "4": {
            "id": "4",
            "type": "SubProcess",
            "name": "subproc 1",
            "pipeline": {
                "activities": {
                    "5": {
                        "type": "ServiceActivity",
                        "id": "5",
                        "name": "act_5",
                        "component": {"code": "bk_notify", "data": {}, "version": "legacy"},
                    },
                    "6": {
                        "type": "ServiceActivity",
                        "id": "6",
                        "name": "act_6",
                        "component": {"code": "bk_notify", "data": {}, "version": "v1.0"},
                    },
                    "7": {  # node without version
                        "type": "ServiceActivity",
                        "id": "7",
                        "name": "act_7",
                        "component": {"code": "bk_job", "data": {}},
                    },
                    "8": {
                        "id": "8",
                        "type": "SubProcess",
                        "name": "subproc 2",
                        "pipeline": {
                            "activities": {
                                "9": {
                                    "type": "ServiceActivity",
                                    "id": "9",
                                    "name": "act_9",
                                    "component": {"code": "bk_notify", "data": {}, "version": "legacy"},
                                },
                                "10": {
                                    "type": "ServiceActivity",
                                    "id": "10",
                                    "name": "act_10",
                                    "component": {"code": "bk_notify", "data": {}, "version": "v1.0"},
                                },
                                "11": {  # node without version
                                    "type": "ServiceActivity",
                                    "id": "11",
                                    "name": "act_11",
                                    "component": {"code": "bk_job", "data": {}},
                                },
                            },
                            "constants": {},
                        },
                    },
                },
                "constants": {
                    "${bk_notify_title}": {"key": "${bk_notify_title}", "name": "var_4", "custom_type": ""},
                    "${input}": {"key": "${input}", "name": "var_5", "custom_type": "input"},
                    "${ip}": {"key": "${ip}", "name": "var_6", "custom_type": "ip", "version": "legacy"},
                },
            },
        },
    },
    "constants": {
        "${bk_notify_title}": {"key": "${bk_notify_title}", "name": "var_1", "custom_type": ""},
        "${input}": {"key": "${input}", "name": "var_2", "custom_type": "input"},
        "${ip}": {"key": "${ip}", "name": "var_3", "custom_type": "ip", "version": "legacy"},
    },
}


class FindDeprecatedPluginInSpreadTreeTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None

        DeprecatedPlugin.objects.create(
            code="bk_notify",
            version="legacy",
            type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT,
            phase=DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="bk_notify",
            version="v1.0",
            type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT,
            phase=DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="bk_job",
            version="legacy",
            type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT,
            phase=DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="ip",
            version="legacy",
            type=DeprecatedPlugin.PLUGIN_TYPE_VARIABLE,
            phase=DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
        )

    def tearDown(self):
        DeprecatedPlugin.objects.all().delete()

    def test__without_deprecated_plugins_exist(self):
        DeprecatedPlugin.objects.all().delete()

        dp_check = find_deprecated_plugins_in_spread_tree(TEST_TREE)
        self.assertEqual(dp_check, {"found": False, "plugins": {"activities": [], "variables": []}})

    def test__without_phases_param(self):
        dp_check = find_deprecated_plugins_in_spread_tree(TEST_TREE)
        self.assertEqual(
            dp_check,
            {
                "found": True,
                "plugins": {
                    "activities": [
                        {"id": "1", "name": "act_1", "component": "bk_notify", "version": "legacy", "subprocess": None},
                        {
                            "id": "5",
                            "name": "act_5",
                            "component": "bk_notify",
                            "version": "legacy",
                            "subprocess": "subproc 1",
                        },
                        {
                            "id": "9",
                            "name": "act_9",
                            "component": "bk_notify",
                            "version": "legacy",
                            "subprocess": "subproc 2",
                        },
                    ],
                    "variables": [
                        {"key": "${ip}", "name": "var_3", "custom_type": "ip", "version": "legacy", "subprocess": None},
                        {
                            "key": "${ip}",
                            "name": "var_6",
                            "custom_type": "ip",
                            "version": "legacy",
                            "subprocess": "subproc 1",
                        },
                    ],
                },
            },
        )

    def test__with_phases_param(self):
        dp_check = find_deprecated_plugins_in_spread_tree(
            TEST_TREE, [DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED, DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED]
        )
        self.assertEqual(
            dp_check,
            {
                "found": True,
                "plugins": {
                    "activities": [
                        {"id": "1", "name": "act_1", "component": "bk_notify", "version": "legacy", "subprocess": None},
                        {"id": "2", "name": "act_2", "component": "bk_notify", "version": "v1.0", "subprocess": None},
                        {"id": "3", "name": "act_3", "component": "bk_job", "version": "legacy", "subprocess": None},
                        {
                            "id": "5",
                            "name": "act_5",
                            "component": "bk_notify",
                            "version": "legacy",
                            "subprocess": "subproc 1",
                        },
                        {
                            "id": "6",
                            "name": "act_6",
                            "component": "bk_notify",
                            "version": "v1.0",
                            "subprocess": "subproc 1",
                        },
                        {
                            "id": "7",
                            "name": "act_7",
                            "component": "bk_job",
                            "version": "legacy",
                            "subprocess": "subproc 1",
                        },
                        {
                            "id": "9",
                            "name": "act_9",
                            "component": "bk_notify",
                            "version": "legacy",
                            "subprocess": "subproc 2",
                        },
                        {
                            "id": "10",
                            "name": "act_10",
                            "component": "bk_notify",
                            "version": "v1.0",
                            "subprocess": "subproc 2",
                        },
                        {
                            "id": "11",
                            "name": "act_11",
                            "component": "bk_job",
                            "version": "legacy",
                            "subprocess": "subproc 2",
                        },
                    ],
                    "variables": [
                        {"key": "${ip}", "name": "var_3", "custom_type": "ip", "version": "legacy", "subprocess": None},
                        {
                            "key": "${ip}",
                            "name": "var_6",
                            "custom_type": "ip",
                            "version": "legacy",
                            "subprocess": "subproc 1",
                        },
                    ],
                },
            },
        )

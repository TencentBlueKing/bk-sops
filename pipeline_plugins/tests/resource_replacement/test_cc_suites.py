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


class CCHostCustomPropertyChangeSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_host_custom_property_change",
        "data": {
            "cc_ip_list": {
                "hook": False,
                "need_render": True,
                "value": "127.0.0.1\n2:127.0.0.1,3:127.0.0.1\n0:127.0.0.3",
            },
            "cc_custom_property": {"hook": False, "need_render": True, "value": "bk_bak_operator"},
            "cc_hostname_rule": {"hook": False, "need_render": True, "value": []},
            "cc_custom_rule": {"hook": False, "need_render": True, "value": []},
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
        suite: base.Suite = suites.CCHostCustomPropertyChangeSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            "127.0.0.1\n10002:127.0.0.1\n10003:127.0.0.1\n0:127.0.0.3",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_ip_list"]["value"],
        )

    def test_do_by_hook(self):
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_ip_list"]["hook"] = True
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_ip_list"][
            "value"
        ] = "${cc_ip_list}"

        self.PIPELINE_TREE["constants"]["${cc_ip_list}"] = {
            "key": "${cc_ip_list}",
            "desc": "",
            "custom_type": "",
            "source_info": {local_base.FIRST_ACT_ID: ["cc_ip_list"]},
            "value": "2:127.0.0.1, 3:127.0.0.1",
            "show_type": "show",
            "source_type": "component_inputs",
            "validation": "",
            "index": 1,
            "version": "legacy",
            "plugin_code": "",
        }

        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCHostCustomPropertyChangeSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual("10002:127.0.0.1\n10003:127.0.0.1", self.PIPELINE_TREE["constants"]["${cc_ip_list}"]["value"])
        self.assertTrue(self.PIPELINE_TREE["constants"]["${cc_ip_list}"]["resource_replaced"])

        # 验证不重复更新
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual("10002:127.0.0.1\n10003:127.0.0.1", self.PIPELINE_TREE["constants"]["${cc_ip_list}"]["value"])

    def test_do_by_constants(self):
        self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_ip_list"][
            "value"
        ] = "${ip_list}"
        self.PIPELINE_TREE["constants"]["${ip_list}"] = {
            "custom_type": "textarea",
            "desc": "",
            "index": 1,
            "key": "${ip_list}",
            "name": "ip_list",
            "show_type": "show",
            "source_info": {},
            "source_tag": "textarea.textarea",
            "source_type": "custom",
            "value": "127.0.0.1\n1:127.0.0.2",
            "version": "legacy",
        }
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCHostCustomPropertyChangeSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])

        self.assertTrue(self.PIPELINE_TREE["constants"]["${ip_list}"]["resource_replaced"])
        self.assertEqual("127.0.0.1\n10001:127.0.0.2", self.PIPELINE_TREE["constants"]["${ip_list}"]["value"])


class CCCreateSetSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_create_set",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "cc_select_set_parent_method": {"hook": False, "need_render": True, "value": "text"},
            "cc_set_parent_select_topo": {"hook": False, "need_render": True, "value": ["biz_2"]},
            "cc_set_parent_select_text": {"hook": False, "need_render": True, "value": "测试业务"},
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
        suite: base.Suite = suites.CCCreateSetSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP[2]["bk_new_biz_id"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            [f"biz_{local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP[2]['bk_new_biz_id']}"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_parent_select_topo"][
                "value"
            ],
        )
        self.assertEqual(
            "测试业务_new",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_parent_select_text"][
                "value"
            ],
        )


class CCCreateModuleSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_create_module",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "cc_set_select_method": {"hook": False, "need_render": True, "value": "topo"},
            "cc_set_select_topo": {"hook": False, "need_render": True, "value": ["set_97", "set_98"]},
            "cc_set_select_text": {"hook": False, "need_render": True, "value": "测试业务>集群A\n测试业务>集群B"},
            "cc_create_method": {"hook": False, "need_render": True, "value": "category"},
            "cc_module_infos_template": {
                "hook": False,
                "need_render": True,
                "value": [
                    {"cc_service_template": "test_40", "bk_module_type": "普通", "operator": "", "bk_bak_operator": ""}
                ],
            },
        },
        "version": "legacy",
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
        suite: base.Suite = suites.CCCreateModuleSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP[2]["bk_new_biz_id"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            ["set_10097", "set_10098"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_select_topo"][
                "value"
            ],
        )
        self.assertEqual(
            "测试业务_new > 集群A\n测试业务_new > 集群B",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_select_text"][
                "value"
            ],
        )
        self.assertEqual(
            "test_10040",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_module_infos_template"][
                "value"
            ][0]["cc_service_template"],
        )


class CCCreateSetBySetTemplateSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_create_set_by_template",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "cc_select_set_parent_method": {"hook": False, "need_render": True, "value": "topo"},
            "cc_set_parent_select_topo": {"hook": False, "need_render": True, "value": ["biz_2", "set_98"]},
            "cc_set_parent_select_text": {"hook": False, "need_render": True, "value": "测试业务>B"},
            "cc_set_name": {"hook": False, "need_render": True, "value": "A,B"},
            "cc_set_template": {"hook": False, "need_render": True, "value": 25},
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
        suite: base.Suite = suites.CCCreateSetBySetTemplateSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP[2]["bk_new_biz_id"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            ["biz_1002", "set_10098"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_parent_select_topo"][
                "value"
            ],
        )
        self.assertEqual(
            "测试业务_new > B",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_parent_select_text"][
                "value"
            ],
        )
        self.assertEqual(
            10025,
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_template"]["value"],
        )


class CCUpdateModuleSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_update_module",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "cc_module_select_method": {"hook": False, "need_render": True, "value": "text"},
            "cc_module_select_topo": {
                "hook": False,
                "need_render": True,
                "value": ["set_102", "module_232", "module_217"],
            },
            "cc_module_select": {"hook": False, "need_render": True, "value": ["set_102", "module_232", "module_217"]},
            "cc_module_select_text": {"hook": False, "need_render": True, "value": "测试业务>A>B\n测试业务>A1>B1"},
            "cc_module_property": {"hook": False, "need_render": True, "value": "bk_module_name"},
            "cc_module_prop_value": {"hook": False, "need_render": True, "value": "111"},
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
        suite: base.Suite = suites.CCUpdateModuleSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP[2]["bk_new_biz_id"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            ["set_10102", "module_10232", "module_10217"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_module_select_topo"][
                "value"
            ],
        )
        self.assertEqual(
            ["set_10102", "module_10232", "module_10217"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_module_select"]["value"],
        )
        self.assertEqual(
            "测试业务_new > A > B\n测试业务_new > A1 > B1",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_module_select_text"][
                "value"
            ],
        )


class CCEmptySetHostsSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_empty_set_hosts",
        "data": {
            "biz_cc_id": {"hook": False, "need_render": True, "value": 2},
            "cc_set_select_method": {"hook": False, "need_render": True, "value": "text"},
            "cc_set_select_topo": {"hook": False, "need_render": True, "value": ["set_102", 1, "hahaha"]},
            "cc_set_select": {"hook": False, "need_render": True, "value": ["set_1", "custom_102", "error_xxxx"]},
            "cc_set_select_text": {"hook": False, "need_render": True, "value": "测试业务>集群"},
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
        suite: base.Suite = suites.CCEmptySetHostsSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP[2]["bk_new_biz_id"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["biz_cc_id"]["value"],
        )
        self.assertEqual(
            ["set_10102", 1, "hahaha"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_select_topo"][
                "value"
            ],
        )
        self.assertEqual(
            ["set_10001", "custom_10102", "error_xxxx"],
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_select"]["value"],
        )
        self.assertEqual(
            "测试业务_new > 集群",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["cc_set_select_text"][
                "value"
            ],
        )


class CCUpdateSetServiceStatusSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "code": "cc_update_set_service_status",
        "data": {
            "set_select_method": {"hook": False, "need_render": True, "value": "id"},
            "set_attr_id": {"hook": False, "need_render": True, "value": ""},
            "set_list": {"hook": False, "need_render": True, "value": "1,2,3"},
            "set_status": {"hook": False, "need_render": True, "value": "1"},
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
        suite: base.Suite = suites.CCUpdateSetServiceStatusSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do(local_base.FIRST_ACT_ID, self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"])
        self.assertEqual(
            "10001,10002,10003",
            self.PIPELINE_TREE["activities"][local_base.FIRST_ACT_ID]["component"]["data"]["set_list"]["value"],
        )


class CCVarCmdbSetAllocationSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "custom_type": "set_allocation",
        "desc": "",
        "index": 1,
        "key": "${VarCmdbSetAllocation}",
        "name": "VarCmdbSetAllocation",
        "source_info": {},
        "source_tag": "var_cmdb_resource_allocation.set_allocation",
        "source_type": "custom",
        "value": {
            "config": {
                "set_count": "1",
                "set_template_id": "set_102",
                "set_template_name": "test1207",
                "host_resources": [{"id": "set_101", "label": "标准运维"}, {"id": "set_102", "label": "test1207"}],
                "mute_attribute": "",
                "filter_lock": False,
                "shareEqually": "",
                "module_detail": [{"id": 232, "name": "test", "host_count": "1", "reuse_module": ""}],
            },
            "separator": ",",
        },
        "version": "legacy",
        "is_meta": False,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["constants"]["${VarCmdbSetAllocation}"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCVarCmdbSetAllocationSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do("${VarCmdbSetAllocation}", self.PIPELINE_TREE["constants"]["${VarCmdbSetAllocation}"])
        self.assertEqual(
            [{"id": "set_10101", "label": "标准运维"}, {"id": "set_10102", "label": "test1207"}],
            self.PIPELINE_TREE["constants"]["${VarCmdbSetAllocation}"]["value"]["config"]["host_resources"],
        )
        self.assertEqual(
            "set_10102",
            self.PIPELINE_TREE["constants"]["${VarCmdbSetAllocation}"]["value"]["config"]["set_template_id"],
        )
        self.assertEqual(
            [{"id": 10232, "name": "test", "host_count": "1", "reuse_module": ""}],
            self.PIPELINE_TREE["constants"]["${VarCmdbSetAllocation}"]["value"]["config"]["module_detail"],
        )


class CCVarIpPickerVariableSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "custom_type": "ip",
        "desc": "",
        "index": 3,
        "key": "${VarIpPickerVariable}",
        "name": "VarIpPickerVariable",
        "source_info": {},
        "source_tag": "var_ip_picker.ip_picker",
        "source_type": "custom",
        "validation": "",
        "is_condition_hide": "false",
        "pre_render_mako": False,
        "value": {
            "var_ip_method": "custom",
            "var_ip_custom_value": "127.0.0.1\n1:127.0.0.1",
            "var_ip_tree": ["232_127.0.0.1", "module_217", "set_96", "module_218", "module_219"],
        },
        "version": "legacy",
        "is_meta": False,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["constants"]["${VarIpPickerVariable}"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCVarIpPickerVariableSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do("${VarIpPickerVariable}", self.PIPELINE_TREE["constants"]["${VarIpPickerVariable}"])
        self.assertEqual(
            ["10232_127.0.0.1", "module_10217", "set_10096", "module_10218", "module_10219"],
            self.PIPELINE_TREE["constants"]["${VarIpPickerVariable}"]["value"]["var_ip_tree"],
        )
        self.assertEqual(
            "127.0.0.1\n10001:127.0.0.1",
            self.PIPELINE_TREE["constants"]["${VarIpPickerVariable}"]["value"]["var_ip_custom_value"],
        )


class CCVarCmdbIpSelectorSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "custom_type": "ip_selector",
        "desc": "",
        "index": 1,
        "key": "${a}",
        "name": "1",
        "show_type": "show",
        "source_info": {},
        "source_tag": "var_cmdb_ip_selector.ip_selector",
        "source_type": "custom",
        "value": {
            "selectors": ["ip"],
            "topo": [{"bk_inst_id": 20, "bk_obj_id": "module"}, {"bk_inst_id": 39, "bk_obj_id": "set"}],
            "ip": [
                {
                    "bk_cloud_id": 1,
                    "bk_host_innerip": "127.0.0.1",
                    "bk_host_id": 1,
                    "bk_host_name": "xxxxx",
                    "cloud": [{"id": "1", "bk_inst_name": "default area"}],
                    "agent": 1,
                }
            ],
            "filters": [{"field": "host", "value": ["0:127.0.0.1", "127.0.0.2", "1:127.0.0.1"]}],
            "excludes": [{"field": "biz", "value": ["测试业务"]}],
            "with_cloud_id": False,
            "separator": ",",
        },
        "version": "legacy",
        "is_meta": False,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["constants"]["${VarCmdbIpSelector}"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCVarCmdbIpSelectorSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do("${VarCmdbIpSelector}", self.PIPELINE_TREE["constants"]["${VarCmdbIpSelector}"])
        self.assertEqual(
            [{"bk_inst_id": 10020, "bk_obj_id": "module"}, {"bk_inst_id": 10039, "bk_obj_id": "set"}],
            self.PIPELINE_TREE["constants"]["${VarCmdbIpSelector}"]["value"]["topo"],
        )
        self.assertEqual(
            [
                {
                    "bk_cloud_id": 10001,
                    "bk_host_innerip": "127.0.0.1",
                    "bk_host_id": 10001,
                    "bk_host_name": "xxxxx",
                    "cloud": [{"id": "10001", "bk_inst_name": "default area"}],
                    "agent": 1,
                }
            ],
            self.PIPELINE_TREE["constants"]["${VarCmdbIpSelector}"]["value"]["ip"],
        )
        self.assertEqual(
            [{"field": "host", "value": ["0:127.0.0.1", "127.0.0.2", "10001:127.0.0.1"]}],
            self.PIPELINE_TREE["constants"]["${VarCmdbIpSelector}"]["value"]["filters"],
        )

        self.assertEqual(
            [{"field": "biz", "value": ["测试业务_new"]}],
            self.PIPELINE_TREE["constants"]["${VarCmdbIpSelector}"]["value"]["excludes"],
        )


class CCVarCmdbIpFilterSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "custom_type": "ip_filter",
        "desc": "",
        "index": 1,
        "key": "${a}",
        "name": "1",
        "show_type": "show",
        "source_info": {},
        "source_tag": "var_cmdb_ip_filter.ip_filter",
        "source_type": "custom",
        "validation": "",
        "is_condition_hide": "false",
        "pre_render_mako": False,
        "value": {
            "origin_ips": "127.0.0.1\n0:127.0.0.1\n2:127.0.0.1",
            "gse_agent_status": 1,
            "ip_cloud": False,
            "ip_separator": ",",
        },
        "version": "legacy",
        "is_meta": False,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["constants"]["${VarCmdbIpFilter}"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCVarCmdbIpFilterSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do("${VarCmdbIpFilter}", self.PIPELINE_TREE["constants"]["${VarCmdbIpFilter}"])
        self.assertEqual(
            "127.0.0.1\n0:127.0.0.1\n10002:127.0.0.1",
            self.PIPELINE_TREE["constants"]["${VarCmdbIpFilter}"]["value"]["origin_ips"],
        )


class CCVarSetModuleIpSelectorSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "custom_type": "set_module_ip_selector",
        "desc": "",
        "index": 1,
        "key": "${a}",
        "name": "1",
        "show_type": "show",
        "source_info": {},
        "source_tag": "set_module_ip_selector.ip_selector",
        "source_type": "custom",
        "validation": "",
        "is_condition_hide": "false",
        "pre_render_mako": False,
        "value": {
            "var_ip_method": "manual",
            "var_ip_custom_value": "1:127.0.0.1\n2:127.0.0.1",
            "var_ip_select_value": {"var_set": ["直连区域", "管控区域"], "var_module": ["空闲机", "故障机"], "var_module_name": ""},
            "var_ip_manual_value": {"var_manual_set": "all", "var_manual_module": "all", "var_module_name": ""},
            "var_filter_set": "test",
            "var_filter_module": "test",
        },
        "version": "legacy",
        "is_meta": False,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["constants"]["${VarSetModuleIpSelector}"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCVarSetModuleIpSelectorSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do("${VarSetModuleIpSelector}", self.PIPELINE_TREE["constants"]["${VarSetModuleIpSelector}"])
        self.assertEqual(
            "10001:127.0.0.1\n10002:127.0.0.1",
            self.PIPELINE_TREE["constants"]["${VarSetModuleIpSelector}"]["value"]["var_ip_custom_value"],
        )


class CCVarSetModuleSelectorSuiteTestCase(TestCase):
    PIPELINE_TREE = None
    COMPONENT = {
        "custom_type": "set_module_selector",
        "desc": "",
        "index": 1,
        "key": "${a}",
        "name": "1",
        "show_type": "show",
        "source_info": {},
        "source_tag": "var_set_module_selector.set_module_selector",
        "source_type": "custom",
        "validation": "",
        "is_condition_hide": "false",
        "pre_render_mako": False,
        "value": {"bk_set_id": 96, "bk_module_id": [219, 218]},
        "version": "legacy",
        "is_meta": False,
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self) -> None:
        self.PIPELINE_TREE = deepcopy(local_base.PIPELINE_TREE_MOCK_DATA)
        self.PIPELINE_TREE["constants"]["${VarSetModuleSelector}"] = self.COMPONENT
        super().setUp()

    def test_do(self):
        suite_meta: base.SuiteMeta = base.SuiteMeta(
            self.PIPELINE_TREE, offset=10000, old_biz_id__new_biz_info_map=local_base.OLD_BIZ_ID__NEW_BIZ_INFO_MAP
        )
        suite: base.Suite = suites.CCVarSetModuleSelectorSuite(suite_meta, local_base.DBMockHelper(None, "", ""))
        suite.do("${VarSetModuleSelector}", self.PIPELINE_TREE["constants"]["${VarSetModuleSelector}"])
        self.assertEqual(
            10096, self.PIPELINE_TREE["constants"]["${VarSetModuleSelector}"]["value"]["bk_set_id"],
        )
        self.assertEqual(
            [10219, 10218], self.PIPELINE_TREE["constants"]["${VarSetModuleSelector}"]["value"]["bk_module_id"],
        )

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
    cc_format_prop_data,
    cc_format_tree_mode_id,
    cc_format_tree_set_id,
    cc_get_name_id_from_combine_value,
    cc_parse_path_text,
    get_module_set_id,
)


class CCFormatPropDataTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "system"
        self.executor = "executor_token"
        self.obj_id = "host"
        self.prop_id = "bk_os_type"
        self.language = "zh-cn"

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__search_object_attribute_fail(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_object_attribute = MagicMock(return_value={"result": False, "message": "search error"})
        mock_get_client.return_value = mock_client

        result = cc_format_prop_data(self.tenant_id, self.executor, self.obj_id, self.prop_id, self.language)

        self.assertFalse(result["result"])
        self.assertIn("search error", result["message"])

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__normal(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_object_attribute = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "bk_property_id": "bk_os_type",
                        "option": [
                            {"id": "1", "name": "Linux"},
                            {"id": "2", "name": "Windows"},
                        ],
                    },
                    {
                        "bk_property_id": "other_prop",
                        "option": [],
                    },
                ],
            }
        )
        mock_get_client.return_value = mock_client

        result = cc_format_prop_data(self.tenant_id, self.executor, self.obj_id, self.prop_id, self.language)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], {"Linux": "1", "Windows": "2"})

    @patch("pipeline_plugins.components.collections.sites.open.cc.base.get_client_by_username")
    def test__no_match_prop_id(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.api.search_object_attribute = MagicMock(
            return_value={
                "result": True,
                "data": [
                    {
                        "bk_property_id": "other_prop",
                        "option": [],
                    }
                ],
            }
        )
        mock_get_client.return_value = mock_client

        result = cc_format_prop_data(self.tenant_id, self.executor, self.obj_id, self.prop_id, self.language)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"], {})


class CCFormatTreeModeIdTestCase(TestCase):
    def test__none_input(self):
        result = cc_format_tree_mode_id(None)
        self.assertEqual(result, [])

    def test__normal(self):
        front_id_list = ["module_1", "set_2", "3", "module_4"]
        result = cc_format_tree_mode_id(front_id_list)
        self.assertEqual(result, [1, 2, 3, 4])

    def test__with_single_underscore(self):
        front_id_list = ["1", "module_2", "set_3"]
        result = cc_format_tree_mode_id(front_id_list)
        self.assertEqual(result, [1, 2, 3])


class CCFormatTreeSetIdTestCase(TestCase):
    def test__none_input(self):
        result = cc_format_tree_set_id(None)
        self.assertEqual(result, [])

    def test__normal(self):
        front_id_list = ["set_1", "module_2", "3", "set_4"]
        result = cc_format_tree_set_id(front_id_list)
        self.assertEqual(result, [1, 4])

    def test__no_set_prefix(self):
        front_id_list = ["module_1", "2", "3"]
        result = cc_format_tree_set_id(front_id_list)
        self.assertEqual(result, [])

    def test__invalid_set_format(self):
        front_id_list = ["set_1_2", "set_3"]
        result = cc_format_tree_set_id(front_id_list)
        self.assertEqual(result, [3])


class CCGetNameIdFromCombineValueTestCase(TestCase):
    def test__normal(self):
        name, id_val = cc_get_name_id_from_combine_value("test_name_123")
        self.assertEqual(name, "test_name")
        self.assertEqual(id_val, 123)

    def test__name_with_multiple_underscores(self):
        name, id_val = cc_get_name_id_from_combine_value("test_name_with_underscores_456")
        self.assertEqual(name, "test_name_with_underscores")
        self.assertEqual(id_val, 456)

    def test__invalid_id(self):
        name, id_val = cc_get_name_id_from_combine_value("test_name_abc")
        self.assertIsNone(name)
        self.assertIsNone(id_val)

    def test__no_underscore(self):
        name, id_val = cc_get_name_id_from_combine_value("testname")
        self.assertIsNone(name)
        self.assertIsNone(id_val)


class CCParsePathTextTestCase(TestCase):
    def test__single_path(self):
        path_text = "a > b > c > s"
        result = cc_parse_path_text(path_text)
        self.assertEqual(result, [["a", "b", "c", "s"]])

    def test__multiple_paths(self):
        path_text = "a > b > c > s\n   a>v>c\na"
        result = cc_parse_path_text(path_text)
        self.assertEqual(result, [["a", "b", "c", "s"], ["a", "v", "c"], ["a"]])

    def test__with_empty_lines(self):
        path_text = "a > b\n\nc > d\n"
        result = cc_parse_path_text(path_text)
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

    def test__with_spaces(self):
        path_text = "  a  >  b  \n c > d  "
        result = cc_parse_path_text(path_text)
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

    def test__empty_input(self):
        path_text = ""
        result = cc_parse_path_text(path_text)
        self.assertEqual(result, [])

    def test__only_empty_lines(self):
        path_text = "\n\n\n"
        result = cc_parse_path_text(path_text)
        self.assertEqual(result, [])


class GetModuleSetIdTestCase(TestCase):
    def test__find_set_id(self):
        topo_data = [
            {
                "bk_obj_id": "biz",
                "bk_inst_id": 1,
                "child": [
                    {
                        "bk_obj_id": "set",
                        "bk_inst_id": 10,
                        "child": [
                            {"bk_obj_id": "module", "bk_inst_id": 100},
                            {"bk_obj_id": "module", "bk_inst_id": 101},
                        ],
                    }
                ],
            }
        ]
        result = get_module_set_id(topo_data, 100)
        self.assertEqual(result, 10)

    def test__find_in_nested_structure(self):
        topo_data = [
            {
                "bk_obj_id": "biz",
                "bk_inst_id": 1,
                "child": [
                    {
                        "bk_obj_id": "custom",
                        "bk_inst_id": 5,
                        "child": [
                            {
                                "bk_obj_id": "set",
                                "bk_inst_id": 20,
                                "child": [
                                    {"bk_obj_id": "module", "bk_inst_id": 200},
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
        result = get_module_set_id(topo_data, 200)
        self.assertEqual(result, 20)

    def test__module_not_found(self):
        topo_data = [
            {
                "bk_obj_id": "biz",
                "bk_inst_id": 1,
                "child": [
                    {
                        "bk_obj_id": "set",
                        "bk_inst_id": 10,
                        "child": [
                            {"bk_obj_id": "module", "bk_inst_id": 100},
                        ],
                    }
                ],
            }
        ]
        result = get_module_set_id(topo_data, 999)
        self.assertIsNone(result)

    def test__empty_topo_data(self):
        topo_data = []
        result = get_module_set_id(topo_data, 100)
        self.assertIsNone(result)

    def test__no_child(self):
        topo_data = [
            {
                "bk_obj_id": "set",
                "bk_inst_id": 10,
            }
        ]
        result = get_module_set_id(topo_data, 100)
        self.assertIsNone(result)

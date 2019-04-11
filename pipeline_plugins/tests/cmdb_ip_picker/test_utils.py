# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase
from mock import patch
from pipeline_plugins.cmdb_ip_picker.utils import (
    get_modules_id,
    get_modules_of_filters,
    get_modules_of_bk_obj,
    get_objects_of_topo_tree,
    get_cmdb_topo_tree)


from pipeline_plugins.tests.utils import mock_get_client_by_user


class TestGetObjects(TestCase):
    def setUp(self):
        self.topo_tree = {
            "default": 0,
            "bk_obj_name": u"业务",
            "bk_obj_id": "biz",
            "child": [
                {
                    "default": 1,
                    "bk_obj_name": u"集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_inst_id": 3,
                            "bk_obj_name": u"模块",
                            "bk_inst_name": u"空闲机"
                        },
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_inst_id": 4,
                            "bk_obj_name": u"模块",
                            "bk_inst_name": u"故障机"
                        }
                    ],
                    "bk_inst_id": 2,
                    "bk_inst_name": u"空闲机池"
                },
                {
                    "default": 0,
                    "bk_obj_name": u"集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 0,
                            "bk_obj_name": u"模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 5,
                            "bk_inst_name": "test1"
                        },
                        {
                            "default": 0,
                            "bk_obj_name": u"模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 6,
                            "bk_inst_name": "test2"
                        },
                        {
                            "default": 0,
                            "bk_obj_name": u"模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 7,
                            "bk_inst_name": "test3"
                        },
                    ],
                    "bk_inst_id": 3,
                    "bk_inst_name": "set2"
                },
                {
                    "default": 0,
                    "bk_obj_name": u"集群",
                    "bk_obj_id": "set",
                    "child": [
                        {
                            "default": 0,
                            "bk_obj_name": u"模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 8,
                            "bk_inst_name": "test1"
                        },
                        {
                            "default": 0,
                            "bk_obj_name": u"模块",
                            "bk_obj_id": "module",
                            "bk_inst_id": 9,
                            "bk_inst_name": "test2"
                        },
                    ],
                    "bk_inst_id": 4,
                    "bk_inst_name": "set3"
                },
            ],
            "bk_inst_id": 2,
            "bk_inst_name": u"蓝鲸"
        }

    def test_get_modules_id(self):
        modules = [
            {
                "default": 0,
                "bk_obj_name": u"模块",
                "bk_obj_id": "module",
                "bk_inst_id": 8,
                "bk_inst_name": "test1"
            },
            {
                "default": 0,
                "bk_obj_name": u"模块",
                "bk_obj_id": "module",
                "bk_inst_id": 9,
                "bk_inst_name": "test2"
            },
        ]
        self.assertEquals(get_modules_id(modules), [8, 9])

    def test_get_modules_of_filters(self):
        filters_dct = {
            'set': [u"空闲机池", 'set3']
        }
        modules1 = get_modules_of_filters(self.topo_tree, filters_dct)
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules1]), {3, 4, 8, 9})

        filters_dct = {
            'set': [u"空闲机池", 'set3'],
            'module': [u"空闲机", 'test1', 'test2']
        }
        modules2 = get_modules_of_filters(self.topo_tree, filters_dct)
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules2]), {3, 8, 9})

        filters_dct = {
            'module': [u"空闲机", 'test1', 'test2']
        }
        modules2 = get_modules_of_filters(self.topo_tree, filters_dct)
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules2]), {3, 5, 6, 8, 9})

    def test_get_objects_of_topo_tree(self):
        obj_dct = {
            'module': [3, 5, 6],
            'set': [4],
        }
        objects = [
            {
                "default": 1,
                "bk_obj_id": "module",
                "bk_inst_id": 3,
                "bk_obj_name": u"模块",
                "bk_inst_name": u"空闲机"
            },
            {
                "default": 0,
                "bk_obj_name": u"模块",
                "bk_obj_id": "module",
                "bk_inst_id": 5,
                "bk_inst_name": "test1"
            },
            {
                "default": 0,
                "bk_obj_name": u"模块",
                "bk_obj_id": "module",
                "bk_inst_id": 6,
                "bk_inst_name": "test2"
            },
            {
                "default": 0,
                "bk_obj_name": u"集群",
                "bk_obj_id": "set",
                "child": [
                    {
                        "default": 0,
                        "bk_obj_name": u"模块",
                        "bk_obj_id": "module",
                        "bk_inst_id": 8,
                        "bk_inst_name": "test1"
                    },
                    {
                        "default": 0,
                        "bk_obj_name": u"模块",
                        "bk_obj_id": "module",
                        "bk_inst_id": 9,
                        "bk_inst_name": "test2"
                    },
                ],
                "bk_inst_id": 4,
                "bk_inst_name": "set3"
            },
        ]
        self.assertEquals(get_objects_of_topo_tree(self.topo_tree, obj_dct), objects)

    def test_get_modules_of_bk_obj(self):
        modules1 = get_modules_of_bk_obj(self.topo_tree)
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules1]), {3, 4, 5, 6, 7, 8, 9})

        modules2 = get_modules_of_bk_obj(self.topo_tree['child'][2])
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules2]), {8, 9})

        modules3 = get_modules_of_bk_obj(self.topo_tree['child'][2]['child'][1])
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules3]), {9})

    @patch('pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user', mock_get_client_by_user)
    def test_get_cmdb_topo_tree(self):
        mock_get_client_by_user.success = True
        topo_tree = get_cmdb_topo_tree('admin', '2', '')
        self.assertEquals(topo_tree['result'], True)

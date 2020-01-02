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
from mock import patch
from pipeline_plugins.cmdb_ip_picker.utils import (
    get_modules_id,
    get_modules_by_condition,
    get_modules_of_bk_obj,
    get_objects_of_topo_tree,
    get_cmdb_topo_tree,
    process_topo_tree_by_condition,
    format_condition_value,
    build_cmdb_search_host_kwargs,
    get_ip_picker_result
)


from pipeline_plugins.tests.utils import mock_get_client_by_user


class TestGetObjects(TestCase):
    def setUp(self):
        self.username = 'admin'
        self.bk_biz_id = '2'
        self.bk_supplier_account = 0
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

    def test_format_condition_value(self):
        self.assertEquals(format_condition_value(['111', '222']), ['111', '222'])
        self.assertEquals(format_condition_value(['111', '222\n333']), ['111', '222', '333'])
        self.assertEquals(format_condition_value(['', '222\n', ' 333  ']), ['222', '333'])

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

    def test_process_topo_tree_by_condition(self):
        condition = {'group': [1, 3]}
        expected = {
            "default": 0,
            "bk_obj_name": u"业务",
            "bk_obj_id": "biz",
            "child": [],
            "bk_inst_id": 2,
            "bk_inst_name": u"蓝鲸"
        }
        self.assertEquals(process_topo_tree_by_condition(self.topo_tree, condition), expected)

        condition = {'set': [1, 3]}
        self.assertEquals(process_topo_tree_by_condition(self.topo_tree, condition), self.topo_tree)

    def test_get_modules_by_condition(self):
        filters_dct = {
            'set': [u"空闲机池", 'set3']
        }
        modules1 = get_modules_by_condition(self.topo_tree, filters_dct)
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules1]), {3, 4, 8, 9})

        filters_dct = {
            'set': [u"空闲机池", 'set3'],
            'module': [u"空闲机", 'test1', 'test2']
        }
        modules2 = get_modules_by_condition(self.topo_tree, filters_dct)
        self.assertEquals(set([mod['bk_inst_id'] for mod in modules2]), {3, 8, 9})

        filters_dct = {
            'module': [u"空闲机", 'test1', 'test2']
        }
        modules2 = get_modules_by_condition(self.topo_tree, filters_dct)
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
        self.assertTrue(topo_tree['result'])
        self.assertEquals(topo_tree['data'][0], self.topo_tree)

    @patch('pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user', mock_get_client_by_user)
    def test_get_ip_picker_result__boundary_value(self):
        mock_get_client_by_user.success = True
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [],
            'ip': [],
            'filters': [],
            'excludes': [],
        }
        self.assertFalse(
            get_ip_picker_result(self.username,
                                 self.bk_biz_id,
                                 self.bk_supplier_account,
                                 topo_kwargs)['result']
        )

    @patch('pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user', mock_get_client_by_user)
    def test_get_ip_picker_result__selector_topo(self):
        mock_get_client_by_user.success = True
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [
                {'bk_obj_id': 'set', 'bk_inst_id': 2},
            ],
            'ip': [],
            'filters': [],
            'excludes': [],
        }
        ip_data = get_ip_picker_result(self.username,
                                       self.bk_biz_id,
                                       self.bk_supplier_account,
                                       topo_kwargs)['data']
        ip = [host['bk_host_innerip'] for host in ip_data]
        self.assertEquals(ip, ['1.1.1.1'])

        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [
                {'bk_obj_id': 'set', 'bk_inst_id': 3},
                {'bk_obj_id': 'module', 'bk_inst_id': 5},
            ],
            'ip': [],
            'filters': [],
            'excludes': [],
        }
        ip_data = get_ip_picker_result(self.username,
                                       self.bk_biz_id,
                                       self.bk_supplier_account,
                                       topo_kwargs)['data']
        ip = [host['bk_host_innerip'] for host in ip_data]
        self.assertEquals(ip, ['2.2.2.2'])

    @patch('pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user', mock_get_client_by_user)
    def test_get_ip_picker_result__selector_ip(self):
        mock_get_client_by_user.success = True
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['ip'],
            'topo': [],
            'ip': [
                {
                    'bk_host_name': 'host1',
                    'bk_host_id': 2,
                    'agent': 1,
                    'cloud': [
                        {
                            'bk_obj_name': '',
                            'id': '0',
                            'bk_obj_id': 'plat',
                            'bk_obj_icon': '',
                            'bk_inst_id': 0,
                            'bk_inst_name': 'default area'
                        }
                    ],
                    'bk_host_innerip': '1.1.1.1'
                },
                {
                    'bk_host_name': 'host2',
                    'bk_host_id': 2,
                    'agent': 1,
                    'cloud': [
                        {
                            'bk_obj_name': '',
                            'id': '0',
                            'bk_obj_id': 'plat',
                            'bk_obj_icon': '',
                            'bk_inst_id': 0,
                            'bk_inst_name': 'default area'
                        }
                    ],
                    'bk_host_innerip': '2.2.2.2'
                }
            ],
            'filters': [],
            'excludes': [],
        }
        ip_data = get_ip_picker_result(self.username,
                                       self.bk_biz_id,
                                       self.bk_supplier_account,
                                       topo_kwargs)['data']
        ip = [host['bk_host_innerip'] for host in ip_data]
        self.assertEquals(ip, ['1.1.1.1', '2.2.2.2'])

    @patch('pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user', mock_get_client_by_user)
    def test_get_ip_picker_result__filters(self):
        mock_get_client_by_user.success = True
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [
                {'bk_obj_id': 'biz', 'bk_inst_id': 2},
            ],
            'ip': [],
            'filters': [
                {'field': 'set', 'value': ['set2']}
            ],
            'excludes': [],
        }
        ip_data = get_ip_picker_result(self.username,
                                       self.bk_biz_id,
                                       self.bk_supplier_account,
                                       topo_kwargs)['data']
        ip = [host['bk_host_innerip'] for host in ip_data]
        self.assertEquals(ip, ['2.2.2.2'])

    @patch('pipeline_plugins.cmdb_ip_picker.utils.get_client_by_user', mock_get_client_by_user)
    def test_get_ip_picker_result__excludes(self):
        mock_get_client_by_user.success = True
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [
                {'bk_obj_id': 'biz', 'bk_inst_id': 2},
            ],
            'ip': [],
            'filters': [],
            'excludes': [
                {'field': 'set', 'value': ['set2']}
            ],
        }
        ip_data = get_ip_picker_result(self.username,
                                       self.bk_biz_id,
                                       self.bk_supplier_account,
                                       topo_kwargs)['data']
        ip = [host['bk_host_innerip'] for host in ip_data]
        self.assertEquals(ip, ['1.1.1.1'])

    def test_build_cmdb_search_host_kwargs__boundary_value(self):
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [],
            'ip': [],
            'filters': [],
            'excludes': [],
        }
        self.assertFalse(
            build_cmdb_search_host_kwargs(self.bk_biz_id,
                                          self.bk_supplier_account,
                                          topo_kwargs,
                                          self.topo_tree)['result']
        )

        ip_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['ip'],
            'topo': [],
            'ip': [],
            'filters': [],
            'excludes': [],
        }
        self.assertFalse(
            build_cmdb_search_host_kwargs(self.bk_biz_id,
                                          self.bk_supplier_account,
                                          ip_kwargs,
                                          self.topo_tree)['result']
        )

    def test_build_cmdb_search_host_kwargs__selector_topo(self):
        topo_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['topo'],
            'topo': [
                {'bk_obj_id': 'set', 'bk_inst_id': 3},
                {'bk_obj_id': 'module', 'bk_inst_id': 8},
            ],
            'ip': [],
            'filters': [],
            'excludes': [],
        }
        self.assertEquals(
            build_cmdb_search_host_kwargs(self.bk_biz_id,
                                          self.bk_supplier_account,
                                          topo_kwargs,
                                          self.topo_tree)['data'],
            {
                'bk_biz_id': '2',
                'bk_supplier_account': 0,
                'condition': [{
                    'bk_obj_id': 'module',
                    'fields': ['bk_module_id', 'bk_module_name'],
                    'condition': [{
                        'field': 'bk_module_id',
                        'operator': '$in',
                        'value': [5, 6, 7, 8]
                    }]
                }]
            }
        )

    def test_build_cmdb_search_host_kwargs__selector_ip(self):
        ip_kwargs = {
            'bk_biz_id': self.bk_biz_id,
            'selectors': ['ip'],
            'topo': [],
            'ip': [
                {
                    'bk_host_name': 'host1',
                    'bk_host_id': 2,
                    'agent': 1,
                    'cloud': [
                        {
                            'bk_obj_name': '',
                            'id': '0',
                            'bk_obj_id': 'plat',
                            'bk_obj_icon': '',
                            'bk_inst_id': 0,
                            'bk_inst_name': 'default area'
                        }
                    ],
                    'bk_host_innerip': '1.1.1.1'
                },
                {
                    'bk_host_name': 'host2',
                    'bk_host_id': 2,
                    'agent': 1,
                    'cloud': [
                        {
                            'bk_obj_name': '',
                            'id': '0',
                            'bk_obj_id': 'plat',
                            'bk_obj_icon': '',
                            'bk_inst_id': 0,
                            'bk_inst_name': 'default area'
                        }
                    ],
                    'bk_host_innerip': '2.2.2.2'
                }
            ],
            'filters': [],
            'excludes': [],
        }
        self.assertEquals(
            build_cmdb_search_host_kwargs(self.bk_biz_id,
                                          self.bk_supplier_account,
                                          ip_kwargs,
                                          self.topo_tree)['data'],
            {
                'bk_biz_id': '2',
                'bk_supplier_account': 0,
                'condition': [
                    {
                        'bk_obj_id': 'module',
                        'fields': ['bk_module_id', 'bk_module_name'],
                        'condition': []
                    },
                    {
                        'bk_obj_id': 'host',
                        'fields': ['bk_host_id', 'bk_host_innerip', 'bk_host_outerip', 'bk_host_name'],
                        'condition': [{
                            'field': 'bk_host_innerip',
                            'operator': '$in',
                            'value': ['1.1.1.1', '2.2.2.2']
                        }]
                    }
                ]
            }
        )

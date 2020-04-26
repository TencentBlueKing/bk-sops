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

from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from django.test import TestCase
from mock.mock import MagicMock, patch

from auth_backend.resources.migrations.differ import SnapshotDiffer
from auth_backend.tests.mock_path import *  # noqa


class SnapshotDifferTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.snapshot = OrderedDict()
        self.snapshot['system'] = [
            {
                "resource_type_name": "资源A",
                "actions": [
                    {
                        "action_name": "查看",
                        "is_related_resource": True,
                        "action_id": "view"
                    },
                    {
                        "action_name": "编辑",
                        "is_related_resource": True,
                        "action_id": "edit"
                    },
                    {
                        "action_name": "删除",
                        "is_related_resource": True,
                        "action_id": "delete"
                    }
                ],
                "parent_resource_type": "project",
                "resource_type": "resource_a"
            },
            {
                "resource_type_name": "资源B",
                "actions": [
                    {
                        "action_name": "查看",
                        "is_related_resource": True,
                        "action_id": "view"
                    },
                    {
                        "action_name": "删除",
                        "is_related_resource": True,
                        "action_id": "delete"
                    }
                ],
                "parent_resource_type": "project",
                "resource_type": "resource_b"
            },
        ]
        self.snapshot['business'] = [
            {
                "resource_type_name": "资源C",
                "actions": [
                    {
                        "action_name": "查看",
                        "is_related_resource": True,
                        "action_id": "view"
                    },
                    {
                        "action_name": "删除",
                        "is_related_resource": True,
                        "action_id": "delete"
                    }
                ],
                "parent_resource_type": "",
                "resource_type": "resource_c"
            },
        ]

    def test_has_change(self):
        change_differ = SnapshotDiffer(last_snapshot={'a': 1}, snapshot={'a': 2})
        no_change_differ = SnapshotDiffer(last_snapshot={'a': 1}, snapshot={'a': 1})

        self.assertTrue(change_differ.has_change())
        self.assertFalse(no_change_differ.has_change())

    def test_init_diff_operations(self):

        setttings = MagicMock()
        setattr(setttings, 'BK_IAM_SYSTEM_ID', 'BK_IAM_SYSTEM_ID')
        setattr(setttings, 'BK_IAM_SYSTEM_NAME', 'BK_IAM_SYSTEM_NAME')
        setattr(setttings, 'BK_IAM_SYSTEM_DESC', 'BK_IAM_SYSTEM_DESC')
        setattr(setttings, 'BK_IAM_QUERY_INTERFACE', 'BK_IAM_QUERY_INTERFACE')
        setattr(setttings, 'BK_IAM_RELATED_SCOPE_TYPES', 'BK_IAM_RELATED_SCOPE_TYPES')
        setattr(setttings, 'BK_IAM_SYSTEM_MANAGERS', 'BK_IAM_SYSTEM_MANAGERS')
        setattr(setttings, 'BK_IAM_SYSTEM_CREATOR', 'BK_IAM_SYSTEM_CREATOR')

        with patch(MIGRATION_DIFFER_SETTINGS, setttings):
            differ = SnapshotDiffer(last_snapshot=None, snapshot=self.snapshot)
            operations = differ.init_diff_operations()
            expect = [{'data': {'creator': setttings.BK_IAM_SYSTEM_CREATOR,
                                'desc': setttings.BK_IAM_SYSTEM_DESC,
                                'managers': setttings.BK_IAM_SYSTEM_MANAGERS,
                                'query_interface': setttings.BK_IAM_QUERY_INTERFACE,
                                'related_scope_types': setttings.BK_IAM_RELATED_SCOPE_TYPES,
                                'system_id': setttings.BK_IAM_SYSTEM_ID,
                                'system_name': setttings.BK_IAM_SYSTEM_NAME},
                       'operation': 'register_system'},
                      {'data': {'resource_types': [{'actions': [{'action_id': 'view',
                                                                 'action_name': '查看',
                                                                 'is_related_resource': True},
                                                                {'action_id': 'edit',
                                                                 'action_name': '编辑',
                                                                 'is_related_resource': True},
                                                                {'action_id': 'delete',
                                                                 'action_name': '删除',
                                                                 'is_related_resource': True}],
                                                    'parent_resource_type': 'project',
                                                    'resource_type': 'resource_a',
                                                    'resource_type_name': '资源A'},
                                                   {'actions': [{'action_id': 'view',
                                                                 'action_name': '查看',
                                                                 'is_related_resource': True},
                                                                {'action_id': 'delete',
                                                                 'action_name': '删除',
                                                                 'is_related_resource': True}],
                                                    'parent_resource_type': 'project',
                                                    'resource_type': 'resource_b',
                                                    'resource_type_name': '资源B'}],
                                'scope_type': 'system'},
                       'operation': 'batch_upsert_resource_types'},
                      {'data': {'resource_types': [{'actions': [{'action_id': 'view',
                                                                 'action_name': '查看',
                                                                 'is_related_resource': True},
                                                                {'action_id': 'delete',
                                                                 'action_name': '删除',
                                                                 'is_related_resource': True}],
                                                    'parent_resource_type': '',
                                                    'resource_type': 'resource_c',
                                                    'resource_type_name': '资源C'}],
                                'scope_type': 'business'},
                       'operation': 'batch_upsert_resource_types'}, ]
            self.assertEqual(operations, expect)

    def test_diff_operations__init(self):
        differ = SnapshotDiffer(last_snapshot=None, snapshot=self.snapshot)
        return_token = 'TOKEN'
        differ.init_diff_operations = MagicMock(return_value=return_token)
        operations = differ.diff_operations()

        differ.init_diff_operations.assert_called_once()
        self.assertEqual(operations, return_token)

    def test_diff_operations__scope_not_exist(self):
        new_snapshot = {
            'business': [
                {
                    "resource_type_name": "资源C",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "",
                    "resource_type": "resource_c"
                },
            ]
        }
        expect = [{
            'operation': 'delete_resource_type',
            'data': {
                'scope_type': 'system',
                'resource_type': 'resource_a'
            }
        }, {
            'operation': 'delete_resource_type',
            'data': {
                'scope_type': 'system',
                'resource_type': 'resource_b'
            }
        }]

        differ = SnapshotDiffer(last_snapshot=self.snapshot, snapshot=new_snapshot)
        operations = differ.diff_operations()
        self.assertEqual(operations, expect)

    def test_diff_operations__resource_delete(self):
        new_snapshot = {
            'system': [
                {
                    "resource_type_name": "资源A",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "编辑",
                            "is_related_resource": True,
                            "action_id": "edit"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "project",
                    "resource_type": "resource_a"
                },

            ],
            'business': [
                {
                    "resource_type_name": "资源C",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "",
                    "resource_type": "resource_c"
                },
            ]
        }
        expect = [{
            'operation': 'delete_resource_type',
            'data': {
                'scope_type': 'system',
                'resource_type': 'resource_b'
            }
        }]

        differ = SnapshotDiffer(last_snapshot=self.snapshot, snapshot=new_snapshot)
        operations = differ.diff_operations()

        self.assertEqual(expect, operations)

    def test_diff_operations__resource_update(self):
        new_snapshot = {
            'system': [
                {
                    "resource_type_name": "新资源A",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "编辑",
                            "is_related_resource": True,
                            "action_id": "edit"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "project",
                    "resource_type": "resource_a"
                },
                {
                    "resource_type_name": "资源B",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "project",
                    "resource_type": "resource_b"
                },
            ],
            'business': [
                {
                    "resource_type_name": "资源C",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "新删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "",
                    "resource_type": "resource_c"
                },
            ]
        }
        differ = SnapshotDiffer(last_snapshot=self.snapshot, snapshot=new_snapshot)
        expect = [{'data': {'resource_types': [{'actions': [{'action_id': 'view',
                                                             'action_name': '查看',
                                                             'is_related_resource': True},
                                                            {'action_id': 'edit',
                                                             'action_name': '编辑',
                                                             'is_related_resource': True},
                                                            {'action_id': 'delete',
                                                             'action_name': '删除',
                                                             'is_related_resource': True}],
                                                'parent_resource_type': 'project',
                                                'resource_type': 'resource_a',
                                                'resource_type_name': '新资源A'}],
                            'scope_type': 'system'},
                   'operation': 'batch_upsert_resource_types'},
                  {'data': {'resource_types': [{'actions': [{'action_id': 'view',
                                                             'action_name': '查看',
                                                             'is_related_resource': True},
                                                            {'action_id': 'delete',
                                                             'action_name': '新删除',
                                                             'is_related_resource': True}],
                                                'parent_resource_type': '',
                                                'resource_type': 'resource_c',
                                                'resource_type_name': '资源C'}],
                            'scope_type': 'business'},
                   'operation': 'batch_upsert_resource_types'}, ]
        operations = differ.diff_operations()
        self.assertEqual(expect, operations)

    def test_diff_operations__resource_not_change(self):
        differ = SnapshotDiffer(last_snapshot=self.snapshot, snapshot=self.snapshot)
        expect = []
        operations = differ.diff_operations()
        self.assertEqual(expect, operations)

    def test_diff_operations__new_resource(self):
        new_snapshot = {
            'system': [
                {
                    "resource_type_name": "资源A",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "编辑",
                            "is_related_resource": True,
                            "action_id": "edit"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "project",
                    "resource_type": "resource_a"
                },
                {
                    "resource_type_name": "资源B",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "project",
                    "resource_type": "resource_b"
                },
                {
                    "resource_type_name": "资源D",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "project",
                    "resource_type": "resource_d"
                },
            ],
            'business': [
                {
                    "resource_type_name": "资源C",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "",
                    "resource_type": "resource_c"
                },
                {
                    "resource_type_name": "资源E",
                    "actions": [
                        {
                            "action_name": "查看",
                            "is_related_resource": True,
                            "action_id": "view"
                        },
                        {
                            "action_name": "删除",
                            "is_related_resource": True,
                            "action_id": "delete"
                        }
                    ],
                    "parent_resource_type": "",
                    "resource_type": "resource_e"
                },
            ]
        }
        expect = [{'data': {'resource_types': [{'actions': [{'action_id': 'view',
                                                             'action_name': '查看',
                                                             'is_related_resource': True},
                                                            {'action_id': 'delete',
                                                             'action_name': '删除',
                                                             'is_related_resource': True}],
                                                'parent_resource_type': 'project',
                                                'resource_type': 'resource_d',
                                                'resource_type_name': '资源D'}],
                            'scope_type': 'system'},
                   'operation': 'batch_upsert_resource_types'},
                  {'data': {'resource_types': [{'actions': [{'action_id': 'view',
                                                             'action_name': '查看',
                                                             'is_related_resource': True},
                                                            {'action_id': 'delete',
                                                             'action_name': '删除',
                                                             'is_related_resource': True}],
                                                'parent_resource_type': '',
                                                'resource_type': 'resource_e',
                                                'resource_type_name': '资源E'}],
                            'scope_type': 'business'},
                   'operation': 'batch_upsert_resource_types'}, ]

        differ = SnapshotDiffer(last_snapshot=self.snapshot, snapshot=new_snapshot)
        operations = differ.diff_operations()

        self.assertEqual(expect, operations)

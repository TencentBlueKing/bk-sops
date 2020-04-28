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

from gcloud.tasktmpl3 import api


class ApiTestCase(TestCase):
    def test_replace_job_relate_id_in_templates_data(self):
        # for template contain job_var constants

        assert_data = {'activities': {
            'node7ee2048214dbf045e0043fe1f62b': {
                'component': {
                    'code': 'job_execute_task',
                    'data': {
                        'job_global_var': {'hook': False, 'value': []},
                        'job_task_id': {'hook': False,
                                        'value': 82401}}},
                'type': 'ServiceActivity'},
            'node51f27cbf5d61d50b36d1b25b58ed': {
                'component': {
                    'code': 'job_execute_task', 'data': {
                        'job_global_var': {
                            'hook': False,
                            'value': [{
                                'value': '0:1.1.1.1,0:2.2.2.2,0:3.3.3.3',
                                'type': 2,
                                'description': '',
                                'name': 'id-2018112023375235',
                                'id': 71821},
                                {
                                    'value': 'a"bc\'cb\'a',
                                    'type': 1,
                                    'description': '',
                                    'name': 'str1',
                                    'id': 71831},
                                {
                                    'value': 'ctx1',
                                    'type': 1,
                                    'description': 'ctx1',
                                    'name': 'ctx1',
                                    'id': 71841},
                                {
                                    'value': '(a b c)',
                                    'type': 3,
                                    'description': '',
                                    'name': 'aa',
                                    'id': 71851},
                                {
                                    'value': '([A]=a [B]=b [C]=c)',
                                    'type': 4,
                                    'description': '',
                                    'name': 'bb',
                                    'id': 71861},
                                {
                                    'value': 'const_str',
                                    'type': 1,
                                    'description': 'const_str',
                                    'name': 'const_str',
                                    'id': 71901},
                                {
                                    'value': "<script>alert1('xss')</script>",
                                    'type': 1,
                                    'description': '',
                                    'name': 'str2',
                                    'id': 72011}]},
                        'job_task_id': {
                            'hook': False,
                            'value': 82251}}},
                'type': 'ServiceActivity', },
            'node10dfa52df286c92c180398a78a5f': {
                'component': {
                    'code': 'job_execute_task', 'data': {
                        'job_global_var': {'hook': True,
                                           'value': '${job_global_var}'},
                        'job_task_id': {'hook': False, 'value': 10001}}},
                'type': 'ServiceActivity'}},
            'constants': {
                '${job_global_var}': {'value': [
                    {'value': '5', 'type': 1,
                     'name': 'SECONDS', 'id': 11},
                    {'value': '0', 'type': 1,
                     'name': 'EXIT', 'id': 21},
                    {'value': '0:1.1.1.1,0:1.1.1.12,0:1.1.1.17', 'type': 2,
                     'description': 'wewew',
                     'name': 'id-201868163412877', 'id': 31}]}}}

        template_data = {'pipeline_template_data': {
            'template': {
                '1': {'tree': {'activities': {
                    'node7ee2048214dbf045e0043fe1f62b': {
                        'component': {'code': 'job_execute_task', 'data': {
                            'job_global_var': {'hook': False, 'value': []},
                            'job_task_id': {'hook': False, 'value': 8240}}},
                        'type': 'ServiceActivity'},
                    'node51f27cbf5d61d50b36d1b25b58ed': {'component': {'code': 'job_execute_task', 'data': {
                        'job_global_var': {'hook': False, 'value': [{
                            'value': '0:1.1.1.1,0:2.2.2.2,0:3.3.3.3',
                            'type': 2,
                            'description': '',
                            'name': 'id-2018112023375235',
                            'id': 7182},
                            {
                                'value': 'a"bc\'cb\'a',
                                'type': 1,
                                'description': '',
                                'name': 'str1',
                                'id': 7183},
                            {
                                'value': 'ctx1',
                                'type': 1,
                                'description': 'ctx1',
                                'name': 'ctx1',
                                'id': 7184},
                            {
                                'value': '(a b c)',
                                'type': 3,
                                'description': '',
                                'name': 'aa',
                                'id': 7185},
                            {
                                'value': '([A]=a [B]=b [C]=c)',
                                'type': 4,
                                'description': '',
                                'name': 'bb',
                                'id': 7186},
                            {
                                'value': 'const_str',
                                'type': 1,
                                'description': 'const_str',
                                'name': 'const_str',
                                'id': 7190},
                            {
                                'value': "<script>alert1('xss')</script>",
                                'type': 1,
                                'description': '',
                                'name': 'str2',
                                'id': 7201}]},
                        'job_task_id': {'hook': False, 'value': 8225}}}, 'type': 'ServiceActivity', },
                    'node10dfa52df286c92c180398a78a5f': {
                        'component': {
                            'code': 'job_execute_task', 'data': {
                                'job_global_var': {'hook': True,
                                                   'value': '${job_global_var}'},
                                'job_task_id': {'hook': False, 'value': 1000}}},
                        'type': 'ServiceActivity'}}, 'constants': {
                    '${job_global_var}': {
                        'value': [
                            {'value': '5', 'type': 1,
                             'name': 'SECONDS', 'id': 1},
                            {'value': '0', 'type': 1,
                             'name': 'EXIT', 'id': 2},
                            {'value': '0:1.1.1.1,0:1.1.1.12,0:1.1.1.17', 'type': 2,
                             'description': 'wewew',
                             'name': 'id-201868163412877', 'id': 3}]}}}}
            }
        }}

        job_id_map = {1000: {'id': 10001, 'var_id_map': {1: 11, 2: 21, 3: 31}},
                      8225: {'id': 82251,
                             'var_id_map': {7182: 71821,
                                            7183: 71831,
                                            7184: 71841,
                                            7185: 71851,
                                            7186: 71861,
                                            7190: 71901,
                                            7201: 72011}},
                      8240: {'id': 82401, 'var_id_map': {}}}

        api.replace_job_relate_id_in_templates_data(job_id_map, template_data)
        self.assertEqual(template_data['pipeline_template_data']['template']['1']['tree'], assert_data)

        # for template do not have job atom

        assert_data = {'activities': {
            'node7ee2048214dbf045e0043fe1f62b': {
                'component': {'code': 'not_a_job', 'data': {
                    'job_global_var': {'hook': False, 'value': []},
                    'job_task_id': {'hook': False, 'value': 82401}}},
                'type': 'ServiceActivity'},
            'node51f27cbf5d61d50b36d1b25b58ed': {'component': {'code': 'not_a_job', 'data': {}},
                                                 'type': 'ServiceActivity'},
            'node10dfa52df286c92c180398a78a5f': {'component': {'code': 'not_a_job', 'data': {
                'job_global_var': {'hook': True,
                                   'value': '${job_global_var}'},
                'job_task_id': {'hook': False, 'value': 10001}}}, 'type': 'ServiceActivity'}}, 'constants': {}}

        template_data = {'pipeline_template_data': {
            'template': {
                '1': {'tree': {'activities': {
                    'node7ee2048214dbf045e0043fe1f62b': {
                        'component': {'code': 'not_a_job', 'data': {
                            'job_global_var': {'hook': False, 'value': []},
                            'job_task_id': {'hook': False, 'value': 82401}}},
                        'type': 'ServiceActivity'},
                    'node51f27cbf5d61d50b36d1b25b58ed': {'component': {'code': 'not_a_job', 'data': {}},
                                                         'type': 'ServiceActivity'},
                    'node10dfa52df286c92c180398a78a5f': {'component': {'code': 'not_a_job', 'data': {
                        'job_global_var': {'hook': True,
                                           'value': '${job_global_var}'},
                        'job_task_id': {'hook': False, 'value': 10001}}}, 'type': 'ServiceActivity'}},
                    'constants': {}}}
            }
        }}

        job_id_map = {1000: {'id': 10001, 'var_id_map': {1: 11, 2: 21, 3: 31}},
                      8225: {'id': 82251,
                             'var_id_map': {7182: 71821,
                                            7183: 71831,
                                            7184: 71841,
                                            7185: 71851,
                                            7186: 71861,
                                            7190: 71901,
                                            7201: 72011}},
                      8240: {'id': 82401, 'var_id_map': {}}}

        api.replace_job_relate_id_in_templates_data(job_id_map, template_data)
        self.assertEqual(template_data['pipeline_template_data']['template']['1']['tree'], assert_data)

    def test_job_id_map_convert(self):
        # empty case
        job_id_maps = []
        result = api.job_id_map_convert(job_id_maps)

        self.assertEqual(result, {})

        # one map case

        job_id_maps = [
            {
                "original_job_id": 1,
                "new_job_id": 5,
                "original_job_name": "test",
                "new_job_name": "test_import20190120212225",
                "step_id_mapping": [
                ],
                "global_var_id_mapping": [
                    {
                        "original_id": 1,
                        "new_id": 5
                    },
                    {
                        "original_id": 10,
                        "new_id": 50
                    }
                ]
            }
        ]
        result = api.job_id_map_convert(job_id_maps)

        self.assertEqual(result, {1: {'id': 5,
                                      api.VAR_ID_MAP: {1: 5,
                                                       10: 50}}})

        # multiple map case
        job_id_maps = [
            {
                "original_job_id": 1,
                "new_job_id": 2,
                "original_job_name": "test",
                "new_job_name": "test_import20190120212225",
                "step_id_mapping": [],
                "global_var_id_mapping": [
                    {
                        "original_id": 1,
                        "new_id": 5
                    },
                    {
                        "original_id": 10,
                        "new_id": 50
                    }
                ]},
            {
                "original_job_id": 3,
                "new_job_id": 4,
                "original_job_name": "test",
                "new_job_name": "test_import20190120212225",
                "step_id_mapping": [],
                "global_var_id_mapping": [
                    {
                        "original_id": 2,
                        "new_id": 10
                    },
                    {
                        "original_id": 10,
                        "new_id": 50
                    }]},
            {
                "original_job_id": 5,
                "new_job_id": 6,
                "original_job_name": "test",
                "new_job_name": "test_import20190120212225",
                "step_id_mapping": [],
                "global_var_id_mapping": [
                    {
                        "original_id": 3,
                        "new_id": 20
                    },
                    {
                        "original_id": 10,
                        "new_id": 50
                    }]}
        ]
        result = api.job_id_map_convert(job_id_maps)

        self.assertEqual(result, {1: {'id': 2,
                                      api.VAR_ID_MAP: {1: 5,
                                                       10: 50}},
                                  3: {'id': 4,
                                      api.VAR_ID_MAP: {10: 50,
                                                       2: 10}},
                                  5: {'id': 6,
                                      api.VAR_ID_MAP: {10: 50,
                                                       3: 20}}})

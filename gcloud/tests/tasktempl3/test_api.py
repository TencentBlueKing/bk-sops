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

from __future__ import absolute_import

from django.test import TestCase

from gcloud.tasktmpl3 import api


class ApiTestCase(TestCase):

    def test_replace_job_relate_id_in_templates_data(self):
        # for template contain job_var constants

        assert_data = {u'activities': {
            u'node7ee2048214dbf045e0043fe1f62b': {
                u'component': {
                    u'code': u'job_execute_task',
                    u'data': {
                        u'job_global_var': {u'hook': False, u'value': []},
                        u'job_task_id': {u'hook': False,
                                         u'value': 82401}}},
                u'type': u'ServiceActivity'},
            u'node51f27cbf5d61d50b36d1b25b58ed': {
                u'component': {
                    u'code': u'job_execute_task', u'data': {
                        u'job_global_var': {
                            u'hook': False,
                            u'value': [{
                                u'value': u'0:1.1.1.1,0:2.2.2.2,0:3.3.3.3',
                                u'type': 2,
                                u'description': u'',
                                u'name': u'id-2018112023375235',
                                u'id': 71821},
                                {
                                    u'value': u'a"bc\'cb\'a',
                                    u'type': 1,
                                    u'description': u'',
                                    u'name': u'str1',
                                    u'id': 71831},
                                {
                                    u'value': u'ctx1',
                                    u'type': 1,
                                    u'description': u'ctx1',
                                    u'name': u'ctx1',
                                    u'id': 71841},
                                {
                                    u'value': u'(a b c)',
                                    u'type': 3,
                                    u'description': u'',
                                    u'name': u'aa',
                                    u'id': 71851},
                                {
                                    u'value': u'([A]=a [B]=b [C]=c)',
                                    u'type': 4,
                                    u'description': u'',
                                    u'name': u'bb',
                                    u'id': 71861},
                                {
                                    u'value': u'const_str',
                                    u'type': 1,
                                    u'description': u'const_str',
                                    u'name': u'const_str',
                                    u'id': 71901},
                                {
                                    u'value': u"<script>alert1('xss')</script>",
                                    u'type': 1,
                                    u'description': u'',
                                    u'name': u'str2',
                                    u'id': 72011}]},
                        u'job_task_id': {
                            u'hook': False,
                            u'value': 82251}}},
                u'type': u'ServiceActivity', },
            u'node10dfa52df286c92c180398a78a5f': {
                u'component': {
                    u'code': u'job_execute_task', u'data': {
                        u'job_global_var': {u'hook': True,
                                            u'value': u'${job_global_var}'},
                        u'job_task_id': {u'hook': False, u'value': 10001}}},
                u'type': u'ServiceActivity'}},
            u'constants': {
                u'${job_global_var}': {u'value': [
                    {u'value': u'5', u'type': 1,
                     u'name': u'SECONDS', u'id': 11},
                    {u'value': u'0', u'type': 1,
                     u'name': u'EXIT', u'id': 21},
                    {u'value': u'0:1.1.1.1,0:1.1.1.12,0:1.1.1.17', u'type': 2,
                     u'description': u'wewew',
                     u'name': u'id-201868163412877', u'id': 31}]}}}

        template_data = {'pipeline_template_data': {
            'template': {
                '1': {'tree': {u'activities': {
                    u'node7ee2048214dbf045e0043fe1f62b': {
                        u'component': {u'code': u'job_execute_task', u'data': {
                            u'job_global_var': {u'hook': False, u'value': []},
                            u'job_task_id': {u'hook': False, u'value': 8240}}},
                        u'type': u'ServiceActivity'},
                    u'node51f27cbf5d61d50b36d1b25b58ed': {u'component': {u'code': u'job_execute_task', u'data': {
                        u'job_global_var': {u'hook': False, u'value': [{
                            u'value': u'0:1.1.1.1,0:2.2.2.2,0:3.3.3.3',
                            u'type': 2,
                            u'description': u'',
                            u'name': u'id-2018112023375235',
                            u'id': 7182},
                            {
                                u'value': u'a"bc\'cb\'a',
                                u'type': 1,
                                u'description': u'',
                                u'name': u'str1',
                                u'id': 7183},
                            {
                                u'value': u'ctx1',
                                u'type': 1,
                                u'description': u'ctx1',
                                u'name': u'ctx1',
                                u'id': 7184},
                            {
                                u'value': u'(a b c)',
                                u'type': 3,
                                u'description': u'',
                                u'name': u'aa',
                                u'id': 7185},
                            {
                                u'value': u'([A]=a [B]=b [C]=c)',
                                u'type': 4,
                                u'description': u'',
                                u'name': u'bb',
                                u'id': 7186},
                            {
                                u'value': u'const_str',
                                u'type': 1,
                                u'description': u'const_str',
                                u'name': u'const_str',
                                u'id': 7190},
                            {
                                u'value': u"<script>alert1('xss')</script>",
                                u'type': 1,
                                u'description': u'',
                                u'name': u'str2',
                                u'id': 7201}]},
                        u'job_task_id': {u'hook': False, u'value': 8225}}}, u'type': u'ServiceActivity', },
                    u'node10dfa52df286c92c180398a78a5f': {
                        u'component': {
                            u'code': u'job_execute_task', u'data': {
                                u'job_global_var': {u'hook': True,
                                                    u'value': u'${job_global_var}'},
                                u'job_task_id': {u'hook': False, u'value': 1000}}},
                        u'type': u'ServiceActivity'}}, u'constants': {
                    u'${job_global_var}': {
                        u'value': [
                            {u'value': u'5', u'type': 1,
                             u'name': u'SECONDS', u'id': 1},
                            {u'value': u'0', u'type': 1,
                             u'name': u'EXIT', u'id': 2},
                            {u'value': u'0:1.1.1.1,0:1.1.1.12,0:1.1.1.17', u'type': 2,
                             u'description': u'wewew',
                             u'name': u'id-201868163412877', u'id': 3}]}}}}
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

        assert_data = {u'activities': {
            u'node7ee2048214dbf045e0043fe1f62b': {
                u'component': {u'code': u'not_a_job', u'data': {
                    u'job_global_var': {u'hook': False, u'value': []},
                    u'job_task_id': {u'hook': False, u'value': 82401}}},
                u'type': u'ServiceActivity'},
            u'node51f27cbf5d61d50b36d1b25b58ed': {u'component': {u'code': u'not_a_job', u'data': {}},
                                                  u'type': u'ServiceActivity'},
            u'node10dfa52df286c92c180398a78a5f': {u'component': {u'code': u'not_a_job', u'data': {
                u'job_global_var': {u'hook': True,
                                    u'value': u'${job_global_var}'},
                u'job_task_id': {u'hook': False, u'value': 10001}}}, u'type': u'ServiceActivity'}}, u'constants': {}}

        template_data = {'pipeline_template_data': {
            'template': {
                '1': {'tree': {u'activities': {
                    u'node7ee2048214dbf045e0043fe1f62b': {
                        u'component': {u'code': u'not_a_job', u'data': {
                            u'job_global_var': {u'hook': False, u'value': []},
                            u'job_task_id': {u'hook': False, u'value': 82401}}},
                        u'type': u'ServiceActivity'},
                    u'node51f27cbf5d61d50b36d1b25b58ed': {u'component': {u'code': u'not_a_job', u'data': {}},
                                                          u'type': u'ServiceActivity'},
                    u'node10dfa52df286c92c180398a78a5f': {u'component': {u'code': u'not_a_job', u'data': {
                        u'job_global_var': {u'hook': True,
                                            u'value': u'${job_global_var}'},
                        u'job_task_id': {u'hook': False, u'value': 10001}}}, u'type': u'ServiceActivity'}},
                    u'constants': {}}}
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

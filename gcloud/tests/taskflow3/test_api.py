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

from __future__ import absolute_import

from copy import deepcopy

from django.test import TestCase, Client

from pipeline.utils.uniqid import node_uniqid

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from gcloud.taskflow3 import api


TEST_BIZ_CC_ID = '2'  # do not change this to non number
TEST_ID_LIST = [node_uniqid() for i in range(10)]
TEST_PIPELINE_TREE = {
    'id': TEST_ID_LIST[0],
    'name': 'name',
    'start_event': {
        'id': TEST_ID_LIST[1],
        'name': 'start',
        'type': 'EmptyStartEvent',
        'incoming': None,
        'outgoing': TEST_ID_LIST[5]
    },
    'end_event': {
        'id': TEST_ID_LIST[2],
        'name': 'end',
        'type': 'EmptyEndEvent',
        'incoming': TEST_ID_LIST[7],
        'outgoing': None
    },
    'activities': {
        TEST_ID_LIST[3]: {
            'id': TEST_ID_LIST[3],
            'type': 'ServiceActivity',
            'name': 'first_task',
            'incoming': TEST_ID_LIST[5],
            'outgoing': TEST_ID_LIST[6],
            'optional': True,
            'component': {
                'code': 'test',
                'data': {
                    'input_test': {
                        'hook': False,
                        'value': '${custom_key1}',
                    },
                    'radio_test': {
                        'hook': False,
                        'value': '1',
                    },
                },
            }
        },
        TEST_ID_LIST[4]: {
            'id': TEST_ID_LIST[4],
            'type': 'ServiceActivity',
            'name': 'first_task',
            'incoming': TEST_ID_LIST[6],
            'outgoing': TEST_ID_LIST[7],
            'optional': True,
            'component': {
                'code': 'test',
                'data': {
                    'input_test': {
                        'hook': True,
                        'value': '${custom_key2}'
                    },
                    'radio_test': {
                        'hook': False,
                        'value': '2'
                    },
                },
            }
        },
    },
    'flows': {  # 存放该 Pipeline 中所有的线
        TEST_ID_LIST[5]: {
            'id': TEST_ID_LIST[5],
            'source': TEST_ID_LIST[1],
            'target': TEST_ID_LIST[3]
        },
        TEST_ID_LIST[6]: {
            'id': TEST_ID_LIST[6],
            'source': TEST_ID_LIST[3],
            'target': TEST_ID_LIST[4]
        },
        TEST_ID_LIST[7]: {
            'id': TEST_ID_LIST[7],
            'source': TEST_ID_LIST[4],
            'target': TEST_ID_LIST[2]
        },
    },
    'gateways': {  # 这里存放着网关的详细信息
    },
    'constants': {
        '${custom_key1}': {
            'index': 0,
            'name': 'input1',
            'key': '${custom_key1}',
            'desc': '',
            'validation': '^.*$',
            'show_type': 'show',
            'value': 'value1',
            'source_type': 'custom',
            'source_tag': '',
            'source_info': {},
            'custom_type': 'input',
        },
        '${custom_key2}': {
            'index': 1,
            'name': 'input2',
            'key': '${custom_key2}',
            'desc': '',
            'validation': '^.*$',
            'show_type': 'show',
            'value': 'value1',
            'source_type': 'custom',
            'source_tag': '',
            'source_info': {},
            'custom_type': 'input',
        },
    },
    'outputs': ['${custom_key1}'],
}


class APITest(TestCase):

    def setUp(self):
        self.PREVIEW_TASK_TREE_URL = '/taskflow/api/preview_task_tree/{biz_cc_id}/'
        self.client = Client()

    @mock.patch('gcloud.taskflow3.api.JsonResponse', MockJsonResponse())
    def test_preview_task_tree__constants_not_referred(self):

        with mock.patch(TASKTEMPLATE_GET,
                        MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))):
            data1 = {
                'template_source': 'business',
                'template_id': 1,
                'version': 'test_version',
                'exclude_task_nodes_id': '["%s"]' % TEST_ID_LIST[3]
            }
            result = api.preview_task_tree(MockRequest('POST', data1), TEST_BIZ_CC_ID)
            self.assertTrue(result['result'])
            self.assertEquals(result['data']['constants_not_referred'].keys(), ['${custom_key1}'])

        with mock.patch(TASKTEMPLATE_GET,
                        MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))):
            data2 = {
                'template_source': 'business',
                'template_id': 1,
                'version': 'test_version',
                'exclude_task_nodes_id': '["%s"]' % TEST_ID_LIST[4]
            }
            result = api.preview_task_tree(MockRequest('POST', data2), TEST_BIZ_CC_ID)
            self.assertTrue(result['result'])
            self.assertEquals(result['data']['constants_not_referred'].keys(), ['${custom_key2}'])

        with mock.patch(TASKTEMPLATE_GET,
                        MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))):
            data3 = {
                'template_source': 'business',
                'template_id': 1,
                'version': 'test_version',
                'exclude_task_nodes_id': '[]'
            }
            result = api.preview_task_tree(MockRequest('POST', data3), TEST_BIZ_CC_ID)
            self.assertTrue(result['result'])
            self.assertEquals(result['data']['constants_not_referred'].keys(), [])

        with mock.patch(TASKTEMPLATE_GET,
                        MagicMock(return_value=MockBaseTemplate(id=1, pipeline_tree=deepcopy(TEST_PIPELINE_TREE)))):
            data4 = {
                'template_source': 'business',
                'template_id': 1,
                'version': 'test_version',
                'exclude_task_nodes_id': '["%s", "%s"]' % (TEST_ID_LIST[3], TEST_ID_LIST[4])
            }
            result = api.preview_task_tree(MockRequest('POST', data4), TEST_BIZ_CC_ID)
            self.assertTrue(result['result'])
            self.assertEquals(result['data']['constants_not_referred'].keys(), ['${custom_key1}', '${custom_key2}'])

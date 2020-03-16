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


import ujson as json


from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = '123'
TEST_PROJECT_NAME = 'biz name'
TEST_BIZ_CC_ID = '123'
TEST_NODE_ID = 'node_id'
TEST_CALLBACK_DATA = 'callback_data'
TEST_TASKFLOW_ID = '2'


class NodeCallbackAPITest(APITest):
    def url(self):
        return '/apigw/node_callback/{task_id}/{project_id}/'

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID,
                                                                name=TEST_PROJECT_NAME,
                                                                bk_biz_id=TEST_BIZ_CC_ID,
                                                                from_cmdb=True)))
    def test_node_callback__success(self):
        mock_instance = MockTaskFlowInstance()
        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=mock_instance)):
            response = self.client.post(path=self.url().format(task_id=TEST_TASKFLOW_ID,
                                                               project_id=TEST_PROJECT_ID),
                                        data=json.dumps({
                                            'node_id': TEST_NODE_ID,
                                            'callback_data': TEST_CALLBACK_DATA
                                        }),
                                        content_type='application/json')

            data = json.loads(response.content)

            self.assertTrue(data['result'], msg=data)
            mock_instance.callback.assert_called_once_with(TEST_NODE_ID, TEST_CALLBACK_DATA)

    @mock.patch(TASKINSTANCE_GET, MagicMock(side_effect=TaskFlowInstance.DoesNotExist()))
    def test_node_callback__taskflow_does_not_exists(self):
        response = self.client.post(path=self.url().format(task_id=TEST_TASKFLOW_ID,
                                                           project_id=TEST_PROJECT_ID),
                                    data=json.dumps({
                                        'node_id': TEST_NODE_ID,
                                        'callback_data': TEST_CALLBACK_DATA
                                    }),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

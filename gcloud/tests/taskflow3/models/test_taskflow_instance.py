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

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class TaskflowTestCase(TestCase):

    def test_callback(self):
        instance = TaskFlowInstance()

        objects_callback_return = {'result': True, 'message': 'success'}

        with mock.patch(TASKINSTANCE_OBJECTS_CALLBACK, MagicMock(return_value=objects_callback_return)):
            with mock.patch(TASKINSTANCE_HAS_NODE, MagicMock(return_value=False)):
                result = instance.callback('act_id', 'data')
                self.assertFalse(result['result'])
                self.assertTrue('message' in result)
                TaskFlowInstance.objects.callback.assert_not_called()

            with mock.patch(TASKINSTANCE_HAS_NODE, MagicMock(return_value=True)):
                result = instance.callback('act_id', 'data')
                self.assertTrue(result['result'])
                self.assertTrue('message' in result)
                TaskFlowInstance.objects.callback.assert_called_once_with('act_id', 'data')

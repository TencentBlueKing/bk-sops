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

from django.test import TestCase, Client, override_settings

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

PROJECT_ID = 1
TASK_ID = 1


@override_settings(MIDDLEWARE=('django.contrib.sessions.middleware.SessionMiddleware',
                               'django.middleware.common.CommonMiddleware',))
class APITestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.SET_ENABLED_URL = '/periodictask/api/enabled/{project_id}/{task_id}/'
        cls.MODIFY_CRON_URL = '/periodictask/api/cron/{project_id}/{task_id}/'
        cls.MODIFY_CONSTANTS_URL = '/periodictask/api/constants/{project_id}/{task_id}/'

        super(APITestCase, cls).setUpClass()

    def setUp(self):
        self.client = Client()

    def test_set_enabled_for_periodic_task(self):
        periodic_task = MockPeriodicTask()
        with patch(PERIODIC_TASK_GET, MagicMock(return_value=periodic_task)):
            response = self.client.post(path=self.SET_ENABLED_URL.format(project_id=PROJECT_ID, task_id=TASK_ID),
                                        data={'enabled': True})

            periodic_task.set_enabled.assert_called_once_with(True)

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertTrue('message' in data)

    def test_modify_cron(self):
        periodic_task = MockPeriodicTask()
        project = MockProject()

        with patch(PERIODIC_TASK_GET, MagicMock(return_value=periodic_task)):
            with patch(PROJECT_GET, MagicMock(return_value=project)):
                response = self.client.post(path=self.MODIFY_CRON_URL.format(project_id=PROJECT_ID, task_id=TASK_ID),
                                            data={'cron': '{}'})

                periodic_task.modify_cron.assert_called_once_with({}, project.time_zone)

                data = json.loads(response.content)

                self.assertTrue(data['result'])
                self.assertTrue('message' in data)

    def test_modify_cron__modify_raise_exc(self):
        periodic_task = MockPeriodicTask(modify_cron_raise=Exception)
        project = MockProject()

        with patch(PERIODIC_TASK_GET, MagicMock(return_value=periodic_task)):
            with patch(PROJECT_GET, MagicMock(return_value=project)):
                response = self.client.post(path=self.MODIFY_CRON_URL.format(project_id=PROJECT_ID, task_id=TASK_ID),
                                            data={'cron': '{}'})

                periodic_task.modify_cron.assert_called_once_with({}, project.time_zone)

                data = json.loads(response.content)

                self.assertFalse(data['result'])
                self.assertTrue('message' in data)

    def test_modify_constants(self):
        modify_constants_return = {'token_key': 'token_value'}
        periodic_task = MockPeriodicTask(modify_constants_return=modify_constants_return)

        with patch(PERIODIC_TASK_GET, MagicMock(return_value=periodic_task)):
            response = self.client.post(path=self.MODIFY_CONSTANTS_URL.format(project_id=PROJECT_ID, task_id=TASK_ID),
                                        data={'constants': '{}'})

            periodic_task.modify_constants.assert_called_once_with({})

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertTrue('message' in data)
            self.assertEqual(data['data'], modify_constants_return)

    def test_modify_constants__modify_raise_exc(self):
        periodic_task = MockPeriodicTask(modify_constants_raise=Exception)

        with patch(PERIODIC_TASK_GET, MagicMock(return_value=periodic_task)):
            response = self.client.post(path=self.MODIFY_CONSTANTS_URL.format(project_id=PROJECT_ID, task_id=TASK_ID),
                                        data={'constants': '{}'})

            periodic_task.modify_constants.assert_called_once_with({})

            data = json.loads(response.content)

            self.assertFalse(data['result'])
            self.assertTrue('message' in data)

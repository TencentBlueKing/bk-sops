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

from mock import patch, MagicMock

from django.test import TestCase

from gcloud.constants import CallbackStatus
from gcloud.taskflow3.celery.tasks import task_callback


class TaskCallbackTestCase(TestCase):
    def test_callback_fail_reach_retry_times(self):
        settings = MagicMock()
        settings.REQUEST_RETRY_NUMBER = 0
        tcb = MagicMock()
        tcb.record = MagicMock()
        tcb.callback = MagicMock(return_value=False)
        with patch("gcloud.taskflow3.celery.tasks.settings", settings):
            with patch("gcloud.taskflow3.celery.tasks.TaskCallBacker", MagicMock(return_value=tcb)):
                task_callback(task_id=1)
        self.assertEqual(tcb.record.status, CallbackStatus.FAIL.value)

    def test_callback_fail_not_reach_retry_times(self):
        settings = MagicMock()
        settings.REQUEST_RETRY_NUMBER = 1
        tcb = MagicMock()
        tcb.record = MagicMock()
        tcb.callback = MagicMock(return_value=False)
        with patch("gcloud.taskflow3.celery.tasks.settings", settings):
            with patch("gcloud.taskflow3.celery.tasks.TaskCallBacker", MagicMock(return_value=tcb)):
                task_callback(task_id=1)
        tcb.record.save.assert_not_called()

    def test_callback_success(self):
        settings = MagicMock()
        settings.REQUEST_RETRY_NUMBER = 1
        tcb = MagicMock()
        tcb.record = MagicMock()
        tcb.callback = MagicMock(return_value=True)
        with patch("gcloud.taskflow3.celery.tasks.settings", settings):
            with patch("gcloud.taskflow3.celery.tasks.TaskCallBacker", MagicMock(return_value=tcb)):
                task_callback(task_id=1)
        self.assertEqual(tcb.record.status, CallbackStatus.SUCCESS.value)

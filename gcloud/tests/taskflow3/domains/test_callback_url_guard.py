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

import json
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from gcloud.constants import CallbackStatus
from gcloud.taskflow3.domains.callback import TaskCallBacker


@contextmanager
def acquired_lock(*args, **kwargs):
    yield True, None


class TaskCallBackerUrlGuardTestCase(SimpleTestCase):
    def build_callbacker(self):
        record = MagicMock(
            url="https://attacker.example.net/callback", extra_info=json.dumps({"callback_version": "v2"})
        )
        with patch("gcloud.taskflow3.domains.callback.TaskCallBackRecord.objects.filter") as record_filter:
            record_filter.return_value.first.return_value = record
            return TaskCallBacker(1), record

    @patch("gcloud.taskflow3.domains.callback.requests.post")
    @patch("gcloud.taskflow3.domains.callback.settings", MagicMock())
    @patch("gcloud.taskflow3.domains.callback.redis_lock", acquired_lock)
    @patch("gcloud.taskflow3.domains.callback.OutboundCallbackValidator.validate", return_value=(False, []))
    def test_rejected_host_is_marked_failed_without_retry(self, _validate, post):
        callbacker, record = self.build_callbacker()

        result = callbacker._url_callback()

        self.assertIsNone(result)
        post.assert_not_called()
        self.assertEqual(record.status, CallbackStatus.FAIL.value)
        self.assertEqual(json.loads(record.extra_info)["callback_error"], "callback_url host is not allowed")
        record.save.assert_called_once()

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
import time
import gevent
from django.conf import settings
from fakeredis import FakeRedis
from mock import MagicMock, patch

from django.test import TestCase

from gcloud.tests.mock import MockTaskOperationTimesConfig
from gcloud.tests.mock_settings import TASK_OPERATION_TIMES_CONFIG_GET
from api.utils.thread import ThreadPool
from gcloud.utils.throttle import check_task_operation_throttle


class CheckTaskOperationThrottleTestCase(TestCase):
    def setUp(self):
        self.start_time_stamp = time.time()
        self.times_config = MockTaskOperationTimesConfig({"times": 10, "time_unit": "m"})
        setattr(settings, "redis_inst", FakeRedis())

    def tearDown(self):
        delattr(settings, "redis_inst")

    def test__task_operation_throttle_exceed_times(self):
        with patch(TASK_OPERATION_TIMES_CONFIG_GET, MagicMock(return_value=self.times_config)):
            for time_num in range(100):
                result = check_task_operation_throttle(project_id=1, operation="test_exceed_times")
                if time_num < 10:
                    self.assertTrue(result)
                else:
                    self.assertFalse(result)

    def test__task_operation_throttle_within_times(self):
        with patch(TASK_OPERATION_TIMES_CONFIG_GET, MagicMock(return_value=self.times_config)):
            for time_num in range(100):
                time_stamp = self.start_time_stamp + time_num * 7
                with patch("time.time", MagicMock(return_value=time_stamp)):
                    result = check_task_operation_throttle(project_id=1, operation="test_within_times")
                    self.assertTrue(result)

    def test__task_operation_throttle_concurrency(self):
        with patch(TASK_OPERATION_TIMES_CONFIG_GET, MagicMock(return_value=self.times_config)):
            pool = ThreadPool()
            result_list = []
            for time_num in range(20):
                result_list.append(
                    pool.apply_async(
                        check_task_operation_throttle, kwds={"project_id": 1, "operation": "test_concurrency"}
                    )
                )
            pool.close()
            pool.join()
            success_num = len([result for result in result_list if result.get() is True])
            self.assertEqual(success_num, self.times_config.times)

    def test__task_operation_throttle_gevent(self):
        with patch(TASK_OPERATION_TIMES_CONFIG_GET, MagicMock(return_value=self.times_config)):
            jobs = [gevent.spawn(check_task_operation_throttle, 1, "test_gevent") for _ in range(20)]
            gevent.joinall(jobs)
            success_num = len([job.value for job in jobs if job.value is True])
            self.assertEqual(success_num, self.times_config.times)

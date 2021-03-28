# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import socket

import mock
from celery import current_app
from django.test import TestCase
from redis.exceptions import ConnectionError

from pipeline.conf import settings
from pipeline.django_signal_valve import valve
from pipeline.engine.core import api, data
from pipeline.engine.exceptions import RabbitMQConnectionError
from pipeline.engine.models import FunctionSwitch


class EngineCoreApiTestCase(TestCase):
    @mock.patch("pipeline.engine.models.FunctionSwitch.objects.freeze_engine", mock.MagicMock())
    def test_freeze(self):
        api.freeze()
        FunctionSwitch.objects.freeze_engine.assert_called_once()

    @mock.patch(
        "pipeline.engine.models.FunctionSwitch.objects.unfreeze_engine", mock.MagicMock(),
    )
    @mock.patch("pipeline.django_signal_valve.valve.open_valve", mock.MagicMock())
    def test_unfreeze(self):
        class MockFrozenProcess(object):
            pass

        res = []
        for i in range(10):
            p = MockFrozenProcess()
            p.unfreeze = mock.MagicMock()
            res.append(p)

        def mock_process_filter(*args, **kwargs):
            return res

        with mock.patch("pipeline.engine.models.PipelineProcess.objects.filter", mock_process_filter):
            api.unfreeze()
            FunctionSwitch.objects.unfreeze_engine.assert_called_once()
            valve.open_valve.assert_called_once()
            for mock_process in res:
                mock_process.unfreeze.assert_called_once()

    @mock.patch("celery.current_app.control.ping", mock.MagicMock())
    @mock.patch("pipeline.engine.core.data.expire_cache", mock.MagicMock())
    def test_workers(self):

        # throw error
        def throw_conn_error(*args, **kwargs):
            raise ConnectionError()

        with mock.patch("pipeline.engine.core.data.cache_for", throw_conn_error):
            self.assertRaises(ConnectionError, api.workers)

        # cache situation
        def return_worker_list(*args, **kwargs):
            return ["worker-1", "worker-2"]

        with mock.patch("pipeline.engine.core.data.cache_for", return_worker_list):
            worker = api.workers()
            self.assertEqual(worker, return_worker_list())
            current_app.control.ping.assert_not_called()
            data.expire_cache.assert_not_called()

        # no cache
        def return_none(*args, **kwargs):
            return None

        with mock.patch("pipeline.engine.core.data.cache_for", return_none):
            # no workers

            def no_workers(*args, **kwargs):
                return []

            current_app.control.ping.reset_mock()
            data.expire_cache.reset_mock()

            with mock.patch("celery.current_app.control.ping", no_workers):
                worker = api.workers()
                self.assertEqual(worker, no_workers())
                data.expire_cache.assert_not_called()

            # has workers

            def two_workers(*args, **kwargs):
                return ["w1", "w2"]

            current_app.control.ping.reset_mock()
            data.expire_cache.reset_mock()

            with mock.patch("celery.current_app.control.ping", two_workers):
                worker = api.workers()
                self.assertEqual(worker, two_workers())
                data.expire_cache.assert_called_with(
                    "__pipeline__workers__", two_workers(), settings.PIPELINE_WORKER_STATUS_CACHE_EXPIRES,
                )

            # raise exception

            def raise_mq_conn_error(*args, **kwargs):
                raise socket.error()

            current_app.control.ping.reset_mock()
            data.expire_cache.reset_mock()

            with mock.patch("celery.current_app.control.ping", raise_mq_conn_error):
                self.assertRaises(RabbitMQConnectionError, api.workers)
                data.expire_cache.assert_not_called()

            # retry test
            ping_mock = mock.MagicMock(side_effect=[[], two_workers()])

            with mock.patch("celery.current_app.control.ping", ping_mock):
                worker = api.workers()
                self.assertEqual(worker, two_workers())
                ping_mock.assert_has_calls([mock.call(timeout=1), mock.call(timeout=2)])
                data.expire_cache.assert_called_with(
                    "__pipeline__workers__", two_workers(), settings.PIPELINE_WORKER_STATUS_CACHE_EXPIRES,
                )

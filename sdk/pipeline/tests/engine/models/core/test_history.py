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

import datetime

import mock
from django.test import TestCase
from django.utils import timezone

from pipeline.engine.models import History, HistoryData
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.tests.mock_settings import *  # noqa

from ..mock import *  # noqa


class HistoryTestCase(TestCase):
    def test_record(self):
        def data_get(*args, **kwargs):
            data = Object()
            data.inputs = {"input": "value"}
            data.outputs = {"outputs": "value"}
            data.ex_data = "ex_data"
            return data

        status = MockStatus(skip=True)
        status.name = "name"
        status.started_time = timezone.now()
        status.archived_time = timezone.now()
        with mock.patch(PIPELINE_DATA_GET, data_get):
            history = History.objects.record(status)
            self.assertEqual(history.identifier, status.id)
            self.assertEqual(history.started_time, status.started_time)
            self.assertEqual(history.archived_time, status.archived_time)
            self.assertEqual(history.loop, status.loop)
            self.assertTrue(history.skip, status.skip)
            self.assertIsInstance(history.data, HistoryData)
            history_data = HistoryData.objects.get(id=history.data.id)
            self.assertEqual(history_data.inputs, data_get().inputs)
            self.assertEqual(history_data.outputs, data_get().outputs)
            self.assertEqual(history_data.ex_data, data_get().ex_data)

    def test_get_histories(self):
        def data_get(*args, **kwargs):
            data = Object()
            data.inputs = {"input": "value"}
            data.outputs = {"outputs": "value"}
            data.ex_data = "ex_data"
            return data

        started = timezone.now()
        archived = timezone.now()
        status = MockStatus(skip=False)
        status.name = "name"

        # no need microseconds
        status.started_time = datetime.datetime(
            year=started.year,
            month=started.month,
            day=started.day,
            hour=started.hour,
            minute=started.minute,
            second=started.second,
            tzinfo=started.tzinfo,
        )
        status.archived_time = datetime.datetime(
            year=archived.year,
            month=archived.month,
            day=archived.day,
            hour=archived.hour,
            minute=archived.minute,
            second=archived.second,
            tzinfo=archived.tzinfo,
        )
        with mock.patch(PIPELINE_DATA_GET, data_get):
            for i in range(3):
                History.objects.record(status)

            history_list = History.objects.get_histories(status.id)
            self.assertEqual(len(history_list), 3)
            for history in history_list:
                self.assertEqual(history["started_time"], status.started_time)
                self.assertEqual(history["archived_time"], status.archived_time)
                self.assertEqual(
                    history["elapsed_time"], calculate_elapsed_time(status.started_time, status.archived_time)
                )
                self.assertEqual(history["inputs"], data_get().inputs)
                self.assertEqual(history["outputs"], data_get().outputs)
                self.assertEqual(history["ex_data"], data_get().ex_data)
                self.assertEqual(history["loop"], status.loop)
                self.assertEqual(history["skip"], status.skip)
                self.assertTrue("history_id" in history)

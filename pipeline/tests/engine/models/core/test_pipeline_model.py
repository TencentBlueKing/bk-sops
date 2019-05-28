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

import mock

from django.test import TestCase

from django_signal_valve import valve
from pipeline.engine import signals
from pipeline.core.pipeline import Pipeline
from pipeline.engine.models import PipelineModel, PipelineProcess
from ..mock import *  # noqa

valve.unload_valve_function()


class TestPipelineModel(TestCase):

    def test_prepare_for_pipeline(self):
        pipeline = PipelineObject()
        process = PipelineProcess.objects.prepare_for_pipeline(pipeline)
        pipeline_model = PipelineModel.objects.prepare_for_pipeline(pipeline=pipeline, process=process)
        self.assertEqual(pipeline_model.process.id, process.id)
        self.assertEqual(pipeline_model.id, pipeline.id)

    @mock.patch('django_signal_valve.valve.send', mock.MagicMock())
    def test_pipeline_ready(self):
        process_id = uniqid()
        PipelineModel.objects.pipeline_ready(process_id=process_id)
        valve.send.assert_called_with(
            signals,
            'pipeline_ready',
            sender=Pipeline,
            process_id=process_id
        )

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

from django.test import TestCase

from pipeline.core.data.base import DataObject
from pipeline.core.flow.activity import *  # noqa


class TestActivity(TestCase):
    def test_base_activity(self):
        act_id = "1"
        base_act = Activity(act_id)
        self.assertTrue(isinstance(base_act, FlowNode))
        self.assertEqual(act_id, base_act.id)

    def test_service_activity(self):
        class TestService(Service):
            def execute(self, data, parent_data):
                return True

        act_id = "1"
        service = TestService()
        inputs = {"args": [1, 2, 3], "kwargs": {"1": 1, "2": 2}}
        service_act = ServiceActivity(id=act_id, service=service, data=DataObject(inputs))
        self.assertTrue(isinstance(service_act, Activity))
        self.assertEqual(service, service_act.service)

        service_act.setup_runtime_attrs(id="123", root_pipeline_id="456")
        self.assertEqual(service_act.service._runtime_attrs, {"id": "123", "root_pipeline_id": "456"})
        self.assertEqual(service_act.service.id, "123")
        self.assertEqual(service_act.service.root_pipeline_id, "456")

    def test_subprocess(self):
        act_id = "1"

        class MockData(object):
            def __init__(self, val):
                self.val = val

            def inputs_copy(self):
                pass

            def outputs_copy(self):
                pass

        class MockPipeline(object):
            def __init__(self, data):
                self.data = MockData(data)

        pipeline = MockPipeline("data")
        sub_process = SubProcess(act_id, pipeline)
        self.assertTrue(isinstance(sub_process, Activity))
        self.assertEqual(sub_process.data, pipeline.data)

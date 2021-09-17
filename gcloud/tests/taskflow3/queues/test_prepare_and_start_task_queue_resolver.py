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

from gcloud.tests.mock_settings import *  # noqa
from gcloud.taskflow3.domains.queues import PrepareAndStartTaskQueueResolver


class PrepareAndStartTaskQueueResolverTestCase(TestCase):
    def setUp(self):
        self.api_r = PrepareAndStartTaskQueueResolver("api")
        self.r = PrepareAndStartTaskQueueResolver("")

    def test_resolve_task_queue_and_routing_key(self):
        queue, routing_key = self.api_r.resolve_task_queue_and_routing_key()
        self.assertEqual(queue, "task_prepare_api")
        self.assertEqual(routing_key, "task_prepare_api")

        queue, routing_key = self.r.resolve_task_queue_and_routing_key()
        self.assertEqual(queue, "task_prepare")
        self.assertEqual(routing_key, "task_prepare")

    def test_routes_config(self):
        routes_config = self.api_r.routes_config()
        self.assertEqual(
            routes_config, {self.api_r.TASK_NAME: {"queue": "task_prepare_api", "routing_key": "task_prepare_api"}},
        )

        routes_config = self.r.routes_config()
        self.assertEqual(
            routes_config, {self.r.TASK_NAME: {"queue": "task_prepare", "routing_key": "task_prepare"}},
        )

    def test_queues(self):
        queues = self.api_r.queues()
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0].name, "task_prepare_api")
        self.assertEqual(queues[0].routing_key, "task_prepare_api")

        queues = self.r.queues()
        self.assertEqual(len(queues), 1)
        self.assertEqual(queues[0].name, "task_prepare")
        self.assertEqual(queues[0].routing_key, "task_prepare")

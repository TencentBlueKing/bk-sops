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

from django.test import TestCase

from gcloud.taskflow3.domains.auto_retry import AutoRetryNodeStrategyCreator
from gcloud.taskflow3.models import AutoRetryNodeStrategy


class AutoRetryNodeStrategyCreatorTestCase(TestCase):
    def test_batch_create_strategy(self):
        pipeline_tree = {
            "activities": {
                "a1": {"type": "ServiceActivity", "auto_retry": {"enable": True, "times": 2}},
                "a2": {"type": "ServiceActivity", "auto_retry": {"enable": True, "times": 12, "interval": 4}},
                "a3": {"type": "ServiceActivity"},
                "s1": {
                    "type": "SubProcess",
                    "pipeline": {
                        "activities": {
                            "a4": {"type": "ServiceActivity", "auto_retry": {"enable": True, "times": -1}},
                            "a5": {
                                "type": "ServiceActivity",
                                "auto_retry": {"enable": True, "times": 20, "interval": 30},
                            },
                            "a6": {"type": "ServiceActivity"},
                        }
                    },
                },
            }
        }
        taskflow_id = 1
        root_pipeline_id = "root"

        creator = AutoRetryNodeStrategyCreator(taskflow_id=taskflow_id, root_pipeline_id=root_pipeline_id)

        creator.batch_create_strategy(pipeline_tree)

        strategies = AutoRetryNodeStrategy.objects.all()
        self.assertEqual(len(strategies), 4)
        strategies_map = {
            s.node_id: {
                "taskflow_id": s.taskflow_id,
                "root_pipeline_id": s.root_pipeline_id,
                "node_id": s.node_id,
                "retry_times": s.retry_times,
                "max_retry_times": s.max_retry_times,
                "interval": s.interval,
            }
            for s in strategies
        }

        self.assertEqual(
            strategies_map["a1"],
            {
                "taskflow_id": 1,
                "root_pipeline_id": "root",
                "node_id": "a1",
                "retry_times": 0,
                "max_retry_times": 2,
                "interval": 0,
            },
        )
        self.assertEqual(
            strategies_map["a2"],
            {
                "taskflow_id": 1,
                "root_pipeline_id": "root",
                "node_id": "a2",
                "retry_times": 0,
                "max_retry_times": 10,
                "interval": 4,
            },
        )
        self.assertEqual(
            strategies_map["a4"],
            {
                "taskflow_id": 1,
                "root_pipeline_id": "root",
                "node_id": "a4",
                "retry_times": 0,
                "max_retry_times": 1,
                "interval": 0,
            },
        )
        self.assertEqual(
            strategies_map["a5"],
            {
                "taskflow_id": 1,
                "root_pipeline_id": "root",
                "node_id": "a5",
                "retry_times": 0,
                "max_retry_times": 10,
                "interval": 10,
            },
        )

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

from gcloud import constants as gcloud_constants
from pipeline.core import constants as pipeline_constants
from gcloud.taskflow3.models import AutoRetryNodeStrategy


class AutoRetryNodeStrategyCreator:
    def __init__(self, taskflow_id: int, root_pipeline_id: str):
        """

        Args:
            taskflow_id (int): TaskflowInstance 实例 ID
            root_pipeline_id (str): Pipeline ID
        """
        self.taskflow_id = taskflow_id
        self.root_pipeline_id = root_pipeline_id

    def batch_create_strategy(self, pipeline_tree: dict):
        """批量创建自动重试策略

        Args:
            pipeline_tree (dict): 经过子流程展开后的 pipeline 描述结构
        """

        def _initiate_strategy(pipeline_tree: dict):
            strategies = []
            for act_id, act in pipeline_tree[pipeline_constants.PE.activities].items():
                if act["type"] == pipeline_constants.PE.SubProcess:
                    strategies.extend(_initiate_strategy(act[pipeline_constants.PE.pipeline]))
                else:
                    auto_retry = act.get("auto_retry", {})
                    enable = auto_retry.get("enable")
                    if not enable:
                        continue

                    try:
                        max_retry_times = min(
                            abs(int(auto_retry.get("times", gcloud_constants.TASKFLOW_NODE_AUTO_RETRY_MAX_TIMES))),
                            gcloud_constants.TASKFLOW_NODE_AUTO_RETRY_MAX_TIMES,
                        )
                    except Exception:
                        max_retry_times = gcloud_constants.TASKFLOW_NODE_AUTO_RETRY_MAX_TIMES

                    try:
                        interval = min(
                            abs(int(auto_retry.get("interval", 0))),
                            gcloud_constants.TASKFLOW_NODE_AUTO_RETRY_MAX_INTERVAL,
                        )
                    except Exception:
                        interval = gcloud_constants.TASKFLOW_NODE_AUTO_RETRY_MAX_INTERVAL

                    strategies.append(
                        AutoRetryNodeStrategy(
                            taskflow_id=self.taskflow_id,
                            root_pipeline_id=self.root_pipeline_id,
                            node_id=act_id,
                            max_retry_times=max_retry_times,
                            interval=interval,
                        )
                    )
            return strategies

        strategies = _initiate_strategy(pipeline_tree)
        AutoRetryNodeStrategy.objects.bulk_create(
            strategies, batch_size=gcloud_constants.TASKFLOW_NODE_AUTO_RETRY_BATCH_CREATE_COUNT
        )

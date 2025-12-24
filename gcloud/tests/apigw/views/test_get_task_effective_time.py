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

from datetime import timedelta
from unittest.mock import MagicMock, patch

import ujson as json
from django.utils import timezone

from gcloud import err_code
from gcloud.analysis_statistics.models import TaskflowStatistics
from gcloud.core.models import Project
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TASKFLOW_ID = "2"
TEST_INSTANCE_ID = 100
TEST_TEMPLATE_ID = "template_123"
TEST_TASK_TEMPLATE_ID = "task_template_123"

GET_TASK_EFFECTIVE_TIME_TASK_COMMAND_DISPATCHER = "gcloud.apigw.views.get_task_effective_time.TaskCommandDispatcher"
GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH = "gcloud.apigw.views.get_task_effective_time.get_project_with"


class GetTaskEffectiveTimeAPITest(APITest):
    def url(self):
        return "/apigw/get_task_effective_time/{task_id}/{bk_biz_id}/"

    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        self.start_time = self.now
        self.finish_time = self.now + timedelta(seconds=200)
        self.total_elapsed_time = 200

    def _create_mock_task_stat(self):
        """创建模拟的任务统计对象"""
        task_stat = MagicMock()
        task_stat.task_instance_id = int(TEST_TASKFLOW_ID)
        task_stat.instance_id = TEST_INSTANCE_ID
        task_stat.template_id = TEST_TEMPLATE_ID
        task_stat.task_template_id = TEST_TASK_TEMPLATE_ID
        task_stat.project_id = int(TEST_PROJECT_ID)
        task_stat.creator = "test_user"
        task_stat.create_method = "app"
        task_stat.create_time = self.start_time
        task_stat.start_time = self.start_time
        task_stat.finish_time = self.finish_time
        task_stat.elapsed_time = self.total_elapsed_time
        task_stat.category = "Default"
        return task_stat

    def _create_mock_node_stat(
        self,
        node_id,
        component_code,
        elapsed_time,
        started_time=None,
        archived_time=None,
        is_retry=False,
        is_skip=False,
        status=True,
    ):
        """创建模拟的节点统计对象"""
        node_stat = MagicMock()
        node_stat.node_id = node_id
        node_stat.component_code = component_code
        node_stat.elapsed_time = elapsed_time
        node_stat.started_time = started_time or self.start_time
        node_stat.archived_time = archived_time or self.finish_time
        node_stat.is_retry = is_retry
        node_stat.is_skip = is_skip
        node_stat.status = status
        node_stat.template_node_id = f"template_{node_id}"
        return node_stat

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__task_statistics_not_found(self):
        """测试任务统计信息不存在的情况"""
        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={},
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(side_effect=TaskflowStatistics.DoesNotExist()),
            ):
                response = self.client.get(path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        self.assertIn("task statistics not found", data["message"])

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__task_not_finished(self):
        """测试任务未完成的情况"""
        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=None,  # 任务未完成
                        execution_data={},
                    ),
                )
            ),
        ):
            response = self.client.get(path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("not finished yet", data["message"])

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__task_revoked(self):
        """测试任务被终止的情况"""
        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={},
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(return_value=self._create_mock_task_stat()),
            ):
                with patch(
                    TASKFLOWEXECUTEDNODE_STATISTICS_FILTER,
                    MagicMock(
                        return_value=MagicMock(
                            filter=MagicMock(return_value=MagicMock()),
                        )
                    ),
                ):
                    with patch(
                        "gcloud.apigw.views.get_task_effective_time._check_revoke_operation",
                        MagicMock(return_value=True),
                    ):
                        response = self.client.get(
                            path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID)
                        )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("was revoked", data["message"])

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__success_with_excluded_nodes(self):
        """测试成功场景：包含排除节点"""
        # 创建节点统计数据
        node_stats = [
            self._create_mock_node_stat(
                "node1", "bk_approve", 50, self.start_time, self.start_time + timedelta(seconds=50)
            ),
            self._create_mock_node_stat(
                "node2",
                "normal_node",
                100,
                self.start_time + timedelta(seconds=50),
                self.start_time + timedelta(seconds=150),
            ),
            self._create_mock_node_stat(
                "node3", "normal_node", 50, self.start_time + timedelta(seconds=150), self.finish_time
            ),
        ]

        node_stats_qs = MagicMock()
        node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        node_stats_qs.aggregate = MagicMock(return_value={"total_time": 50})  # 排除节点耗时
        node_stats_qs.count = MagicMock(return_value=1)  # 排除节点数量

        all_node_stats_qs = MagicMock()
        all_node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        all_node_stats_qs.__iter__ = MagicMock(return_value=iter(node_stats))
        all_node_stats_qs.count = MagicMock(return_value=3)

        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={},
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(return_value=self._create_mock_task_stat()),
            ):
                with patch(
                    "gcloud.apigw.views.get_task_effective_time._check_revoke_operation",
                    MagicMock(return_value=False),
                ):
                    with patch(
                        "gcloud.apigw.views.get_task_effective_time._get_excluded_component_codes",
                        MagicMock(return_value=["bk_approve", "pause_node"]),
                    ):
                        with patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=all_node_stats_qs)):
                            with patch(
                                "gcloud.apigw.views.get_task_effective_time._calculate_retry_node_time_adjustment",
                                MagicMock(return_value=0),
                            ):
                                with patch(
                                    "gcloud.apigw.views.get_task_effective_time._calculate_failure_wait_time",
                                    MagicMock(return_value=0),
                                ):
                                    with patch(
                                        GET_TASK_EFFECTIVE_TIME_TASK_COMMAND_DISPATCHER,
                                        MagicMock(
                                            return_value=MagicMock(
                                                get_task_status=MagicMock(return_value={"result": True, "data": {}}),
                                            )
                                        ),
                                    ):
                                        response = self.client.get(
                                            path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID)
                                        )

                                        data = json.loads(response.content)
                                        self.assertTrue(data["result"])
                                        self.assertEqual(data["code"], err_code.SUCCESS.code)
                                        self.assertEqual(data["data"]["total_elapsed_time"], 200)
                                        self.assertEqual(data["data"]["excluded_time"], 50)
                                        self.assertEqual(data["data"]["effective_time"], 150)  # 200 - 50
                                        self.assertEqual(data["data"]["excluded_node_count"], 1)

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__parallel_gateway_non_critical_path(self):
        """测试并行网关场景：非关键路径分支中的人工节点"""
        # 分支A（人工操作）：耗时100秒
        # 分支B（非人工操作）：耗时200秒
        # 总执行时间 = 200秒
        # 应该排除分支A中的人工节点耗时（100秒），因为不影响总时间

        node1_start = self.start_time
        node1_end = self.start_time + timedelta(seconds=100)
        node2_start = self.start_time
        node2_end = self.start_time + timedelta(seconds=200)

        node_stats = [
            self._create_mock_node_stat("node1", "bk_approve", 100, node1_start, node1_end),
            self._create_mock_node_stat("node2", "normal_node", 200, node2_start, node2_end),
        ]

        node_stats_qs = MagicMock()
        node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        node_stats_qs.aggregate = MagicMock(return_value={"total_time": 100})  # 排除节点耗时
        node_stats_qs.count = MagicMock(return_value=1)

        all_node_stats_qs = MagicMock()
        all_node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        all_node_stats_qs.__iter__ = MagicMock(return_value=iter(node_stats))
        all_node_stats_qs.count = MagicMock(return_value=2)

        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={
                            "gateways": {
                                "gateway1": {
                                    "id": "gateway1",
                                    "type": "ParallelGateway",
                                    "outgoing": ["flow1", "flow2"],
                                },
                                "gateway2": {
                                    "id": "gateway2",
                                    "type": "ConvergeGateway",
                                    "incoming": ["flow3", "flow4"],
                                },
                            },
                            "flows": {
                                "flow1": {"source": "gateway1", "target": "node1"},
                                "flow2": {"source": "gateway1", "target": "node2"},
                                "flow3": {"source": "node1", "target": "gateway2"},
                                "flow4": {"source": "node2", "target": "gateway2"},
                            },
                            "activities": {
                                "node1": {"id": "node1", "outgoing": "flow3"},
                                "node2": {"id": "node2", "outgoing": "flow4"},
                            },
                        },
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(return_value=self._create_mock_task_stat()),
            ):
                with patch(
                    "gcloud.apigw.views.get_task_effective_time._check_revoke_operation",
                    MagicMock(return_value=False),
                ):
                    with patch(
                        "gcloud.apigw.views.get_task_effective_time._get_excluded_component_codes",
                        MagicMock(return_value=["bk_approve"]),
                    ):
                        with patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=all_node_stats_qs)):
                            with patch(
                                "gcloud.apigw.views.get_task_effective_time._calculate_retry_node_time_adjustment",
                                MagicMock(return_value=0),
                            ):
                                with patch(
                                    "gcloud.apigw.views.get_task_effective_time._calculate_failure_wait_time",
                                    MagicMock(return_value=0),
                                ):
                                    with patch(
                                        GET_TASK_EFFECTIVE_TIME_TASK_COMMAND_DISPATCHER,
                                        MagicMock(
                                            return_value=MagicMock(
                                                get_task_status=MagicMock(
                                                    return_value={
                                                        "result": True,
                                                        "data": {
                                                            "children": {
                                                                "gateway1": {"id": "gateway1"},
                                                                "node1": {"id": "node1"},
                                                                "node2": {"id": "node2"},
                                                            },
                                                        },
                                                    }
                                                ),
                                            )
                                        ),
                                    ):
                                        response = self.client.get(
                                            path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID)
                                        )

                                        data = json.loads(response.content)
                                        self.assertTrue(data["result"])
                                        self.assertEqual(data["code"], err_code.SUCCESS.code)
                                        self.assertEqual(data["data"]["total_elapsed_time"], 200)
                                        self.assertEqual(data["data"]["excluded_time"], 100)
                                        # 并行网关调整：非关键路径分支中的人工节点耗时应该被排除
                                        # effective_time = 200 - 100 - 0 - 0 + 100 = 200
                                        self.assertGreaterEqual(data["data"]["parallel_gateway_adjustment"], 0)
                                        self.assertEqual(data["data"]["effective_time"], 200)

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__with_retry_nodes(self):
        """测试包含重试节点的场景"""
        node_stats = [
            self._create_mock_node_stat(
                "node1", "normal_node", 50, self.start_time, self.start_time + timedelta(seconds=50), is_retry=True
            ),
            self._create_mock_node_stat(
                "node1",
                "normal_node",
                30,
                self.start_time + timedelta(seconds=60),
                self.start_time + timedelta(seconds=90),
            ),  # 重试后的节点
        ]

        node_stats_qs = MagicMock()
        node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        node_stats_qs.aggregate = MagicMock(return_value={"total_time": 0})
        node_stats_qs.count = MagicMock(return_value=0)

        all_node_stats_qs = MagicMock()
        all_node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        all_node_stats_qs.__iter__ = MagicMock(return_value=iter(node_stats))
        all_node_stats_qs.count = MagicMock(return_value=2)

        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={},
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(return_value=self._create_mock_task_stat()),
            ):
                with patch(
                    "gcloud.apigw.views.get_task_effective_time._check_revoke_operation",
                    MagicMock(return_value=False),
                ):
                    with patch(
                        "gcloud.apigw.views.get_task_effective_time._get_excluded_component_codes",
                        MagicMock(return_value=["bk_approve"]),
                    ):
                        with patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=all_node_stats_qs)):
                            with patch(
                                "gcloud.apigw.views.get_task_effective_time._calculate_retry_node_time_adjustment",
                                MagicMock(return_value=10),  # 重试间隔10秒
                            ):
                                with patch(
                                    "gcloud.apigw.views.get_task_effective_time._calculate_failure_wait_time",
                                    MagicMock(return_value=0),
                                ):
                                    with patch(
                                        GET_TASK_EFFECTIVE_TIME_TASK_COMMAND_DISPATCHER,
                                        MagicMock(
                                            return_value=MagicMock(
                                                get_task_status=MagicMock(return_value={"result": True, "data": {}}),
                                            )
                                        ),
                                    ):
                                        response = self.client.get(
                                            path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID)
                                        )

                                        data = json.loads(response.content)
                                        self.assertTrue(data["result"])
                                        self.assertEqual(data["data"]["retry_node_time_adjustment"], 10)
                                        # effective_time = 200 - 0 - 0 - 10 = 190
                                        self.assertEqual(data["data"]["effective_time"], 190)

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__with_failure_wait_time(self):
        """测试包含失败后等待时间的场景"""
        node_stats = [
            self._create_mock_node_stat(
                "node1",
                "normal_node",
                50,
                self.start_time,
                self.start_time + timedelta(seconds=50),
                is_skip=True,
                status=False,
            ),
        ]

        node_stats_qs = MagicMock()
        node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        node_stats_qs.aggregate = MagicMock(return_value={"total_time": 0})
        node_stats_qs.count = MagicMock(return_value=0)
        node_stats_qs.order_by = MagicMock(return_value=node_stats_qs)
        node_stats_qs.exists = MagicMock(return_value=True)

        all_node_stats_qs = MagicMock()
        all_node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        all_node_stats_qs.__iter__ = MagicMock(return_value=iter(node_stats))
        all_node_stats_qs.count = MagicMock(return_value=1)

        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={},
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(return_value=self._create_mock_task_stat()),
            ):
                with patch(
                    "gcloud.apigw.views.get_task_effective_time._check_revoke_operation",
                    MagicMock(return_value=False),
                ):
                    with patch(
                        "gcloud.apigw.views.get_task_effective_time._get_excluded_component_codes",
                        MagicMock(return_value=["bk_approve"]),
                    ):
                        with patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=all_node_stats_qs)):
                            with patch(
                                "gcloud.apigw.views.get_task_effective_time._calculate_retry_node_time_adjustment",
                                MagicMock(return_value=0),
                            ):
                                with patch(
                                    "gcloud.apigw.views.get_task_effective_time._calculate_failure_wait_time",
                                    MagicMock(return_value=30),  # 失败后等待30秒
                                ):
                                    with patch(
                                        TASK_OPERATE_RECORD_FILTER,
                                        MagicMock(
                                            return_value=MagicMock(
                                                filter=MagicMock(
                                                    return_value=MagicMock(
                                                        order_by=MagicMock(
                                                            return_value=MagicMock(exists=MagicMock(return_value=True))
                                                        ),
                                                    )
                                                ),
                                            )
                                        ),
                                    ):
                                        with patch(
                                            GET_TASK_EFFECTIVE_TIME_TASK_COMMAND_DISPATCHER,
                                            MagicMock(
                                                return_value=MagicMock(
                                                    get_task_status=MagicMock(
                                                        return_value={"result": True, "data": {}}
                                                    ),
                                                )
                                            ),
                                        ):
                                            response = self.client.get(
                                                path=self.url().format(
                                                    task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID
                                                )
                                            )

                                            data = json.loads(response.content)
                                            self.assertTrue(data["result"])
                                            self.assertEqual(data["data"]["failure_wait_time"], 30)
                                            # effective_time = 200 - 0 - 30 - 0 = 170
                                            self.assertEqual(data["data"]["effective_time"], 170)

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    def test_get_task_effective_time__parallel_gateway_critical_path(self):
        """测试并行网关场景：关键路径分支中的人工节点"""
        # 分支A（人工操作）：耗时200秒（关键路径）
        # 分支B（非人工操作）：耗时100秒
        # 总执行时间 = 200秒
        # 分支A是关键路径，其中的人工节点耗时应该被排除

        node1_start = self.start_time
        node1_end = self.start_time + timedelta(seconds=200)
        node2_start = self.start_time
        node2_end = self.start_time + timedelta(seconds=100)

        node_stats = [
            self._create_mock_node_stat("node1", "bk_approve", 200, node1_start, node1_end),
            self._create_mock_node_stat("node2", "normal_node", 100, node2_start, node2_end),
        ]

        node_stats_qs = MagicMock()
        node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        node_stats_qs.aggregate = MagicMock(return_value={"total_time": 200})  # 排除节点耗时
        node_stats_qs.count = MagicMock(return_value=1)

        all_node_stats_qs = MagicMock()
        all_node_stats_qs.filter = MagicMock(return_value=node_stats_qs)
        all_node_stats_qs.__iter__ = MagicMock(return_value=iter(node_stats))
        all_node_stats_qs.count = MagicMock(return_value=2)

        with patch(
            TASKINSTANCE_GET,
            MagicMock(
                return_value=MagicMock(
                    id=int(TEST_TASKFLOW_ID),
                    project_id=int(TEST_PROJECT_ID),
                    is_deleted=False,
                    engine_ver=1,
                    pipeline_instance=MagicMock(
                        finish_time=self.finish_time,
                        execution_data={
                            "gateways": {
                                "gateway1": {
                                    "id": "gateway1",
                                    "type": "ParallelGateway",
                                    "outgoing": ["flow1", "flow2"],
                                },
                                "gateway2": {
                                    "id": "gateway2",
                                    "type": "ConvergeGateway",
                                    "incoming": ["flow3", "flow4"],
                                },
                            },
                            "flows": {
                                "flow1": {"source": "gateway1", "target": "node1"},
                                "flow2": {"source": "gateway1", "target": "node2"},
                                "flow3": {"source": "node1", "target": "gateway2"},
                                "flow4": {"source": "node2", "target": "gateway2"},
                            },
                            "activities": {
                                "node1": {"id": "node1", "outgoing": "flow3"},
                                "node2": {"id": "node2", "outgoing": "flow4"},
                            },
                        },
                    ),
                )
            ),
        ):
            with patch(
                TASKFLOW_STATISTICS_GET,
                MagicMock(return_value=self._create_mock_task_stat()),
            ):
                with patch(
                    "gcloud.apigw.views.get_task_effective_time._check_revoke_operation",
                    MagicMock(return_value=False),
                ):
                    with patch(
                        "gcloud.apigw.views.get_task_effective_time._get_excluded_component_codes",
                        MagicMock(return_value=["bk_approve"]),
                    ):
                        with patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=all_node_stats_qs)):
                            with patch(
                                "gcloud.apigw.views.get_task_effective_time._calculate_retry_node_time_adjustment",
                                MagicMock(return_value=0),
                            ):
                                with patch(
                                    "gcloud.apigw.views.get_task_effective_time._calculate_failure_wait_time",
                                    MagicMock(return_value=0),
                                ):
                                    with patch(
                                        GET_TASK_EFFECTIVE_TIME_TASK_COMMAND_DISPATCHER,
                                        MagicMock(
                                            return_value=MagicMock(
                                                get_task_status=MagicMock(
                                                    return_value={
                                                        "result": True,
                                                        "data": {
                                                            "children": {
                                                                "gateway1": {"id": "gateway1"},
                                                                "node1": {"id": "node1"},
                                                                "node2": {"id": "node2"},
                                                            },
                                                        },
                                                    }
                                                ),
                                            )
                                        ),
                                    ):
                                        response = self.client.get(
                                            path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID)
                                        )

                                        data = json.loads(response.content)
                                        self.assertTrue(data["result"])
                                        self.assertEqual(data["code"], err_code.SUCCESS.code)
                                        self.assertEqual(data["data"]["total_elapsed_time"], 200)
                                        self.assertEqual(data["data"]["excluded_time"], 200)
                                        # 关键路径分支中的人工节点耗时应该被排除，但不会因为并行网关而调整
                                        # effective_time = 200 - 200 - 0 - 0 + 0 = 0
                                        self.assertEqual(data["data"]["parallel_gateway_adjustment"], 0)
                                        self.assertEqual(data["data"]["effective_time"], 0)

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(side_effect=Project.DoesNotExist()),
    )
    def test_get_task_effective_time__project_not_found(self):
        """测试项目不存在的情况"""
        response = self.client.get(path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        self.assertIn("does not exist", data["message"])

    @patch(
        GET_TASK_EFFECTIVE_TIME_GET_PROJECT_WITH,
        MagicMock(return_value=MagicMock(id=int(TEST_PROJECT_ID))),
    )
    @patch(
        TASKINSTANCE_GET,
        MagicMock(side_effect=TaskFlowInstance.DoesNotExist()),
    )
    def test_get_task_effective_time__task_not_found(self):
        """测试任务不存在的情况"""
        response = self.client.get(path=self.url().format(task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        self.assertIn("does not exist", data["message"])

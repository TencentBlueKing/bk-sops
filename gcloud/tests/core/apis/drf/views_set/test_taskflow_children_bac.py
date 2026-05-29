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

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase

from gcloud.core.apis.drf.viewsets.taskflow import TaskFlowInstanceViewSet

INSTANCE_FILTER = "gcloud.core.apis.drf.viewsets.taskflow.TaskFlowInstance.objects.filter"
RELATION_FILTER = "gcloud.core.apis.drf.viewsets.taskflow.TaskFlowRelation.objects.filter"


def _build_view(action, query_params):
    view = TaskFlowInstanceViewSet()
    view.action = action
    view.request = SimpleNamespace(query_params=query_params, user=SimpleNamespace(username="tester"))
    view.kwargs = {}
    view.format_kwarg = None
    return view


class RootTaskInfoProjectScopeTestCase(TestCase):
    """BAC: root_task_info 必须仅统计属于已鉴权项目的任务，
    不属于该项目的 task_id 一律返回 False，避免跨项目探测任务子流程结构。"""

    def test_root_task_info__only_counts_tasks_in_authorized_project(self):
        view = _build_view("root_task_info", {"task_ids": "1,2,3", "project_id": "10"})

        instance_qs = MagicMock()
        # 仅 task 1、2 属于项目 10，task 3 属于其它项目
        instance_qs.values_list.return_value = [1, 2]
        relation_qs = MagicMock()
        # 仅 task 1 拥有子任务
        relation_qs.values_list.return_value = [1]

        with patch(INSTANCE_FILTER, MagicMock(return_value=instance_qs)):
            with patch(RELATION_FILTER, MagicMock(return_value=relation_qs)):
                response = view.root_task_info(view.request)

        self.assertEqual(response.data["has_children_taskflow"], {1: True, 2: False, 3: False})

    def test_root_task_info__empty_project_id_normalized_to_none(self):
        """空串 project_id 应归一化为 None(filter(project_id=None) 走 IS NULL 返回空集)，
        避免 filter(project_id="") 触发整型转换 ValueError 导致 500。"""
        view = _build_view("root_task_info", {"task_ids": "1,2", "project_id": ""})

        instance_qs = MagicMock()
        instance_qs.values_list.return_value = []
        relation_qs = MagicMock()
        relation_qs.values_list.return_value = []
        instance_filter = MagicMock(return_value=instance_qs)

        with patch(INSTANCE_FILTER, instance_filter):
            with patch(RELATION_FILTER, MagicMock(return_value=relation_qs)):
                response = view.root_task_info(view.request)

        _, filter_kwargs = instance_filter.call_args
        self.assertIsNone(filter_kwargs.get("project_id"))
        self.assertEqual(response.data["has_children_taskflow"], {1: False, 2: False})


class ListChildrenTaskflowProjectScopeTestCase(TestCase):
    """BAC: list_children_taskflow 的鉴权接受 project_id/project__id，但过滤器仅识别 project__id，
    导致仅传 project_id 时子任务未按项目收敛。修复后应显式按已鉴权项目过滤子任务及关系。"""

    def test_list_children__scopes_children_and_relations_by_project(self):
        view = _build_view("list_children_taskflow", {"root_task_id": "500", "project_id": "10"})

        relation_values = [
            {"task_id": 1, "parent_task_id": 500},
            {"task_id": 2, "parent_task_id": 500},
        ]
        relation_qs = MagicMock()
        relation_qs.values.return_value = relation_values

        instance_filter = MagicMock(return_value="CHILDREN_QS")

        with patch(RELATION_FILTER, MagicMock(return_value=relation_qs)):
            with patch(INSTANCE_FILTER, instance_filter):
                with patch.object(TaskFlowInstanceViewSet, "filter_queryset", side_effect=lambda qs: qs):
                    with patch.object(
                        TaskFlowInstanceViewSet,
                        "get_serializer",
                        return_value=SimpleNamespace(data=[{"id": 1}]),
                    ):
                        with patch.object(
                            TaskFlowInstanceViewSet,
                            "injection_auth_actions",
                            side_effect=lambda request, data, qs: data,
                        ):
                            with patch.object(TaskFlowInstanceViewSet, "_inject_template_related_info"):
                                response = view.list_children_taskflow(view.request)

        # 子任务查询必须按已鉴权项目收敛
        _, filter_kwargs = instance_filter.call_args
        self.assertEqual(filter_kwargs.get("project_id"), "10")
        # 只有真正返回（属于该项目）的 task 1 才会出现在 tasks / relations 中，task 2 被剔除
        self.assertEqual(response.data["tasks"], [{"id": 1}])
        self.assertEqual(response.data["relations"], {500: [1]})

    def test_list_children__empty_project_id_normalized_to_none(self):
        """空串 project_id 应归一化为 None，避免 filter(project_id="") 触发 500。"""
        view = _build_view("list_children_taskflow", {"root_task_id": "500", "project_id": ""})

        relation_qs = MagicMock()
        relation_qs.values.return_value = [{"task_id": 1, "parent_task_id": 500}]
        instance_filter = MagicMock(return_value="CHILDREN_QS")

        with patch(RELATION_FILTER, MagicMock(return_value=relation_qs)):
            with patch(INSTANCE_FILTER, instance_filter):
                with patch.object(TaskFlowInstanceViewSet, "filter_queryset", side_effect=lambda qs: qs):
                    with patch.object(TaskFlowInstanceViewSet, "get_serializer", return_value=SimpleNamespace(data=[])):
                        with patch.object(
                            TaskFlowInstanceViewSet,
                            "injection_auth_actions",
                            side_effect=lambda request, data, qs: data,
                        ):
                            with patch.object(TaskFlowInstanceViewSet, "_inject_template_related_info"):
                                response = view.list_children_taskflow(view.request)

        _, filter_kwargs = instance_filter.call_args
        self.assertIsNone(filter_kwargs.get("project_id"))
        self.assertEqual(response.data["tasks"], [])
        self.assertEqual(response.data["relations"], {})

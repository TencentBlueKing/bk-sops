# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import SimpleTestCase
from mock import patch

from gcloud.taskflow3.models import TaskFlowInstance


class MockQuery(object):
    def __init__(self, sql, params):
        self.sql = sql
        self.params = params

    def sql_with_params(self):
        return self.sql, self.params


class MockSlicedQuerySet(object):
    def __init__(self, sql, params, rows=None):
        self.query = MockQuery(sql, params)
        self.rows = rows or []

    def __iter__(self):
        return iter(self.rows)


class MockQuerySet(object):
    def __init__(self, sql, params, rows=None):
        self.sliced_queryset = MockSlicedQuerySet(sql, params, rows)
        self.used_slice = None

    def __getitem__(self, used_slice):
        self.used_slice = used_slice
        return self.sliced_queryset


class TaskFlowInstanceManagerTestCase(SimpleTestCase):
    def test_fetch_task_list_page_ignore_primary_index_injects_mysql_index_hint(self):
        sql = (
            "SELECT `taskflow3_taskflowinstance`.`id` "
            "FROM `taskflow3_taskflowinstance` "
            "INNER JOIN `pipeline_pipelineinstance` "
            "ON (`taskflow3_taskflowinstance`.`pipeline_instance_id` = `pipeline_pipelineinstance`.`id`) "
            "ORDER BY `taskflow3_taskflowinstance`.`id` DESC LIMIT 15"
        )
        params = ["%tlogd%"]
        queryset = MockQuerySet(sql, params)

        with patch("gcloud.taskflow3.models.connection.vendor", "mysql"):
            with patch.object(TaskFlowInstance.objects, "raw", return_value=["row"]) as mock_raw:
                result = TaskFlowInstance.objects.fetch_task_list_page_ignore_primary_index(
                    queryset=queryset, limit=15, offset=5
                )

        expected_sql = sql.replace(
            "FROM `taskflow3_taskflowinstance`",
            "FROM `taskflow3_taskflowinstance` IGNORE INDEX (`PRIMARY`)",
            1,
        )
        self.assertEqual(result, ["row"])
        self.assertEqual(queryset.used_slice, slice(5, 20, None))
        mock_raw.assert_called_once_with(expected_sql, params)

    def test_fetch_task_list_page_ignore_primary_index_falls_back_for_non_mysql(self):
        sql = "SELECT `taskflow3_taskflowinstance`.`id` FROM `taskflow3_taskflowinstance`"
        queryset = MockQuerySet(sql, [], rows=["row"])

        with patch("gcloud.taskflow3.models.connection.vendor", "sqlite"):
            with patch.object(TaskFlowInstance.objects, "raw") as mock_raw:
                result = TaskFlowInstance.objects.fetch_task_list_page_ignore_primary_index(
                    queryset=queryset, limit=15, offset=0
                )

        self.assertEqual(result, ["row"])
        self.assertEqual(queryset.used_slice, slice(0, 15, None))
        mock_raw.assert_not_called()

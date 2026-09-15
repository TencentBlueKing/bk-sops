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
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from gcloud import err_code
from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TEMPLATE_ID = "1"
TEST_TEMPLATE_NODE_ID = "node123"


class _NodeExecutionRecordQuerySet(object):
    def __init__(self, rows):
        self.rows = rows
        self.count_called = False
        self.sliced_limits = []

    def order_by(self, *args):
        return self

    def values(self, *args):
        return self

    def count(self):
        self.count_called = True
        return len(self.rows)

    def __getitem__(self, item):
        self.sliced_limits.append((item.start, item.stop))
        return self.rows[item]


class GetNodeExecutionRecordTest(APITest):
    def setUp(self):
        super().setUp()
        self.project = Project.objects.create(
            id=int(TEST_PROJECT_ID), name=TEST_PROJECT_NAME, tenant_id="system", creator="tester"
        )
        self.template = TaskTemplate.objects.create(id=int(TEST_TEMPLATE_ID), project=self.project)

    def url(self):
        return "/apigw/get_node_execution_record/{template_id}/{project_id}/"

    def create_record(self, project, template, **overrides):
        now = timezone.now()
        fields = {
            "project_id": project.id,
            "trigger_template_id": str(template.id),
            "task_template_id": str(template.id),
            "template_node_id": TEST_TEMPLATE_NODE_ID,
            "node_id": "executed-node",
            "component_code": "job_execute_task",
            "instance_id": 1,
            "task_instance_id": 1,
            "template_id": "pipeline-template",
            "started_time": now,
            "archived_time": now,
            "instance_create_time": now,
            "elapsed_time": 10,
            "status": True,
            "is_skip": False,
        }
        fields.update(overrides)
        return TaskflowExecutedNodeStatistics.objects.create(**fields)

    def query_records(self, project, template_id):
        with mock.patch(PROJECT_GET, return_value=project):
            response = self.client.get(
                self.url().format(template_id=template_id, project_id=project.id),
                data={"template_node_id": TEST_TEMPLATE_NODE_ID, "scope": "project"},
                HTTP_X_BK_TENANT_ID="system",
            )
        return json.loads(response.content)

    def test_trusted_app_cannot_query_another_projects_template(self):
        for tenant_id in ("system", "another-tenant"):
            with self.subTest(tenant_id=tenant_id):
                project = Project.objects.create(name=tenant_id, tenant_id=tenant_id, creator="tester")
                template = TaskTemplate.objects.create(project=project)
                self.create_record(project, template)

                result = self.query_records(self.project, template.id)

                self.assertFalse(result["result"])
                self.assertEqual(result["code"], err_code.CONTENT_NOT_EXIST.code)

    def test_trusted_app_cannot_use_another_tenants_project(self):
        project = Project.objects.create(name="other", tenant_id="another-tenant", creator="tester")
        template = TaskTemplate.objects.create(project=project)
        self.create_record(project, template)

        result = self.query_records(project, template.id)

        self.assertFalse(result["result"])
        self.assertEqual(result["code"], err_code.CONTENT_NOT_EXIST.code)

    def test_missing_template_returns_not_found(self):
        result = self.query_records(self.project, 99999)

        self.assertFalse(result["result"])
        self.assertEqual(result["code"], err_code.CONTENT_NOT_EXIST.code)

    def test_records_are_limited_to_current_project_and_successful_nodes(self):
        self.create_record(self.project, self.template)
        other_project = Project.objects.create(name="other", tenant_id="another-tenant", creator="tester")
        self.create_record(other_project, self.template, elapsed_time=99)
        self.create_record(self.project, self.template, status=False)
        self.create_record(self.project, self.template, is_skip=True)

        result = self.query_records(self.project, self.template.id)

        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["total"], 1)
        self.assertEqual([row["elapsed_time"] for row in result["data"]["execution_time"]], [10])

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_get_node_execution_record_success(self):
        rows = [
            {"archived_time": datetime(2026, 1, 1, 10, 0, 0), "elapsed_time": 10},
            {"archived_time": datetime(2026, 1, 1, 10, 1, 0), "elapsed_time": 12},
        ]
        queryset = _NodeExecutionRecordQuerySet(rows)

        with mock.patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock(return_value=queryset)):
            response = self.client.get(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data={"template_node_id": TEST_TEMPLATE_NODE_ID},
            )

            data = json.loads(response.content)
            self.assertTrue(data["result"])
            self.assertEqual(data["data"]["total"], 2)
            self.assertEqual(len(data["data"]["execution_time"]), 2)
            self.assertEqual(queryset.sliced_limits, [(None, settings.MAX_RECORDED_NODE_EXECUTION_TIMES)])

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_get_node_execution_record_without_template_node_id(self):
        with mock.patch(TASKFLOWEXECUTEDNODE_STATISTICS_FILTER, MagicMock()):
            response = self.client.get(path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID))

            data = json.loads(response.content)
            self.assertFalse(data["result"])
            self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)

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


import ujson as json
from django.test import override_settings

from gcloud.contrib.audit.instances import AuditSnapshot
from gcloud.periodictask.models import PeriodicTask
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import TEST_USERNAME, APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_BIZ_CC_NAME = "biz name"
TEST_PERIODIC_TASK_ID = "3"


class SetPeriodicTaskEnabledAPITest(APITest):
    def url(self):
        return "/apigw/set_periodic_task_enabled/{task_id}/{project_id}/"

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
    def test_set_periodic_task_enabled__success(self):
        task = MockPeriodicTask()
        with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
            response = self.client.post(
                path=self.url().format(task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"enabled": True}),
                content_type="application/json",
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

            task.set_enabled.assert_called_once_with(True)
            self.assertEqual(task.editor, TEST_USERNAME)
            task.save.assert_called_once_with(update_fields=["editor", "edit_time"])

            data = json.loads(response.content)

            self.assertTrue(data["result"], msg=data)
            self.assertEqual(data["data"], {"enabled": task.enabled})

    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_set_periodic_task_enabled__task_does_not_exist(self):
        response = self.client.post(
            path=self.url().format(task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID),
            data=json.dumps({"enabled": True}),
            content_type="application/json",
        )

        data = json.loads(response.content)

        self.assertFalse(data["result"])
        self.assertTrue("message" in data)

    @override_settings(ENABLE_BK_AUDIT=True)
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
    def test_set_periodic_task_enabled__audit_uses_compact_before_and_after_snapshots(self):
        task = MockPeriodicTask(enabled=False)
        task.set_enabled.side_effect = lambda enabled: setattr(task, "enabled", enabled)

        with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
            with mock.patch("gcloud.apigw.views.set_periodic_task_enabled.bk_audit_add_event_on_commit") as add_event:
                response = self.client.post(
                    path=self.url().format(task_id=TEST_PERIODIC_TASK_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps({"enabled": True}),
                    content_type="application/json",
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(
            add_event.call_args[1]["origin_data"],
            AuditSnapshot(
                {
                    "id": task.id,
                    "name": task.name,
                    "cron": task.cron,
                    "enabled": False,
                    "template_id": task.template_id,
                    "template_source": task.template_source,
                    "template_version": task.template_version,
                    "creator": task.creator,
                    "editor": "editor",
                }
            ),
        )
        self.assertEqual(
            add_event.call_args[1]["data"],
            AuditSnapshot(
                {
                    "id": task.id,
                    "name": task.name,
                    "cron": task.cron,
                    "enabled": True,
                    "template_id": task.template_id,
                    "template_source": task.template_source,
                    "template_version": task.template_version,
                    "creator": task.creator,
                    "editor": TEST_USERNAME,
                }
            ),
        )

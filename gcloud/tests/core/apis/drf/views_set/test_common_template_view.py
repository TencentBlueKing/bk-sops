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

from unittest.mock import patch

import factory
from django.db.models import signals
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import LoginExemptMixin, StandardResponseAssertionMixin
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin
from django_test_toolkit.testcases import ToolkitApiTestCase
from pipeline.models import PipelineTemplate, Snapshot

from gcloud.common_template.models import CommonTemplate


class TestCommonTemplateView(
    ToolkitApiTestCase,
    SuperUserMixin,
    LoginExemptMixin,
    DrfPermissionExemptMixin,
    StandardResponseAssertionMixin,
):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        super(TestCommonTemplateView, self).setUp()
        self.test_snapshot = Snapshot.objects.create_snapshot({})
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id="template_id", creator="creator", snapshot=self.test_snapshot
        )
        self.template_url = "/api/v3/common_template/"
        self.common_template = CommonTemplate.objects.create(
            category="category",
            pipeline_template=self.pipeline_template,
        )
        self.mock_referencer_data = [
            {"template_type": "project", "id": 2, "name": "test_task_template", "project_id": 100},
        ]

    def test_filter_project_template(self):
        query_params = {"project_id": 1}
        response = self.client.get(self.template_url, data=query_params)
        self.assertTrue(response.data["result"])
        self.assertIsNotNone(response.data["data"])

    def test_update_common_template(self):
        self.template_url = "/api/v3/common_template/{}/update_specific_fields/".format(self.common_template.id)
        query_params = {"project_scope": ["1"]}
        response = self.client.post(self.template_url, data=query_params, format="json")
        self.assertTrue(response.data["result"])
        self.assertIsNotNone(response.data["data"])

    def test_update_common_template_fail(self):
        with patch.object(CommonTemplate, "referencer", return_value=self.mock_referencer_data) as mock_referencer:
            self.template_url = "/api/v3/common_template/{}/update_specific_fields/".format(self.common_template.id)
            query_params = {"project_scope": ["1"]}
            response = self.client.post(self.template_url, data=query_params, format="json")
            self.assertFalse(response.data["result"])
            mock_referencer.assert_called_once()

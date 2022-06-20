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

from mock import patch, MagicMock, call

from django.test import TestCase


from gcloud.taskflow3.celery.tasks import _ensure_node_can_retry


class EnsureNodeCanRetryTestCase(TestCase):
    def test_engine_ver_invalid(self):
        self.assertRaises(ValueError, _ensure_node_can_retry, "node_id", 3)

    def test_engine_v1_can_retry(self):
        PipelineProcess = MagicMock()
        PipelineProcess.objects.filter().exists = MagicMock(return_value=True)
        PipelineProcess.objects.filter.reset_mock()
        node_id = "node_id"

        with patch("gcloud.taskflow3.celery.tasks.PipelineProcess", PipelineProcess):
            can_retry = _ensure_node_can_retry(node_id, engine_ver=1)

        self.assertTrue(can_retry)
        PipelineProcess.objects.filter.assert_called_once_with(current_node_id=node_id, is_sleep=True)

    def test_engine_v1_can_not_retry(self):
        PipelineProcess = MagicMock()
        PipelineProcess.objects.filter().exists = MagicMock(return_value=False)
        PipelineProcess.objects.filter.reset_mock()
        node_id = "node_id"

        with patch("gcloud.taskflow3.celery.tasks.PipelineProcess", PipelineProcess):
            can_retry = _ensure_node_can_retry(node_id, engine_ver=1)

        self.assertFalse(can_retry)
        PipelineProcess.objects.filter.assert_has_calls(
            [
                call(current_node_id="node_id", is_sleep=True),
                call().exists(),
                call(current_node_id="node_id", is_sleep=True),
                call().exists(),
                call(current_node_id="node_id", is_sleep=True),
                call().exists(),
            ]
        )

    def test_engine_v2_can_retry(self):
        BambooDjangoRuntime = MagicMock()
        BambooDjangoRuntime().get_sleep_process_info_with_current_node_id = MagicMock(return_value=True)
        node_id = "node_id"

        with patch("gcloud.taskflow3.celery.tasks.BambooDjangoRuntime", BambooDjangoRuntime):
            can_retry = _ensure_node_can_retry(node_id, engine_ver=2)

        self.assertTrue(can_retry)
        BambooDjangoRuntime().get_sleep_process_info_with_current_node_id.assert_called_once_with(node_id)

    def test_engine_v2_can_not_retry(self):
        BambooDjangoRuntime = MagicMock()
        BambooDjangoRuntime().get_sleep_process_info_with_current_node_id = MagicMock(return_value=None)
        node_id = "node_id"

        with patch("gcloud.taskflow3.celery.tasks.BambooDjangoRuntime", BambooDjangoRuntime):
            can_retry = _ensure_node_can_retry(node_id, engine_ver=2)

        self.assertFalse(can_retry)
        BambooDjangoRuntime().get_sleep_process_info_with_current_node_id.assert_has_calls(
            [call(node_id), call(node_id), call(node_id)]
        )

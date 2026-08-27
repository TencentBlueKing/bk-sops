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

from django.test import SimpleTestCase
from mock import MagicMock, patch

from gcloud.taskflow3.celery.tasks import async_node_callback_retry


class AsyncNodeCallbackRetryTestCase(SimpleTestCase):
    engine_ver = 2
    node_id = "node_id"
    node_version = "callback_version"
    taskflow_id = 1
    project_id = 2

    def _run_retry(self, current_state, retry_times=3):
        callback_result = {
            "result": False,
            "message": (
                "fail: Traceback (most recent call last):\n"
                "InvalidOperationError: can not find sleep process with current node id: node_id"
            ),
            "code": 3599999,
        }
        dispatcher = MagicMock()
        dispatcher.dispatch.return_value = callback_result
        runtime = MagicMock()
        runtime.get_state_or_none.return_value = current_state
        trace_context = MagicMock()

        with patch("gcloud.taskflow3.celery.tasks.NodeCommandDispatcher", return_value=dispatcher):
            with patch("gcloud.taskflow3.celery.tasks.BambooDjangoRuntime", return_value=runtime):
                with patch("gcloud.taskflow3.celery.tasks.start_trace", return_value=trace_context):
                    with self.assertLogs("celery", level="WARNING") as captured:
                        result = async_node_callback_retry(
                            engine_ver=self.engine_ver,
                            node_id=self.node_id,
                            node_version=self.node_version,
                            callback_data={"status": 3},
                            taskflow_id=self.taskflow_id,
                            project_id=self.project_id,
                            retry_times=retry_times,
                        )

        return result, "\n".join(captured.output)

    def test_stale_callback_is_not_logged_as_actionable_failure(self):
        current_state = SimpleNamespace(version="current_version", name="FINISHED", skip=False)

        result, logs = self._run_retry(current_state)

        self.assertFalse(result["result"])
        self.assertIn("outcome=stale_callback_ignored", logs)
        self.assertIn("reason=node_version_mismatch", logs)
        self.assertIn("callback_node_version=callback_version", logs)
        self.assertIn("current_node_version=current_version", logs)
        self.assertNotIn("outcome=actionable_callback_failure", logs)

    def test_finished_current_version_is_logged_as_stale_callback(self):
        current_state = SimpleNamespace(version=self.node_version, name="FINISHED", skip=True)

        _, logs = self._run_retry(current_state)

        self.assertIn("outcome=stale_callback_ignored", logs)
        self.assertIn("reason=node_already_terminal", logs)
        self.assertIn("current_node_skip=True", logs)

    def test_active_current_version_keeps_actionable_error_log(self):
        current_state = SimpleNamespace(version=self.node_version, name="RUNNING", skip=False)

        _, logs = self._run_retry(current_state)

        self.assertIn("outcome=actionable_callback_failure", logs)
        self.assertIn("reason=active_node_retry_exhausted", logs)
        self.assertIn("error_reason=sleep_process_missing", logs)
        self.assertNotIn("callback failed after async retry", logs)

    def test_retry_scheduled_log_does_not_repeat_traceback(self):
        current_state = SimpleNamespace(version=self.node_version, name="RUNNING", skip=False)

        _, logs = self._run_retry(current_state, retry_times=0)

        self.assertIn("outcome=retry_scheduled", logs)
        self.assertIn("error_reason=sleep_process_missing", logs)
        self.assertNotIn("Traceback", logs)

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

from mock import patch, MagicMock

from django.test import TestCase


from gcloud.taskflow3.celery.tasks import auto_retry_node


class AutoRetryNodeTestCase(TestCase):
    def test_lock_fetch_fail(self):
        settings = MagicMock()
        settings.redis_inst.set = MagicMock(return_value=False)
        _ensure_node_can_retry = MagicMock()

        taskflow_id = 1
        root_pipeline_id = "root"
        node_id = "node_id"
        retry_times = 1
        engine_ver = 2

        with patch("gcloud.taskflow3.celery.tasks.settings", settings):
            with patch("gcloud.taskflow3.celery.tasks._ensure_node_can_retry", _ensure_node_can_retry):
                auto_retry_node(
                    taskflow_id=taskflow_id,
                    root_pipeline_id=root_pipeline_id,
                    node_id=node_id,
                    retry_times=retry_times,
                    engine_ver=engine_ver,
                )

        settings.redis_inst.set.assert_called_once_with(
            name="%s-%s-%s" % (root_pipeline_id, node_id, retry_times), value=1, nx=True, ex=5
        )
        _ensure_node_can_retry.assert_not_called()

    def test_node_can_not_retry(self):
        settings = MagicMock()
        _ensure_node_can_retry = MagicMock(return_value=False)

        taskflow_id = 1
        root_pipeline_id = "root"
        node_id = "node_id"
        retry_times = 1
        engine_ver = 2

        with patch("gcloud.taskflow3.celery.tasks.settings", settings):
            with patch("gcloud.taskflow3.celery.tasks._ensure_node_can_retry", _ensure_node_can_retry):
                auto_retry_node(
                    taskflow_id=taskflow_id,
                    root_pipeline_id=root_pipeline_id,
                    node_id=node_id,
                    retry_times=retry_times,
                    engine_ver=engine_ver,
                )

        lock_name = "%s-%s-%s" % (root_pipeline_id, node_id, retry_times)
        settings.redis_inst.set.assert_called_once_with(name=lock_name, value=1, nx=True, ex=5)
        _ensure_node_can_retry.assert_called_once_with(node_id=node_id, engine_ver=engine_ver)
        settings.redis_inst.delete.assert_called_once_with(lock_name)

    def test_success(self):
        settings = MagicMock()
        _ensure_node_can_retry = MagicMock()
        NodeCommandDispatcher = MagicMock()

        taskflow_id = 1
        root_pipeline_id = "root"
        node_id = "node_id"
        retry_times = 1
        engine_ver = 2

        with patch("gcloud.taskflow3.celery.tasks.settings", settings):
            with patch("gcloud.taskflow3.celery.tasks._ensure_node_can_retry", _ensure_node_can_retry):
                with patch("gcloud.taskflow3.celery.tasks.NodeCommandDispatcher", NodeCommandDispatcher):
                    auto_retry_node(
                        taskflow_id=taskflow_id,
                        root_pipeline_id=root_pipeline_id,
                        node_id=node_id,
                        retry_times=retry_times,
                        engine_ver=engine_ver,
                    )

        lock_name = "%s-%s-%s" % (root_pipeline_id, node_id, retry_times)
        settings.redis_inst.set.assert_called_once_with(name=lock_name, value=1, nx=True, ex=5)
        _ensure_node_can_retry.assert_called_once_with(node_id=node_id, engine_ver=engine_ver)
        NodeCommandDispatcher.assert_called_once_with(engine_ver=engine_ver, node_id=node_id, taskflow_id=taskflow_id)
        NodeCommandDispatcher().dispatch.assert_called_once_with(command="retry", operator="system", inputs={})
        settings.redis_inst.delete.assert_called_once_with(lock_name)

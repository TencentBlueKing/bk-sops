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

from unittest.mock import MagicMock, patch

import ujson as json

from gcloud import err_code

from .utils import APITest

TEST_TASKFLOW_ID = "2"
TEST_BIZ_CC_ID = "123"
TEST_NODE_ID = "node_id"


class _ForInnerTrustGateBase(APITest):
    """``*_for_inner`` 接口的统一安全要求：``request.is_trust=False`` 必须直接拒绝。

    在 ``mark_request_whether_is_trust`` 装饰器中，``request.is_trust`` 由
    ``check_white_apps(request)`` 决定。这里通过 patch
    ``gcloud.apigw.decorators.check_white_apps`` 强制返回 False，验证视图函数返回
    ``REQUEST_FORBIDDEN_INVALID``，并且后续真正读数据的 fetch 函数从未被调用。
    """

    url_path = None
    fetch_target = None
    request_params = None

    def setUp(self):
        super().setUp()
        if self.fetch_target:
            self.fetch_patcher = patch(
                self.fetch_target,
                MagicMock(return_value={"result": True, "message": "success", "data": "log"}),
            )
            self.mock_fetch = self.fetch_patcher.start()
        else:
            self.mock_fetch = None

    def tearDown(self):
        if self.mock_fetch is not None:
            self.fetch_patcher.stop()
        super().tearDown()

    def _call(self):
        return self.client.get(path=self.url_path, data=self.request_params or {})

    def _assert_forbidden(self, response):
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)
        if self.mock_fetch is not None:
            self.mock_fetch.assert_not_called()


class GetTaskNodeLogForInnerTrustTest(_ForInnerTrustGateBase):
    url_path = "/apigw/inner/get_task_node_log/"
    fetch_target = "gcloud.apigw.views.get_task_node_log_for_inner.fetch_task_node_log"
    request_params = {"node_id": TEST_NODE_ID, "version": "legacy"}

    def url(self):
        return self.url_path

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=False))
    def test_untrusted_app_is_forbidden(self):
        self._assert_forbidden(self._call())

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=True))
    def test_trusted_app_can_proceed(self):
        response = self._call()
        self.assertEqual(response.status_code, 200)
        self.mock_fetch.assert_called_once()


class GetNodeJobExecutedLogForInnerTrustTest(_ForInnerTrustGateBase):
    url_path = "/apigw/inner/get_node_job_executed_log/"
    fetch_target = "gcloud.apigw.views.get_node_job_executed_log_for_inner.fetch_node_job_executed_log"
    request_params = {
        "node_id": TEST_NODE_ID,
        "bk_biz_id": TEST_BIZ_CC_ID,
        "job_scope_type": "biz",
        "component_code": "job_execute_task_v2",
    }

    def url(self):
        return self.url_path

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=False))
    def test_untrusted_app_is_forbidden(self):
        self._assert_forbidden(self._call())


class GetTaskEffectiveTimeForInnerTrustTest(_ForInnerTrustGateBase):
    url_path = "/apigw/inner/get_task_effective_time/{task_id}/{bk_biz_id}/".format(
        task_id=TEST_TASKFLOW_ID, bk_biz_id=TEST_BIZ_CC_ID
    )
    # is_trust 在 effective_time_for_task 之前就拦截，因此这里 patch 一个 sentinel，
    # 用来验证拒绝路径上确实不会触达统计逻辑。
    fetch_target = "gcloud.apigw.views.get_task_effective_time_for_inner.effective_time_for_task"

    def url(self):
        return self.url_path

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=False))
    def test_untrusted_app_is_forbidden(self):
        self._assert_forbidden(self._call())


class GetTaskPluginLogForInnerTrustTest(_ForInnerTrustGateBase):
    """plugin 接口在 ``mark_request_whether_is_trust`` 内部嵌套了 ``validate_params``，
    is_trust 设置发生在 validate_params 之前，但 ``if not request.is_trust`` 的判断
    在函数体里、在 validate_params 通过之后。为了让流程能进入函数体，本测试同时提供
    LogQuerySerializer 必填字段。"""

    url_path = "/apigw/inner/get_task_plugin_log/"
    fetch_target = "gcloud.apigw.views.get_task_plugin_log_for_inner.fetch_task_plugin_log"
    request_params = {
        "plugin_code": "demo_plugin",
        "trace_id": "trace-xyz",
    }

    def url(self):
        return self.url_path

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=False))
    def test_untrusted_app_is_forbidden(self):
        self._assert_forbidden(self._call())

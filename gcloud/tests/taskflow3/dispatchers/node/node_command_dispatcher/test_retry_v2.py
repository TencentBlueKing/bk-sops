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

from django.test import TestCase

from gcloud import err_code
from gcloud.taskflow3.domains.dispatchers.node import NodeCommandDispatcher

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class RetryV2TestCase(TestCase):
    def test_get_node_data_fail(self):
        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        err_return = MagicMock()
        err_return.result = False
        err_return.message = "error"
        bamboo_api = MagicMock()
        bamboo_api.get_data = MagicMock(return_value=err_return)

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                result = dispatcher.retry_v2(operator="tester", inputs={})

        bamboo_api.get_data.assert_called_once_with(runtime=runtime, node_id="node_id")
        self.assertEqual(result, {"result": False, "message": "error", "code": err_code.UNKNOWN_ERROR.code})

    def test_no_executor_proxy(self):
        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        get_data_return = MagicMock()
        get_data_return.result = True
        get_data_return.data = {"inputs": {}}
        retry_node_return = MagicMock()
        retry_node_return.result = True
        retry_node_return.message = "success"
        bamboo_api = MagicMock()
        bamboo_api.get_data = MagicMock(return_value=get_data_return)
        bamboo_api.retry_node = MagicMock(return_value=retry_node_return)

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                result = dispatcher.retry_v2(operator="tester", inputs={})

        bamboo_api.get_data.assert_called_once_with(runtime=runtime, node_id="node_id")
        bamboo_api.retry_node.assert_called_once_with(runtime=runtime, node_id="node_id", data=None)
        self.assertEqual(result, {"result": True, "code": err_code.SUCCESS.code, "message": "success"})

    def test_with_executor_proxy(self):
        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        get_data_return = MagicMock()
        get_data_return.result = True
        get_data_return.data = {"inputs": {"__executor_proxy": {"value": "admin"}}}
        retry_node_return = MagicMock()
        retry_node_return.result = True
        retry_node_return.message = "success"
        bamboo_api = MagicMock()
        bamboo_api.get_data = MagicMock(return_value=get_data_return)
        bamboo_api.retry_node = MagicMock(return_value=retry_node_return)

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                result = dispatcher.retry_v2(operator="tester", inputs={"k": "v"})

        bamboo_api.get_data.assert_called_once_with(runtime=runtime, node_id="node_id")
        bamboo_api.retry_node.assert_called_once_with(
            runtime=runtime, node_id="node_id", data={"__executor_proxy": "admin", "k": "v"}
        )
        self.assertEqual(result, {"result": True, "code": err_code.SUCCESS.code, "message": "success"})

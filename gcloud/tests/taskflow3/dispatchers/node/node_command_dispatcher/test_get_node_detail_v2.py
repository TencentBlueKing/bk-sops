# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
from bamboo_engine import states as bamboo_engine_states

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class GetNodeDetailV2TestCase(TestCase):
    def test_node_not_stated(self):
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1
        pipeline_instance = MagicMock()
        kwargs = {"pipeline_instance": pipeline_instance}

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        bamboo_api = MagicMock()
        get_children_states_return = MagicMock()
        get_children_states_return.result = True
        get_children_states_return.data = {}
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"name": "node_name", "error_ignorable": True})

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_detail = dispatcher.get_node_detail(
                    username=username,
                    subprocess_stack=subprocess_stack,
                    component_code=component_code,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        dispatcher._get_node_info.assert_called_once_with(
            node_id=dispatcher.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
        )

        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {"name": "node_name", "error_ignorable": True, "state": bamboo_engine_states.READY},
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

    def test_node_started_loop_is_none(self):
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = None
        pipeline_instance = MagicMock()
        kwargs = {"pipeline_instance": pipeline_instance}

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        bamboo_api = MagicMock()
        get_children_states_return = MagicMock()
        get_children_states_return.result = True
        get_children_states_return.data = {"node_id": {"name": "node_name", "loop": 1}}
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        get_node_histories_return = MagicMock()
        get_node_histories_return.result = True
        get_node_histories_return.data = [{"outputs": {}, "id": "hid"}]
        bamboo_api.get_node_histories = MagicMock(return_value=get_node_histories_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        format_pipeline_status = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                with patch(TASKFLOW_DISPATCHERS_NODE_FORMAT_PIPELINE_STATUS, format_pipeline_status):
                    node_detail = dispatcher.get_node_detail(
                        username=username,
                        subprocess_stack=subprocess_stack,
                        component_code=component_code,
                        loop=loop,
                        **kwargs
                    )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_node_histories.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id, loop=1)
        dispatcher._get_node_info.assert_not_called()

        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {
                    "name": "node_name",
                    "loop": 1,
                    "histories": [
                        {
                            "outputs": {},
                            "ex_data": "",
                            "id": "hid",
                            "history_id": "hid",
                            "state": bamboo_engine_states.FAILED,
                        }
                    ],
                },
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

    def test_node_started_loop_is_latest(self):
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 2
        pipeline_instance = MagicMock()
        kwargs = {"pipeline_instance": pipeline_instance}

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        bamboo_api = MagicMock()
        get_children_states_return = MagicMock()
        get_children_states_return.result = True
        get_children_states_return.data = {"node_id": {"name": "node_name", "loop": 1}}
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        get_node_histories_return = MagicMock()
        get_node_histories_return.result = True
        get_node_histories_return.data = [{"outputs": {}, "id": "hid"}]
        bamboo_api.get_node_histories = MagicMock(return_value=get_node_histories_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        format_pipeline_status = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                with patch(TASKFLOW_DISPATCHERS_NODE_FORMAT_PIPELINE_STATUS, format_pipeline_status):
                    node_detail = dispatcher.get_node_detail(
                        username=username,
                        subprocess_stack=subprocess_stack,
                        component_code=component_code,
                        loop=loop,
                        **kwargs
                    )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_node_histories.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id, loop=1)
        dispatcher._get_node_info.assert_not_called()

        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {
                    "name": "node_name",
                    "loop": 1,
                    "histories": [
                        {
                            "outputs": {},
                            "ex_data": "",
                            "id": "hid",
                            "history_id": "hid",
                            "state": bamboo_engine_states.FAILED,
                        }
                    ],
                },
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

    def test_node_started_loop_is_not_latest(self):
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1
        pipeline_instance = MagicMock()
        kwargs = {"pipeline_instance": pipeline_instance}

        runtime = "runtime"
        runtime_init = MagicMock(return_value=runtime)
        bamboo_api = MagicMock()
        get_children_states_return = MagicMock()
        get_children_states_return.result = True
        get_children_states_return.data = {
            "node_id": {"name": "node_name", "loop": 2, "histories": [{"id": "hid", "ex_data": ""}]}
        }
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        get_node_histories_return = MagicMock()
        get_node_histories_return.result = True
        get_node_histories_return.data = [{"outputs": {}, "id": "hid"}]
        bamboo_api.get_node_histories = MagicMock(return_value=get_node_histories_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        dispatcher._assemble_histroy_detail = MagicMock()
        format_pipeline_status = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                with patch(TASKFLOW_DISPATCHERS_NODE_FORMAT_PIPELINE_STATUS, format_pipeline_status):
                    node_detail = dispatcher.get_node_detail(
                        username=username,
                        subprocess_stack=subprocess_stack,
                        component_code=component_code,
                        loop=loop,
                        **kwargs
                    )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_node_histories.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id, loop=1)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._assemble_histroy_detail.assert_called_once()

        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {
                    "name": "node_name",
                    "loop": 2,
                    "histories": [
                        {"id": "hid", "history_id": "hid", "state": bamboo_engine_states.FAILED, "ex_data": ""}
                    ],
                },
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

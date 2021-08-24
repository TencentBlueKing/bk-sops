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
from pipeline.eri.models import ExecutionData

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class GetNodeDataV2TestCase(TestCase):
    def test_non_act_not_started(self):
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
        get_children_states_return.data = None
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "StartEvent"})

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_data = dispatcher.get_node_data_v2(
                    username=username,
                    component_code=component_code,
                    subprocess_stack=subprocess_stack,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        dispatcher._get_node_info.assert_called_once_with(
            node_id=dispatcher.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": {}, "outputs": [], "ex_data": ""},
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

    def test_act_not_started(self):
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
        get_children_states_return.data = None
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "ServiceActivity"})
        pre_render_inputs = "inputs"
        pre_render_outputs = {"ex_data": "ex_data"}
        dispatcher._prerender_node_data = MagicMock(return_value=(True, None, pre_render_inputs, pre_render_outputs))
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_data = dispatcher.get_node_data_v2(
                    username=username,
                    component_code=component_code,
                    subprocess_stack=subprocess_stack,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        dispatcher._get_node_info.assert_called_once_with(
            node_id=dispatcher.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
        )
        dispatcher._prerender_node_data.assert_called_once_with(
            pipeline_instance=pipeline_instance, subprocess_stack=subprocess_stack, username=username
        )
        dispatcher._format_outputs.assert_called_once_with(
            outputs=pre_render_outputs,
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": pre_render_inputs, "outputs": format_outputs, "ex_data": "ex_data"},
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
        get_children_states_return.data = {"loop": 1}
        get_execution_data_return = MagicMock()
        get_execution_data_return.result = True
        get_execution_data_return.data = {"inputs": "inputs", "outputs": {}}
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        bamboo_api.get_execution_data = MagicMock(return_value=get_execution_data_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "ServiceActivity"})
        dispatcher._prerender_node_data = MagicMock()
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_data = dispatcher.get_node_data_v2(
                    username=username,
                    component_code=component_code,
                    subprocess_stack=subprocess_stack,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_execution_data.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_called_once_with(
            outputs={"outputs": {}},
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": "inputs", "outputs": format_outputs, "ex_data": None},
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
        get_children_states_return.data = {"loop": 1}
        get_execution_data_return = MagicMock()
        get_execution_data_return.result = True
        get_execution_data_return.data = {"inputs": "inputs", "outputs": {}}
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        bamboo_api.get_execution_data = MagicMock(return_value=get_execution_data_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "ServiceActivity"})
        dispatcher._prerender_node_data = MagicMock()
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_data = dispatcher.get_node_data_v2(
                    username=username,
                    component_code=component_code,
                    subprocess_stack=subprocess_stack,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_execution_data.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_called_once_with(
            outputs={"outputs": {}},
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": "inputs", "outputs": format_outputs, "ex_data": None},
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

    def test_node_started_execution_data_not_exist(self):
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
        get_children_states_return.data = {"loop": 1}
        get_execution_data_return = MagicMock()
        get_execution_data_return.result = False
        get_execution_data_return.exc = ExecutionData.DoesNotExist()
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        bamboo_api.get_execution_data = MagicMock(return_value=get_execution_data_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "ServiceActivity"})
        dispatcher._prerender_node_data = MagicMock()
        dispatcher._format_outputs = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_data = dispatcher.get_node_data_v2(
                    username=username,
                    component_code=component_code,
                    subprocess_stack=subprocess_stack,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_execution_data.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_not_called()
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": {}, "outputs": [], "ex_data": ""},
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
        get_children_states_return.data = {"loop": 2}
        get_node_histories_return = MagicMock()
        get_node_histories_return.result = True
        get_node_histories_return.data = [{"inputs": "inputs", "outputs": {}}]
        bamboo_api.get_children_states = MagicMock(return_value=get_children_states_return)
        bamboo_api.get_node_histories = MagicMock(return_value=get_node_histories_return)

        dispatcher = NodeCommandDispatcher(engine_ver=2, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "ServiceActivity"})
        dispatcher._prerender_node_data = MagicMock()
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_RUNTIME, runtime_init):
            with patch(TASKFLOW_DISPATCHERS_NODE_BAMBOO_API, bamboo_api):
                node_data = dispatcher.get_node_data_v2(
                    username=username,
                    component_code=component_code,
                    subprocess_stack=subprocess_stack,
                    loop=loop,
                    **kwargs
                )

        bamboo_api.get_children_states.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id)
        bamboo_api.get_node_histories.assert_called_once_with(runtime=runtime, node_id=dispatcher.node_id, loop=loop)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_called_once_with(
            outputs={"outputs": {}},
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": "inputs", "outputs": format_outputs, "ex_data": None},
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

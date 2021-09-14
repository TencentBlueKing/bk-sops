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

from pipeline.engine import exceptions as pipeline_exceptions

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class GetNodeDataV1TestCase(TestCase):
    def test_non_act_not_started(self):
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1
        pipeline_instance = MagicMock()
        kwargs = {"pipeline_instance": pipeline_instance}

        pipeline_api = MagicMock()
        pipeline_api.get_status_tree = MagicMock(side_effect=pipeline_exceptions.InvalidOperationException)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "StartEvent"})

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            node_data = dispatcher.get_node_data_v1(
                username=username, component_code=component_code, subprocess_stack=subprocess_stack, loop=loop, **kwargs
            )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
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

        pipeline_api = MagicMock()
        pipeline_api.get_status_tree = MagicMock(side_effect=pipeline_exceptions.InvalidOperationException)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"type": "ServiceActivity"})
        pre_render_inputs = "inputs"
        pre_render_outputs = {"ex_data": "ex_data"}
        dispatcher._prerender_node_data = MagicMock(return_value=(True, None, pre_render_inputs, pre_render_outputs))
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            node_data = dispatcher.get_node_data_v1(
                username=username, component_code=component_code, subprocess_stack=subprocess_stack, loop=loop, **kwargs
            )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
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

        pipeline_api = MagicMock()
        inputs = "inputs"
        outputs = {"ex_data": "ex_data"}
        pipeline_api.get_inputs = MagicMock(return_value=inputs)
        pipeline_api.get_outputs = MagicMock(return_value=outputs)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        dispatcher._prerender_node_data = MagicMock()
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            node_data = dispatcher.get_node_data_v1(
                username=username, component_code=component_code, subprocess_stack=subprocess_stack, loop=loop, **kwargs
            )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_inputs.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_outputs.assert_called_once_with(dispatcher.node_id)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_called_once_with(
            outputs=outputs, component_code=component_code, pipeline_instance=pipeline_instance, subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": inputs, "outputs": format_outputs, "ex_data": "ex_data"},
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

        detail = {"loop": 1}
        pipeline_api = MagicMock()
        inputs = "inputs"
        outputs = {"ex_data": "ex_data"}
        pipeline_api.get_status_tree = MagicMock(return_value=detail)
        pipeline_api.get_inputs = MagicMock(return_value=inputs)
        pipeline_api.get_outputs = MagicMock(return_value=outputs)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        dispatcher._prerender_node_data = MagicMock()
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            node_data = dispatcher.get_node_data_v1(
                username=username, component_code=component_code, subprocess_stack=subprocess_stack, loop=loop, **kwargs
            )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_inputs.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_outputs.assert_called_once_with(dispatcher.node_id)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_called_once_with(
            outputs=outputs, component_code=component_code, pipeline_instance=pipeline_instance, subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": inputs, "outputs": format_outputs, "ex_data": "ex_data"},
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

        detail = {"loop": 2}
        histories = [{"inputs": "inputs", "outputs": "outputs", "ex_data": "ex_data"}]
        pipeline_api = MagicMock()
        pipeline_api.get_status_tree = MagicMock(return_value=detail)
        pipeline_api.get_activity_histories = MagicMock(return_value=histories)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        dispatcher._prerender_node_data = MagicMock()
        format_outputs = "format_outputs"
        dispatcher._format_outputs = MagicMock(return_value=(True, None, format_outputs))

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            node_data = dispatcher.get_node_data_v1(
                username=username, component_code=component_code, subprocess_stack=subprocess_stack, loop=loop, **kwargs
            )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_activity_histories.assert_called_once_with(node_id=dispatcher.node_id, loop=loop)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._prerender_node_data.assert_not_called()
        dispatcher._format_outputs.assert_called_once_with(
            outputs={"outputs": "outputs"},
            component_code=component_code,
            pipeline_instance=pipeline_instance,
            subprocess_stack=["1"],
        )
        self.assertEqual(
            node_data,
            {
                "result": True,
                "data": {"inputs": "inputs", "outputs": format_outputs, "ex_data": "ex_data"},
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

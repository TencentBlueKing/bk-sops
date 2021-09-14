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

from pipeline.engine import states as pipeline_states
from pipeline.engine import exceptions as pipeline_exceptions

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class GetNodeDetailV1TestCase(TestCase):
    def test_node_not_stated(self):
        username = "username"
        component_code = "component_code"
        subprocess_stack = ["1"]
        loop = 1
        pipeline_instance = MagicMock()
        kwargs = {"pipeline_instance": pipeline_instance}

        pipeline_api = MagicMock()
        pipeline_api.get_status_tree = MagicMock(side_effect=pipeline_exceptions.InvalidOperationException)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock(return_value={"name": "node_name", "error_ignorable": True})

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            node_detail = dispatcher.get_node_detail_v1(
                username=username,
                subprocess_stack=subprocess_stack,
                component_code=component_code,
                loop=loop,
                **kwargs,
            )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        dispatcher._get_node_info.assert_called_once_with(
            node_id=dispatcher.node_id, pipeline=pipeline_instance.execution_data, subprocess_stack=subprocess_stack
        )
        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {
                    "name": "node_name",
                    "error_ignorable": True,
                    "error_ignored": True,
                    "state": pipeline_states.READY,
                },
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
        detail = {"loop": 1}
        pipeline_api.get_status_tree = MagicMock(return_value=detail)
        histories = [{}]
        pipeline_api.get_activity_histories = MagicMock(return_value=histories)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        format_pipeline_status = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            with patch(TASKFLOW_DISPATCHERS_NODE_FORMAT_PIPELINE_STATUS, format_pipeline_status):
                node_detail = dispatcher.get_node_detail_v1(
                    username=username,
                    subprocess_stack=subprocess_stack,
                    component_code=component_code,
                    loop=loop,
                    **kwargs,
                )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_status_tree.get_activity_histories(node_id=dispatcher.node_id, loop=loop)
        dispatcher._get_node_info.assert_not_called()
        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {"loop": 1, "histories": [{"state": pipeline_states.FAILED}]},
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

        pipeline_api = MagicMock()
        detail = {"loop": 1}
        pipeline_api.get_status_tree = MagicMock(return_value=detail)
        histories = [{}]
        pipeline_api.get_activity_histories = MagicMock(return_value=histories)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        format_pipeline_status = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            with patch(TASKFLOW_DISPATCHERS_NODE_FORMAT_PIPELINE_STATUS, format_pipeline_status):
                node_detail = dispatcher.get_node_detail_v1(
                    username=username,
                    subprocess_stack=subprocess_stack,
                    component_code=component_code,
                    loop=loop,
                    **kwargs,
                )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_status_tree.get_activity_histories(node_id=dispatcher.node_id, loop=loop)
        dispatcher._get_node_info.assert_not_called()
        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {"loop": 1, "histories": [{"state": pipeline_states.FAILED}]},
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

        pipeline_api = MagicMock()
        detail = {"loop": 2, "histories": [{}]}
        pipeline_api.get_status_tree = MagicMock(return_value=detail)
        histories = [{}]
        pipeline_api.get_activity_histories = MagicMock(return_value=histories)
        dispatcher = NodeCommandDispatcher(engine_ver=1, node_id="node_id")
        dispatcher._get_node_info = MagicMock()
        dispatcher._assemble_histroy_detail = MagicMock()
        format_pipeline_status = MagicMock()

        with patch(TASKFLOW_DISPATCHERS_NODE_PIPELINE_API, pipeline_api):
            with patch(TASKFLOW_DISPATCHERS_NODE_FORMAT_PIPELINE_STATUS, format_pipeline_status):
                node_detail = dispatcher.get_node_detail_v1(
                    username=username,
                    subprocess_stack=subprocess_stack,
                    component_code=component_code,
                    loop=loop,
                    **kwargs,
                )

        pipeline_api.get_status_tree.assert_called_once_with(dispatcher.node_id)
        pipeline_api.get_status_tree.get_activity_histories(node_id=dispatcher.node_id, loop=loop)
        dispatcher._get_node_info.assert_not_called()
        dispatcher._assemble_histroy_detail.assert_called_once_with(detail=detail, histories=histories)
        self.assertEqual(
            node_detail,
            {
                "result": True,
                "data": {"loop": 2, "histories": [{"state": pipeline_states.FAILED}]},
                "message": "",
                "code": err_code.SUCCESS.code,
            },
        )

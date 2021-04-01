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

import itertools

from django.test import TestCase

from pipeline.core.flow.activity import SubProcess
from pipeline.engine.core import handlers
from pipeline.engine.core.handlers import subprocess as subprocess_h
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa

handlers.subprocess_handler = handlers.SubprocessHandler()


class SubprocessHandlerTestCase(TestCase):
    def test_element_cls(self):
        self.assertEqual(handlers.SubprocessHandler.element_cls(), SubProcess)

    @patch(SUBPROCESS_HYDRATE_NODE_DATA, MagicMock())
    def test_handle(self):
        for data_inputs, loop in itertools.product(({}, {"k1": "v1", "k2": "v2"}), (1, 2, 3)):
            hydrate_data_return = "hydate_data_return"
            top_context = MockContext()
            process = MockPipelineProcess(top_pipeline_context=top_context)
            data = MockData(get_inputs_return=data_inputs)
            context = MockContext()
            subprocess_act = MockSubprocessActivity(pipeline_data=data, pipeline_context=context)

            with patch(SUBPROCESS_HYDRATE_DATA, MagicMock(return_value=hydrate_data_return)):

                hdl_result = handlers.subprocess_handler(process, subprocess_act, MockStatus(loop=loop))

                if loop > 1:
                    subprocess_act.prepare_rerun_data.assert_called_once()
                    context.recover_variable.assert_called_once()
                    top_context.recover_variable.assert_called_once()
                else:
                    subprocess_act.prepare_rerun_data.assert_not_called()
                    context.recover_variable.assert_not_called()
                    top_context.recover_variable.assert_not_called()

                top_context.extract_output.assert_called_once_with(subprocess_act, set_miss=False)

                subprocess_h.hydrate_node_data.assert_called_once_with(subprocess_act)

                if data_inputs:
                    calls = [mock.call(k, v) for k, v in list(data_inputs.items())]
                    context.set_global_var.assert_has_calls(calls)

                subprocess_h.hydrate_data.assert_called_once_with(context.variables)

                context.update_global_var.assert_called_once_with(hydrate_data_return)

                process.push_pipeline.assert_called_once_with(subprocess_act.pipeline, is_subprocess=True)

                process.take_snapshot.assert_called_once()

                self.assertEqual(hdl_result.next_node, subprocess_act.pipeline.start_event)
                self.assertFalse(hdl_result.should_return)
                self.assertFalse(hdl_result.should_sleep)

                subprocess_h.hydrate_node_data.reset_mock()
                subprocess_h.hydrate_data.reset_mock()

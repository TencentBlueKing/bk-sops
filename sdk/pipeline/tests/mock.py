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

import mock
from mock import MagicMock, patch  # noqa

from pipeline.utils.collections import FancyDict
from pipeline.utils.uniqid import uniqid


def __reduce__(self):
    return (mock.MagicMock, ())


mock.mock.MagicMock.__reduce__ = __reduce__
mock.MagicMock.__reduce__ = __reduce__
MagicMock.__reduce__ = __reduce__


class Object(object):
    pass


class MockResponse(object):
    def __init__(self, **kwargs):
        self.content = kwargs.get("content")
        self.ok = kwargs.get("ok", True)


class ContextObject(object):
    def __init__(self, variables):
        self.variables = variables


class DataObject(object):
    def __init__(self, outputs=None):
        self._outputs = outputs or {}

    def get_outputs(self):
        return self._outputs


class IdentifyObject(object):
    def __init__(self, id=None, name=""):
        self.id = id or uniqid()
        self.name = name


class StartEventObject(IdentifyObject):
    def __init__(self, id=None, node=None):
        self.next = mock.MagicMock(return_value=node or uniqid())
        super(StartEventObject, self).__init__(id=id)


class EndEventObject(IdentifyObject):
    def __init__(self, id=None):
        self.pipeline_finish = mock.MagicMock()
        super(EndEventObject, self).__init__(id=id)


class ExecutableEndEventObject(IdentifyObject):
    def __init__(self, id=None):
        self.pipeline_finish = mock.MagicMock()
        self.execute = mock.MagicMock()
        self.data = mock.MagicMock()
        self.data.outputs = mock.MagicMock()
        super(ExecutableEndEventObject, self).__init__(id=id)


class PipelineSpecObject(object):
    def __init__(self, activities=None):
        self.activities = activities or {}


class PipelineObject(IdentifyObject):
    def __init__(self, context=None, data=None, node=None, nodes=None, start_event=None, spec=None):
        self._start_event = StartEventObject()
        self.context = context
        self.data = data
        self.real_node = node
        self.nodes = nodes or {}
        self.start_event = start_event or StartEventObject()
        self.spec = spec or PipelineSpecObject()
        self.prune = MagicMock()
        super(PipelineObject, self).__init__()

    def node(self, node_id):
        return self.nodes.get(node_id) or self.real_node or node_id

    def shell(self):
        return self


class StatusObject(IdentifyObject):
    def __init__(self, state, id=None):
        self.state = state
        super(StatusObject, self).__init__(id=id)


class StaticIntervalObject(Object):
    def __init__(self, interval):
        self.interval = interval

    def next(self):
        return self.interval


class ServiceActObject(IdentifyObject):
    def __init__(
        self,
        interval=None,
        id=None,
        schedule_return=True,
        execute_return=True,
        execute_pre_process_return=True,
        schedule_exception=None,
        execute_exception=None,
        execute_pre_process_exception=None,
        timeout=None,
        error_ignorable=False,
        is_schedule_done=False,
        result_bit=True,
        data=None,
        need_schedule=False,
        multi_callback_enabled=False,
        on_retry=False,
    ):
        self.service = Object()
        self.service.interval = interval
        self.service.multi_callback_enabled = mock.MagicMock(return_value=multi_callback_enabled)
        self.schedule = (
            mock.MagicMock(return_value=schedule_return)
            if not schedule_exception
            else mock.MagicMock(side_effect=schedule_exception)
        )
        self.execute_pre_process = (
            mock.MagicMock(return_value=execute_pre_process_return)
            if not execute_pre_process_exception
            else mock.MagicMock(side_effect=execute_pre_process_exception)
        )
        self.execute = (
            mock.MagicMock(return_value=execute_return)
            if not execute_exception
            else mock.MagicMock(side_effect=execute_exception)
        )
        self.timeout = timeout
        self._next = IdentifyObject()
        self.schedule_fail = mock.MagicMock()
        self.error_ignorable = error_ignorable
        self.ignore_error = mock.MagicMock()
        self.finish_schedule = mock.MagicMock()
        self.is_schedule_done = mock.MagicMock(return_value=is_schedule_done)
        self.get_result_bit = mock.MagicMock(return_value=result_bit)
        self.prepare_rerun_data = mock.MagicMock()
        self.data = data or MockData()
        self.failure_handler = mock.MagicMock()
        self.need_schedule = mock.MagicMock(return_value=need_schedule)
        self.shell = mock.MagicMock(return_value=self)
        self.on_retry = mock.MagicMock(return_value=on_retry)
        self.retry_at_current_exec = mock.MagicMock()
        self.setup_runtime_attrs = mock.MagicMock()
        super(ServiceActObject, self).__init__(id)

    def next(self):
        return self._next


class SubprocessObject(IdentifyObject):
    def __init__(self, id=None, pipeline=None):
        self.pipeline = pipeline or PipelineObject()
        super(SubprocessObject, self).__init__(id)


class MockPipelineModel(IdentifyObject):
    def __init__(self, **kwargs):
        self.process = kwargs.get("process", MockPipelineProcess())
        super(MockPipelineModel, self).__init__(kwargs.get("id"))


class MockPipelineProcess(IdentifyObject):
    def __init__(self, *args, **kwargs):
        super(MockPipelineProcess, self).__init__(id=kwargs.get("id"))

        self.is_alive = kwargs.get("is_alive", True)
        self.root_pipeline = kwargs.get(
            "root_pipeline",
            PipelineObject(data=kwargs.get("root_pipeline_data"), context=kwargs.get("root_pipeline_context")),
        )
        self.root_pipeline_id = self.root_pipeline.id
        self.top_pipeline = kwargs.get(
            "top_pipeline",
            PipelineObject(
                data=kwargs.get("top_pipeline_data"),
                context=kwargs.get("top_pipeline_context"),
                spec=kwargs.get("top_pipeline_spec"),
            ),
        )
        self.current_node_id = kwargs.get("current_node_id")
        self.destination_id = kwargs.get("destination_id")
        self.current_node_id = kwargs.get("current_node_id")
        self.wake_up = mock.MagicMock()
        self.destroy_and_wake_up_parent = mock.MagicMock()
        self.root_sleep_check = mock.MagicMock()
        self.subproc_sleep_check = mock.MagicMock()
        self.refresh_current_node = mock.MagicMock()
        self.sleep = mock.MagicMock()
        self.freeze = mock.MagicMock()
        self.exit_gracefully = mock.MagicMock()
        self.adjust_status = mock.MagicMock()
        self.is_alive = kwargs.get("is_alive", True)
        self.save = mock.MagicMock()
        self.push_pipeline = mock.MagicMock()
        self.join = mock.MagicMock()
        self.destroy = mock.MagicMock()
        self.pipeline_stack = [self.top_pipeline] + kwargs.get("pipeline_stack", [])
        self.sync_with_children = mock.MagicMock(**{"side_effect": kwargs.get("sync_exception")})
        self.children = kwargs.get("children", [])
        self.clean_children = mock.MagicMock()
        self.revoke_subprocess = mock.MagicMock()
        self.destroy_all = mock.MagicMock()
        self.subprocess_stack = kwargs.get("subprocess_stack", [])
        self.can_be_waked = mock.MagicMock(return_value=kwargs.get("can_be_waked", False))
        self.subproc_sleep_check = mock.MagicMock(
            return_value=kwargs.get("subproc_sleep_check_return", (False, [self.id]))
        )
        self.in_subprocess = mock.MagicMock(return_value=kwargs.get("in_subprocess_return", False))
        self.take_snapshot = mock.MagicMock()

    def pop_pipeline(self):
        return self.pipeline_stack.pop()


class MockActionResult(object):
    def __init__(self, result, message=None, extra=None):
        self.result = result
        self.message = message or ""
        self.extra = extra


class MockHandlerResult(object):
    def __init__(self, should_return, should_sleep, next_node=None, after_sleep_call=None, args=[], kwargs={}):
        self.should_return = should_return
        self.should_sleep = should_sleep
        self.next_node = next_node or IdentifyObject()
        self.after_sleep_call = after_sleep_call
        self.args = args
        self.kwargs = kwargs


class MockScheduleService(object):
    def __init__(self, id=None, **kwargs):
        self.id = id or ("{}{}".format(uniqid(), uniqid()))
        self.activity_id = self.id[:32]
        self.version = self.id[32:]
        self.destroy = mock.MagicMock()
        self.service_act = ServiceActObject(
            interval=None,
            id=self.activity_id,
            schedule_return=kwargs.get("schedule_return"),
            schedule_exception=kwargs.get("schedule_exception"),
            timeout=kwargs.get("service_timeout"),
            error_ignorable=kwargs.get("service_err_ignore", False),
            is_schedule_done=kwargs.get("schedule_done", False),
            result_bit=kwargs.get("result_bit", True),
        )
        self.callback_data = kwargs.get("callback_data", "callback_data")
        self.wait_callback = kwargs.get("wait_callback", False)
        self.multi_callback_enabled = kwargs.get("multi_callback_enabled", False)
        self.process_id = kwargs.get("process_id", uniqid())
        self.is_finished = kwargs.get("is_finished", False)
        self.schedule_times = 0
        self.finish = mock.MagicMock()
        self.set_next_schedule = mock.MagicMock()
        self.callback = mock.MagicMock()
        self.save = mock.MagicMock()
        self.is_one_time_callback = mock.MagicMock(return_value=self.wait_callback and not self.multi_callback_enabled)


class MockQuerySet(object):
    def __init__(self, exists_return=True, get_return=None, first_return=None, qs=None):
        self.update = mock.MagicMock()
        self.exists = mock.MagicMock(return_value=exists_return)
        self.get = mock.MagicMock(return_value=get_return)
        self.first = mock.MagicMock(return_value=first_return)
        self.qs = qs

    def __iter__(self):
        return self.qs.__iter__()


class MockEngineModelStatus(object):
    def __init__(self, error_ignorable):
        self.error_ignorable = error_ignorable
        self.save = mock.MagicMock()


class MockData(object):
    def __init__(self, get_outputs_return=None, get_inputs_return=None, get_one_of_outputs_return=None, ex_data=None):
        self.id = uniqid()
        get_inputs_return = get_inputs_return or FancyDict()
        get_outputs_return = get_outputs_return or FancyDict()
        self.update_outputs = mock.MagicMock()
        self.get_outputs = mock.MagicMock(return_value=get_outputs_return)
        self.set_outputs = mock.MagicMock()
        self.get_inputs = mock.MagicMock(return_value=get_inputs_return)
        self.inputs = get_inputs_return
        self.outputs = get_outputs_return
        self.ex_data = ex_data

        if isinstance(get_one_of_outputs_return, dict):

            def side_effect(arg):
                return get_one_of_outputs_return[arg]

            self.get_one_of_outputs = mock.MagicMock(side_effect=side_effect)
        else:
            self.get_one_of_outputs = mock.MagicMock(return_value=get_one_of_outputs_return)


class MockContext(object):
    def __init__(self, **kwargs):
        self.extract_output = mock.MagicMock()
        self.set_global_var = mock.MagicMock()
        self.update_global_var = mock.MagicMock()
        self.write_output = mock.MagicMock()
        self.clear = mock.MagicMock()
        self.recover_variable = mock.MagicMock()
        self.variables = kwargs.get("variables", "variables")


class MockStatus(IdentifyObject):
    def __init__(self, loop=0, id=None, state=None, started_time=None, archived_time=None, retry=False, skip=False):
        super(MockStatus, self).__init__(id=id)
        self.version = uniqid()
        self.loop = loop
        self.state = state
        self.started_time = started_time
        self.archived_time = archived_time
        self.retry = retry
        self.skip = skip

        self.save = MagicMock()


class MockSubprocessActivity(IdentifyObject):
    def __init__(self, **kwargs):
        self.pipeline = kwargs.get(
            "pipeline", PipelineObject(data=kwargs.get("pipeline_data"), context=kwargs.get("pipeline_context"))
        )
        self.next = mock.MagicMock(return_value=kwargs.get("next", uniqid()))
        self.data = kwargs.get("data", MockData())
        self.prepare_rerun_data = mock.MagicMock()
        super(MockSubprocessActivity, self).__init__(kwargs.get("id"))


class MockSequenceCollection(object):
    def __init__(self, **kwargs):
        self.all_target_node = mock.MagicMock(
            return_value=[IdentifyObject() for _ in range(kwargs.get("target_num", 3))]
        )


class MockParallelGateway(object):
    def __init__(self, **kwargs):
        self.outgoing = kwargs.get("outgoing", MockSequenceCollection())
        self.converge_gateway_id = kwargs.get("converge_gateway_id", uniqid())


class MockExclusiveGateway(object):
    def __init__(self, **kwargs):
        side_effect = kwargs.get("next_exception")
        if side_effect:
            self.next = mock.MagicMock(side_effect=side_effect)
        else:
            self.next = mock.MagicMock(return_value=kwargs.get("node", IdentifyObject()))


class MockConvergeGateway(object):
    def __init__(self, **kwargs):
        self.next = mock.MagicMock(return_value=kwargs.get("next", IdentifyObject()))


class MockParser(object):
    def __init__(self, parse_return="pipeline"):
        self.parse_return = parse_return

    def parse(self):
        return self.parse_return

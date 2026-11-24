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
from unittest import TestCase, mock

import requests
import ujson as json
from bamboo_engine import states as bamboo_engine_states

from gcloud.taskflow3.domains import answer_stream
from gcloud.taskflow3.domains.answer_stream import (
    AnswerStreamUnavailable,
    answer_events,
    locate_upstream,
    proxy_answer_stream,
)
from plugin_service.exceptions import PluginServiceException

MODULE = "gcloud.taskflow3.domains.answer_stream"


def _task(engine_ver=2, component_code="remote_plugin", node_type="ServiceActivity", in_subprocess=False):
    node = {"type": node_type, "component": {"code": component_code}}
    pipeline = {"activities": {"n1": node}}
    if in_subprocess:
        pipeline = {"activities": {"sub": {"pipeline": pipeline}}}
    return SimpleNamespace(
        id=1,
        engine_ver=engine_ver,
        has_node=lambda node_id: node_id == "n1",
        pipeline_instance=SimpleNamespace(execution_data=pipeline),
    )


def _result(data, result=True):
    return SimpleNamespace(result=result, data=data)


class LocateUpstreamTestCase(TestCase):
    def setUp(self):
        self.state = {"n1": {"state": bamboo_engine_states.RUNNING, "loop": 1}}
        self.data = {"inputs": {"plugin_code": "ai-test-output"}, "outputs": {"trace_id": "a" * 32}}
        patches = [
            mock.patch(f"{MODULE}.BambooDjangoRuntime"),
            mock.patch(f"{MODULE}.bamboo_engine_api.get_children_states", side_effect=lambda **kw: _result(self.state)),
            mock.patch(f"{MODULE}.bamboo_engine_api.get_execution_data", side_effect=lambda **kw: _result(self.data)),
            mock.patch(
                f"{MODULE}.PluginServiceApiClient",
                return_value=SimpleNamespace(plugin_host="http://plugin.example.com/bk_plugin/"),
            ),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def assert_unavailable(self, reason, task=None, **kwargs):
        with self.assertRaises(AnswerStreamUnavailable) as ctx:
            locate_upstream(task or _task(), "n1", **kwargs)
        self.assertEqual(ctx.exception.reason, reason)

    def test_locate_running_remote_plugin(self):
        url = locate_upstream(_task(), "n1")
        self.assertEqual(url, "http://plugin.example.com/bk_plugin/plugin_api/answer_stream/" + "a" * 32 + "/")

    def test_locate_node_in_subprocess(self):
        url = locate_upstream(_task(in_subprocess=True), "n1", subprocess_stack=["sub"])
        self.assertTrue(url.endswith("/answer_stream/" + "a" * 32 + "/"))

    def test_engine_v1_not_supported(self):
        self.assert_unavailable("engine_not_supported", _task(engine_ver=1))

    def test_node_not_in_task(self):
        with self.assertRaises(AnswerStreamUnavailable) as ctx:
            locate_upstream(_task(), "other")
        self.assertEqual(ctx.exception.reason, "node_not_found")

    def test_wrong_subprocess_stack(self):
        self.assert_unavailable("node_not_found", subprocess_stack=["missing"])

    def test_not_remote_plugin(self):
        self.assert_unavailable("not_remote_plugin", _task(component_code="job_execute_task"))
        self.assert_unavailable("not_remote_plugin", _task(node_type="SubProcess"))

    def test_not_running(self):
        for state in (bamboo_engine_states.READY, bamboo_engine_states.SUSPENDED):
            self.state = {"n1": {"state": state, "loop": 1}}
            self.assert_unavailable("not_running")
        self.state = {}
        self.assert_unavailable("not_running")

    def test_finished_node_located_for_history(self):
        for state in (bamboo_engine_states.FINISHED, bamboo_engine_states.FAILED):
            self.state = {"n1": {"state": state, "loop": 1}}
            self.assertTrue(locate_upstream(_task(), "n1").endswith("/plugin_api/answer_stream/" + "a" * 32 + "/"))

    def test_finished_node_without_trace_id_does_not_wait(self):
        self.state = {"n1": {"state": bamboo_engine_states.FAILED, "loop": 1}}
        self.data = {"inputs": {"plugin_code": "ai-test-output"}, "outputs": {}}
        self.assert_unavailable("no_trace_id")

    def test_history_loop_rejected(self):
        self.state = {"n1": {"state": bamboo_engine_states.RUNNING, "loop": 3}}
        self.assert_unavailable("not_current_loop", loop="2")
        self.assertTrue(locate_upstream(_task(), "n1", loop="3"))

    def test_trace_id_not_ready(self):
        self.data = {"inputs": {"plugin_code": "ai-test-output"}, "outputs": {}}
        self.assert_unavailable("not_ready")

    def test_invalid_trace_id(self):
        self.data["outputs"]["trace_id"] = "../../admin"
        self.assert_unavailable("invalid_trace_id")

    def test_plugin_client_error(self):
        with mock.patch(f"{MODULE}.PluginServiceApiClient", side_effect=PluginServiceException("x")):
            self.assert_unavailable("plugin_service_error")


class FakeResponse:
    def __init__(self, status_code=200, chunks=(), body=None, broken=False):
        self.status_code = status_code
        self.chunks = chunks
        self.body = body
        self.broken = broken
        self.closed = False

    def json(self):
        if self.body is None:
            raise ValueError
        return self.body

    def iter_content(self, chunk_size=None):
        for chunk in self.chunks:
            yield chunk
        if self.broken:
            raise requests.ConnectionError("broken")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True


def _events(chunks):
    text = b"".join(chunks).decode("utf-8")
    events = []
    for block in text.strip().split("\n\n"):
        lines = block.split("\n")
        events.append((lines[0][len("event: ") :], json.loads(lines[1][len("data: ") :])))
    return events


class ProxyAnswerStreamTestCase(TestCase):
    URL = "http://plugin.example.com/bk_plugin/plugin_api/answer_stream/t/"

    def test_pass_through_bytes(self):
        chunks = [b'event: ready\ndata: {"output_key": "output"}\n\n', b": ping\n\n", b"event: end\ndata: {}\n\n"]
        response = FakeResponse(chunks=chunks)
        with mock.patch(f"{MODULE}.requests.get", return_value=response) as get:
            self.assertEqual(list(proxy_answer_stream(self.URL)), chunks)
        self.assertTrue(get.call_args.kwargs["stream"])
        self.assertTrue(response.closed)

    def test_upstream_unsupported_status(self):
        response = FakeResponse(status_code=409, body={"result": False, "reason": "execution finished"})
        with mock.patch(f"{MODULE}.requests.get", return_value=response):
            self.assertEqual(
                _events(proxy_answer_stream(self.URL)), [("unsupported", {"reason": "execution finished"})]
            )

    def test_upstream_404_without_json(self):
        with mock.patch(f"{MODULE}.requests.get", return_value=FakeResponse(status_code=404)):
            self.assertEqual(_events(proxy_answer_stream(self.URL)), [("unsupported", {"reason": "upstream_404"})])

    def test_upstream_unreachable(self):
        with mock.patch(f"{MODULE}.requests.get", side_effect=requests.ConnectTimeout("x")):
            self.assertEqual(
                _events(proxy_answer_stream(self.URL)), [("unsupported", {"reason": "upstream_unreachable"})]
            )

    def test_upstream_broken_midway(self):
        response = FakeResponse(chunks=[b"event: ready\ndata: {}\n\n"], broken=True)
        with mock.patch(f"{MODULE}.requests.get", return_value=response):
            events = _events(proxy_answer_stream(self.URL))
        self.assertEqual(events[-1], ("end", {"reason": "upstream_error"}))

    def test_client_disconnect_closes_upstream(self):
        response = FakeResponse(chunks=[b"a", b"b", b"c"])
        with mock.patch(f"{MODULE}.requests.get", return_value=response):
            stream = proxy_answer_stream(self.URL)
            next(stream)
            stream.close()
        self.assertTrue(response.closed)

    def test_max_duration(self):
        clock = iter([0, 10, answer_stream.MAX_DURATION + 1])
        response = FakeResponse(chunks=[b"a", b"b", b"c"])
        with mock.patch(f"{MODULE}.requests.get", return_value=response):
            chunks = list(proxy_answer_stream(self.URL, clock=lambda: next(clock)))
        self.assertEqual(chunks[:2], [b"a", b"b"])
        self.assertEqual(_events(chunks[2:]), [("end", {"reason": "timeout"})])


class AnswerEventsTestCase(TestCase):
    def run_events(self, outcomes):
        """outcomes: locate_upstream 依次的结果，异常原因字符串或 URL。"""
        calls = iter(outcomes)
        now = [0.0]

        def locate(*args, **kwargs):
            outcome = next(calls)
            if outcome.startswith("http"):
                return outcome
            raise AnswerStreamUnavailable(outcome)

        def sleep(seconds):
            now[0] += seconds

        with mock.patch(f"{MODULE}.locate_upstream", side_effect=locate), mock.patch(
            f"{MODULE}.proxy_answer_stream", side_effect=lambda url, clock: iter([b"proxied " + url.encode()])
        ):
            return list(answer_events(_task(), "n1", clock=lambda: now[0], sleep=sleep))

    def test_wait_until_trace_id_ready(self):
        chunks = self.run_events(["not_ready", "not_ready", "http://plugin/x/"])
        self.assertEqual(chunks, [b": waiting\n\n", b": waiting\n\n", b"proxied http://plugin/x/"])

    def test_ready_wait_budget(self):
        chunks = self.run_events(["not_ready"] * 100)
        self.assertEqual(len(chunks), answer_stream.READY_WAIT + 1)
        self.assertEqual(_events(chunks[-1:]), [("unsupported", {"reason": "not_ready"})])

    def test_other_reasons_do_not_wait(self):
        self.assertEqual(_events(self.run_events(["not_running"])), [("unsupported", {"reason": "not_running"})])


class AnswerStreamResponseTestCase(TestCase):
    def body(self, response):
        return _events(list(response.streaming_content))

    @mock.patch.object(answer_stream.plugin_service_env, "ENABLE_NODE_ANSWER_STREAM", False)
    def test_disabled(self):
        response = answer_stream.answer_stream_response(1, {"instance_id": "1", "node_id": "n1"})
        self.assertEqual(response["Content-Type"], "text/event-stream; charset=utf-8")
        self.assertEqual(response["X-Accel-Buffering"], "no")
        self.assertEqual(self.body(response), [("unsupported", {"reason": "disabled"})])

    @mock.patch.object(answer_stream.plugin_service_env, "ENABLE_NODE_ANSWER_STREAM", True)
    def test_enabled_forwards_node_events(self):
        task = object()
        with mock.patch.object(
            answer_stream.TaskFlowInstance.objects, "get", return_value=task
        ) as get_task, mock.patch.object(
            answer_stream, "answer_events", return_value=iter([answer_stream.sse("end", {"reason": "history"})])
        ) as events:
            query = {"instance_id": "7", "node_id": "n1", "loop": "2", "subprocess_stack": '["s1"]'}
            response = answer_stream.answer_stream_response(3, query)
            self.assertEqual(self.body(response), [("end", {"reason": "history"})])
        get_task.assert_called_once_with(pk="7", project_id=3)
        events.assert_called_once_with(task, "n1", ["s1"], "2")

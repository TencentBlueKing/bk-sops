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

import json
from mock import patch, MagicMock

from django.test import TestCase

from pipeline.engine.exceptions import CeleryFailedTaskCatchException
from pipeline.engine.models import SendFailedCeleryTask


class SendFailedCeleryTaskTestCase(TestCase):
    def tearDown(self):
        SendFailedCeleryTask.objects.all().delete()

    def test_kwargs_dict(self):
        kwargs = {"task_kwargs": "token"}
        task = SendFailedCeleryTask.objects.create(
            name="name",
            kwargs=json.dumps(kwargs),
            type=SendFailedCeleryTask.TASK_TYPE_EMPTY,
            extra_kwargs="extra_kwargs_token",
            exec_trace="trace_token",
        )

        self.assertEqual(task.kwargs_dict, kwargs)

    def test_extra_kwargs_dict(self):
        extra_kwargs = {"extra_kwargs": "token"}
        task = SendFailedCeleryTask.objects.create(
            name="name",
            kwargs="kwargs_token",
            type=SendFailedCeleryTask.TASK_TYPE_EMPTY,
            extra_kwargs=json.dumps(extra_kwargs),
            exec_trace="trace_token",
        )

        self.assertEqual(task.extra_kwargs_dict, extra_kwargs)

    def test_resend__type_error(self):
        task = SendFailedCeleryTask(
            name="name", kwargs="kwargs_token", type=-1, extra_kwargs="extra_kwargs_token", exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        mock_task.apply_async = MagicMock(side_effect=Exception)
        current_app = MagicMock()
        current_app.tasks = MagicMock()

        with patch("pipeline.engine.models.core.current_app", current_app):
            self.assertRaises(TypeError, task.resend)

        task.delete.assert_not_called()

    def test_resend__empty_send_error(self):
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_EMPTY,
            extra_kwargs="extra_kwargs_token",
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        mock_task.apply_async = MagicMock(side_effect=RuntimeError)
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}

        with patch("pipeline.engine.models.core.current_app", current_app):
            self.assertRaises(RuntimeError, task.resend)

        task.delete.assert_not_called()

    def test_resend__process_send_error(self):
        process_id = "pid"
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_PROCESS,
            extra_kwargs=json.dumps({"process_id": process_id}),
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}
        mock_start_task = MagicMock(side_effect=RuntimeError)

        with patch("pipeline.engine.models.core.current_app", current_app):
            with patch(
                "pipeline.engine.models.core.ProcessCeleryTask.objects.start_task", mock_start_task,
            ):
                self.assertRaises(RuntimeError, task.resend)

        mock_start_task.assert_called_once_with(
            process_id=process_id, task=mock_task, kwargs=task.kwargs_dict, record_error=False,
        )
        task.delete.assert_not_called()

    def test_resend__node_send_error(self):
        node_id = "nid"
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_NODE,
            extra_kwargs=json.dumps({"node_id": node_id}),
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}
        mock_start_task = MagicMock(side_effect=RuntimeError)

        with patch("pipeline.engine.models.core.current_app", current_app):
            with patch(
                "pipeline.engine.models.core.NodeCeleryTask.objects.start_task", mock_start_task,
            ):
                self.assertRaises(RuntimeError, task.resend)

        mock_start_task.assert_called_once_with(
            node_id=node_id, task=mock_task, kwargs=task.kwargs_dict, record_error=False
        )
        task.delete.assert_not_called()

    def test_resend__schedule_send_error(self):
        schedule_id = "sid"
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_SCHEDULE,
            extra_kwargs=json.dumps({"schedule_id": schedule_id}),
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}
        mock_start_task = MagicMock(side_effect=RuntimeError)

        with patch("pipeline.engine.models.core.current_app", current_app):
            with patch(
                "pipeline.engine.models.core.ScheduleCeleryTask.objects.start_task", mock_start_task,
            ):
                self.assertRaises(RuntimeError, task.resend)

        mock_start_task.assert_called_once_with(
            schedule_id=schedule_id, task=mock_task, kwargs=task.kwargs_dict, record_error=False,
        )
        task.delete.assert_not_called()

    def test_resend__empty_send_success(self):
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_EMPTY,
            extra_kwargs="extra_kwargs_token",
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        mock_task.apply_async = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}

        with patch("pipeline.engine.models.core.current_app", current_app):
            task.resend()

        mock_task.apply_async.assert_called_once_with(**task.kwargs_dict)
        task.delete.assert_called_once()

    def test_resend__process_send_success(self):
        process_id = "pid"
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_PROCESS,
            extra_kwargs=json.dumps({"process_id": process_id}),
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}
        mock_start_task = MagicMock()

        with patch("pipeline.engine.models.core.current_app", current_app):
            with patch(
                "pipeline.engine.models.core.ProcessCeleryTask.objects.start_task", mock_start_task,
            ):
                task.resend()

        mock_start_task.assert_called_once_with(
            process_id=process_id, task=mock_task, kwargs=task.kwargs_dict, record_error=False,
        )
        task.delete.assert_called_once()

    def test_resend__node_send_success(self):
        node_id = "nid"
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_NODE,
            extra_kwargs=json.dumps({"node_id": node_id}),
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}
        mock_start_task = MagicMock()

        with patch("pipeline.engine.models.core.current_app", current_app):
            with patch(
                "pipeline.engine.models.core.NodeCeleryTask.objects.start_task", mock_start_task,
            ):
                task.resend()

        mock_start_task.assert_called_once_with(
            node_id=node_id, task=mock_task, kwargs=task.kwargs_dict, record_error=False
        )
        task.delete.assert_called_once()

    def test_resend__schedule_send_success(self):
        schedule_id = "sid"
        task = SendFailedCeleryTask(
            name="name",
            kwargs=json.dumps({"task_kargs": "token"}),
            type=SendFailedCeleryTask.TASK_TYPE_SCHEDULE,
            extra_kwargs=json.dumps({"schedule_id": schedule_id}),
            exec_trace="trace_token",
        )
        task.delete = MagicMock()

        mock_task = MagicMock()
        current_app = MagicMock()
        current_app.tasks = {"name": mock_task}
        mock_start_task = MagicMock()

        with patch("pipeline.engine.models.core.current_app", current_app):
            with patch(
                "pipeline.engine.models.core.ScheduleCeleryTask.objects.start_task", mock_start_task,
            ):
                task.resend()

        mock_start_task.assert_called_once_with(
            schedule_id=schedule_id, task=mock_task, kwargs=task.kwargs_dict, record_error=False,
        )
        task.delete.assert_called_once()

    def test_watch__no_exception(self):
        with SendFailedCeleryTask.watch(1, 2, 3, 4):
            pass

        self.assertFalse(SendFailedCeleryTask.objects.all().exists())

    def test_watch__catch_execption(self):
        name = "name_token"
        kwargs = "kwargs_token"
        type = SendFailedCeleryTask.TASK_TYPE_EMPTY
        extra_kwargs = "extra_kwargs_token"
        try:
            with SendFailedCeleryTask.watch(name, kwargs, type, extra_kwargs):
                raise RuntimeError()
        except CeleryFailedTaskCatchException as e:
            self.assertEqual(e.task_name, name)

        task = SendFailedCeleryTask.objects.all()[0]
        self.assertEqual(task.name, name)
        self.assertEqual(task.kwargs, kwargs)
        self.assertEqual(task.type, type)
        self.assertEqual(task.extra_kwargs, extra_kwargs)
        self.assertNotEqual(len(task.exec_trace), 0)

    def test_record__with_dict_kwargs(self):
        name = "name_token"
        kwargs = {"1": "1"}
        type = SendFailedCeleryTask.TASK_TYPE_EMPTY
        extra_kwargs = {"2": "2"}
        exec_trace = "exec_trace_token"

        task = SendFailedCeleryTask.objects.record(name, kwargs, type, extra_kwargs, exec_trace)
        self.assertEqual(task.name, name)
        self.assertEqual(task.kwargs_dict, kwargs)
        self.assertEqual(task.type, type)
        self.assertEqual(task.extra_kwargs_dict, extra_kwargs)
        self.assertEqual(task.exec_trace, exec_trace)

    def test_record__with_str_kwargs(self):
        name = "name_token"
        kwargs = {"1": "1"}
        type = SendFailedCeleryTask.TASK_TYPE_EMPTY
        extra_kwargs = {"2": "2"}
        exec_trace = "exec_trace_token"

        task = SendFailedCeleryTask.objects.record(name, json.dumps(kwargs), type, json.dumps(extra_kwargs), exec_trace)
        self.assertEqual(task.name, name)
        self.assertEqual(task.kwargs_dict, kwargs)
        self.assertEqual(task.type, type)
        self.assertEqual(task.extra_kwargs_dict, extra_kwargs)
        self.assertEqual(task.exec_trace, exec_trace)

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

from pipeline.engine.models import ProcessCeleryTask, SendFailedCeleryTask

from ..mock import *  # noqa


class TestProcessCeleryTask(TestCase):
    def tearDown(self):
        ProcessCeleryTask.objects.all().delete()

    def test_bind(self):
        process_id = uniqid()
        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]

        ProcessCeleryTask.objects.bind(process_id=process_id, celery_task_id=celery_task_id)
        task = ProcessCeleryTask.objects.get(process_id=process_id, celery_task_id=celery_task_id)
        self.assertEqual(task.process_id, process_id)
        self.assertEqual(task.celery_task_id, celery_task_id)

        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]
        ProcessCeleryTask.objects.bind(process_id=process_id, celery_task_id=celery_task_id)
        task.refresh_from_db()
        self.assertEqual(task.process_id, process_id)
        self.assertEqual(task.celery_task_id, celery_task_id)

    def test_unbind(self):
        process_id = uniqid()
        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]

        ProcessCeleryTask.objects.bind(process_id=process_id, celery_task_id=celery_task_id)
        task = ProcessCeleryTask.objects.get(process_id=process_id, celery_task_id=celery_task_id)
        ProcessCeleryTask.objects.unbind(process_id)
        task.refresh_from_db()
        self.assertEqual(task.celery_task_id, "")

    def test_destroy(self):
        process_id = uniqid()
        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]

        ProcessCeleryTask.objects.bind(process_id=process_id, celery_task_id=celery_task_id)
        ProcessCeleryTask.objects.destroy(process_id)
        self.assertRaises(
            ProcessCeleryTask.DoesNotExist, ProcessCeleryTask.objects.get, process_id=process_id,
        )

    def test_start_task__record_error(self):
        task = MagicMock()
        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]
        task.apply_async = MagicMock(return_value=celery_task_id)
        task.name = "name_token"
        process_id = uniqid()
        kwargs = {"a": "1", "b": 2}
        mock_watch = MagicMock()

        with patch("pipeline.engine.models.core.SendFailedCeleryTask.watch", mock_watch):
            ProcessCeleryTask.objects.start_task(process_id, task=task, kwargs=kwargs)

        mock_watch.assert_called_once_with(
            name=task.name,
            kwargs=kwargs,
            type=SendFailedCeleryTask.TASK_TYPE_PROCESS,
            extra_kwargs={"process_id": process_id},
        )
        task.apply_async.assert_called_with(a="1", b=2)
        self.assertEqual(
            ProcessCeleryTask.objects.filter(
                process_id=process_id, celery_task_id=task.apply_async.return_value
            ).count(),
            1,
        )

    def test_start_task__no_record_error(self):
        task = MagicMock()
        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]
        task.apply_async = MagicMock(return_value=celery_task_id)
        task.name = "name_token"
        process_id = uniqid()
        kwargs = {"a": "1", "b": 2}
        mock_watch = MagicMock()

        with patch("pipeline.engine.models.core.SendFailedCeleryTask.watch", mock_watch):
            ProcessCeleryTask.objects.start_task(process_id, task=task, kwargs=kwargs, record_error=False)

        mock_watch.assert_not_called()
        task.apply_async.assert_called_with(a="1", b=2)
        self.assertEqual(
            ProcessCeleryTask.objects.filter(
                process_id=process_id, celery_task_id=task.apply_async.return_value
            ).count(),
            1,
        )

    @patch("pipeline.engine.models.core.revoke", MagicMock())
    def test_revoke(self):
        from pipeline.engine.models.core import revoke

        process_id = uniqid()
        celery_task_id = "{}{}".format(uniqid(), uniqid())[:40]

        ProcessCeleryTask.objects.bind(process_id=process_id, celery_task_id=celery_task_id)
        ProcessCeleryTask.objects.revoke(process_id)
        revoke.assert_called_with(celery_task_id, terminate=True)
        self.assertRaises(
            ProcessCeleryTask.DoesNotExist,
            ProcessCeleryTask.objects.get,
            process_id=process_id,
            celery_task_id=celery_task_id,
        )

        revoke.reset_mock()

        ProcessCeleryTask.objects.bind(process_id=process_id, celery_task_id=celery_task_id)
        ProcessCeleryTask.objects.revoke(process_id, kill=True)
        revoke.assert_called_with(celery_task_id, terminate=True, signal="SIGKILL")
        self.assertRaises(
            ProcessCeleryTask.DoesNotExist,
            ProcessCeleryTask.objects.get,
            process_id=process_id,
            celery_task_id=celery_task_id,
        )

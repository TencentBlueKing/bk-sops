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

import uuid
import threading

from django.test import TransactionTestCase

from pipeline.eri.models import Process
from pipeline.eri.imp.process import ProcessMixin


class ProcessMixinTestCase(TransactionTestCase):
    def setUp(self):
        self.mixin = ProcessMixin()
        self.process = Process.objects.create(priority=1, queue="queue")

    def test_beat(self):
        last_heartbeat = self.process.last_heartbeat
        self.mixin.beat(self.process.id)
        self.process.refresh_from_db()
        self.assertTrue(last_heartbeat < self.process.last_heartbeat)

    def test_wake_up(self):
        self.assertTrue(self.process.asleep)
        self.mixin.wake_up(self.process.id)
        self.process.refresh_from_db()
        self.assertFalse(self.process.asleep)

    def test_sleep(self):
        self.process.asleep = False
        self.process.save()
        self.mixin.sleep(self.process.id)
        self.process.refresh_from_db()
        self.assertTrue(self.process.asleep)

    def test_suspend(self):
        self.assertFalse(self.process.suspended)
        self.assertEqual(self.process.suspended_by, "")
        self.mixin.suspend(self.process.id, "123")
        self.process.refresh_from_db()
        self.assertTrue(self.process.suspended)
        self.assertEqual(self.process.suspended_by, "123")

    def test_kill(self):
        self.process.asleep = False
        self.process.save()
        self.mixin.kill(self.process.id)
        self.process.refresh_from_db()
        self.assertTrue(self.process.asleep)

    def test_resume(self):
        self.mixin.suspend(self.process.id, "123")
        self.mixin.resume(self.process.id)
        self.process.refresh_from_db()
        self.assertFalse(self.process.suspended)
        self.assertEqual(self.process.suspended_by, "")

    def test_batch_resume(self):
        p1 = Process.objects.create(priority=1, queue="queue")
        p2 = Process.objects.create(priority=1, queue="queue")
        p3 = Process.objects.create(priority=1, queue="queue")
        self.mixin.suspend(p1.id, "123")
        self.mixin.suspend(p2.id, "123")
        self.mixin.suspend(p3.id, "123")
        self.mixin.batch_resume([p1.id, p2.id, p3.id])
        p1.refresh_from_db()
        p2.refresh_from_db()
        p3.refresh_from_db()
        self.assertFalse(p1.suspended)
        self.assertFalse(p2.suspended)
        self.assertFalse(p3.suspended)
        self.assertEqual(p1.suspended_by, "")
        self.assertEqual(p2.suspended_by, "")
        self.assertEqual(p3.suspended_by, "")

    def test_die(self):
        self.assertFalse(self.process.dead)
        self.mixin.die(self.process.id)
        self.process.refresh_from_db()
        self.assertTrue(self.process.dead)

    def test_get_process_info(self):
        process = Process.objects.create(
            priority=1, queue="queue", destination_id="d", root_pipeline_id="r", pipeline_stack="[]", parent_id=2
        )
        process_info = self.mixin.get_process_info(process.id)
        self.assertEqual(process_info.process_id, process.id)
        self.assertEqual(process_info.destination_id, process.destination_id)
        self.assertEqual(process_info.root_pipeline_id, process.root_pipeline_id)
        self.assertEqual(process_info.pipeline_stack, [])
        self.assertEqual(process_info.parent_id, process.parent_id)

    def test_get_suspended_process_info(self):
        p1 = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        p2 = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        p3 = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        self.mixin.suspend(p1.id, "123")
        self.mixin.suspend(p2.id, "123")
        self.mixin.suspend(p3.id, "123")
        spi_list = self.mixin.get_suspended_process_info("123")
        actual = [(spi.process_id, spi.current_node) for spi in spi_list]
        self.assertEqual(
            actual, [(p1.id, p1.current_node_id), (p2.id, p2.current_node_id), (p3.id, p3.current_node_id)]
        )

    def test_get_sleep_process_with_current_node_id(self):
        process = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        self.mixin.sleep(process.id)
        self.assertEqual(self.mixin.get_sleep_process_with_current_node_id(process.current_node_id), process.id)

    def test_get_sleep_process_with_current_node_id__not_exist(self):
        self.assertIsNone(self.mixin.get_sleep_process_with_current_node_id("not_exist"))

    def test_get_sleep_process_with_current_node_id__more_than_one(self):
        p1 = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        p2 = Process.objects.create(priority=1, queue="queue", current_node_id=p1.current_node_id)
        self.mixin.sleep(p1.id)
        self.mixin.sleep(p2.id)
        self.assertRaises(ValueError, self.mixin.get_sleep_process_with_current_node_id, p1.current_node_id)

    def test_get_process_id_with_current_node_id(self):
        p1 = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex, dead=True)
        self.assertEqual(self.mixin.get_process_id_with_current_node_id(p1.current_node_id), p1.id)

    def test_get_process_id_with_current_node_id__not_exist(self):
        self.assertIsNone(self.mixin.get_process_id_with_current_node_id("not_exist"))

    def test_get_process_id_with_current_node_id_more_than_one(self):
        p1 = Process.objects.create(priority=1, queue="queue", current_node_id=uuid.uuid1().hex)
        p2 = Process.objects.create(priority=1, queue="queue", current_node_id=p1.current_node_id)
        self.mixin.sleep(p1.id)
        self.mixin.sleep(p2.id)
        self.assertRaises(ValueError, self.mixin.get_process_id_with_current_node_id, p1.current_node_id)

    def test_set_current_node(self):
        node_id = uuid.uuid1().hex
        self.mixin.set_current_node(self.process.id, node_id)
        self.process.refresh_from_db()
        self.assertEqual(self.process.current_node_id, node_id)

    def test_child_process_finish(self):
        need_ack = 30

        process = Process.objects.create(priority=1, queue="queue", ack_num=0, need_ack=need_ack)

        lock = threading.Lock()
        res = {False: 0, True: 0}

        def target(parent_id, process_id):
            success = self.mixin.child_process_finish(parent_id, process_id)
            lock.acquire()
            res[success] += 1
            lock.release()

        threads = [threading.Thread(target=target, args=(process.id, i)) for i in range(need_ack)]

        for t in threads:
            t.start()

        for t in threads:
            t.join(1)

        process.refresh_from_db()
        self.assertEqual(process.ack_num, 0)
        self.assertEqual(process.need_ack, -1)
        self.assertEqual(res, {True: 1, False: need_ack - 1})

    def test_is_frozen(self):
        self.assertFalse(self.mixin.is_frozen(self.process.id))
        self.process.frozen = True
        self.process.save()
        self.assertTrue(self.mixin.is_frozen(self.process.id))

    def test_freeze(self):
        self.assertFalse(self.process.frozen)
        self.mixin.freeze(self.process.id)
        self.process.refresh_from_db()
        self.assertTrue(self.process.frozen)

    def test_fork(self):
        from_to = {}
        for i in range(10):
            from_to[str(i)] = str(i + 1)

        dps = self.mixin.fork(parent_id=self.process.id, root_pipeline_id="r", pipeline_stack=[1, 2], from_to=from_to)
        self.assertEqual(len(dps), 10)
        actual = [dp.node_id for dp in dps]
        self.assertEqual(actual, [str(i) for i in range(10)])

    def test_fork__parent_does_not_exist(self):
        self.assertRaises(
            Process.DoesNotExist,
            self.mixin.fork,
            parent_id=self.process.id + 1,
            root_pipeline_id="r",
            pipeline_stack=[1, 2],
            from_to={},
        )

    def test_join(self):
        self.mixin.join(self.process.id, list(range(100)))
        self.process.refresh_from_db()
        self.assertEqual(self.process.ack_num, 0)
        self.assertEqual(self.process.need_ack, 100)

    def test_set_pipeline_stack(self):
        self.assertEqual(self.process.pipeline_stack, "[]")
        self.mixin.set_pipeline_stack(self.process.id, ["1", "2", "3"])
        self.process.refresh_from_db()
        self.assertEqual(self.process.pipeline_stack, '["1", "2", "3"]')

    def test_get_process_info_with_root_pipeline(self):
        self.process.root_pipeline_id = "root"
        self.process.save()
        p = self.mixin.get_process_info_with_root_pipeline("root")
        self.assertEqual(1, len(p))
        self.assertEqual(p[0].root_pipeline_id, "root")
        self.assertEqual(p[0].process_id, self.process.id)
        self.assertEqual(p[0].destination_id, self.process.destination_id)
        self.assertEqual(p[0].pipeline_stack, [])
        self.assertEqual(p[0].parent_id, self.process.parent_id)

        p = self.mixin.get_process_info_with_root_pipeline("not_exist")
        self.assertEqual(0, len(p))

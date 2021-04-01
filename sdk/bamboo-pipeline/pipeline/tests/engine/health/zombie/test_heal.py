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
from mock import MagicMock, patch

from pipeline.engine.health.zombie.doctors import ZombieProcDoctor
from pipeline.engine.health.zombie.heal import DummyZombieProcHealer, ZombieProcHealer, get_healer
from pipeline.tests.mock_settings import *  # noqa


class HealTestCase(TestCase):
    def test_get_healer__empty_dr_settings(self):
        settings = MagicMock()
        settings.ENGINE_ZOMBIE_PROCESS_DOCTORS = None
        with patch(ENGINE_HEALTH_ZOMBIE_HEAL_DEFAULT_SETTINGS, settings):
            healer = get_healer()

            self.assertIsInstance(healer, DummyZombieProcHealer)

    def test_get_healer__doctors_init_all_failed(self):
        settings = MagicMock()
        settings.ENGINE_ZOMBIE_PROCESS_DOCTORS = [{}, {}]
        with patch(ENGINE_HEALTH_ZOMBIE_HEAL_DEFAULT_SETTINGS, settings):
            healer = get_healer()

            self.assertIsInstance(healer, DummyZombieProcHealer)

    def test_get_healer(self):
        settings = MagicMock()
        settings.ENGINE_ZOMBIE_PROCESS_DOCTORS = [
            {
                "class": "pipeline.engine.health.zombie.doctors.RunningNodeZombieDoctor",
                "config": {"max_stuck_time": 30},
            },
            {
                "class": "pipeline.engine.health.zombie.doctors.RunningNodeZombieDoctor",
                "config": {"max_stuck_time": 15},
            },
            {"class": "not_exist_class", "config": {"whatever": "whatever"}},
        ]
        with patch(ENGINE_HEALTH_ZOMBIE_HEAL_DEFAULT_SETTINGS, settings):
            healer = get_healer()

            self.assertIsInstance(healer, ZombieProcHealer)
            self.assertEqual(len(healer.doctors), 2)
            self.assertIsInstance(healer.doctors[0], ZombieProcDoctor)
            self.assertIsInstance(healer.doctors[1], ZombieProcDoctor)
            self.assertEqual(healer.doctors[0].max_stuck_time, 30)
            self.assertEqual(healer.doctors[1].max_stuck_time, 15)


class ZombieProcHealerTestCase(TestCase):
    def test_heal__emptry_doctors(self):
        healer = ZombieProcHealer([])
        healer._get_process_ids = MagicMock(return_value=[1, 2, 3])
        healer.heal()

    def test_heal__process_state_not_fit(self):
        doctor_1 = MagicMock()
        healer = ZombieProcHealer([doctor_1])
        healer._get_process_ids = MagicMock(return_value=[1, 2, 3])

        proc_1 = MagicMock()
        proc_1.id = 1
        proc_1.is_alive = False
        proc_1.is_frozen = False

        proc_2 = MagicMock()
        proc_2.id = 2
        proc_2.is_alive = True
        proc_2.is_frozen = True

        proc_3 = MagicMock()
        proc_3.id = 3
        proc_3.is_alive = False
        proc_3.is_frozen = True

        processes = {1: proc_1, 2: proc_2, 3: proc_3}

        def get(id):
            return processes[id]

        with patch(PIPELINE_PROCESS_GET, get):
            self.assertFalse(not healer.doctors)
            healer.heal()
            doctor_1.confirm.assert_not_called()
            doctor_1.cure.assert_not_called()

    def test_heal(self):

        doctor_1 = MagicMock()
        doctor_1_confirm_count = {"count": 0}

        def doctor_1_confirm(proc, count=doctor_1_confirm_count):
            count["count"] += 1
            return proc.id == 1

        doctor_1.confirm = doctor_1_confirm

        doctor_2 = MagicMock()
        doctor_2_confirm_count = {"count": 0}

        def doctor_2_confirm(proc, count=doctor_2_confirm_count):
            count["count"] += 1
            return proc.id == 2

        doctor_2.confirm = doctor_2_confirm

        doctor_3 = MagicMock()
        doctor_3_confirm_count = {"count": 0}

        def doctor_3_confirm(proc, count=doctor_3_confirm_count):
            count["count"] += 1
            return proc.id == 3

        doctor_3.confirm = doctor_3_confirm

        healer = ZombieProcHealer([doctor_1, doctor_2, doctor_3])
        healer._get_process_ids = MagicMock(return_value=[1, 2, 3])

        proc_1 = MagicMock()
        proc_1.id = 1
        proc_1.is_alive = True
        proc_1.is_frozen = False

        proc_2 = MagicMock()
        proc_2.id = 2
        proc_2.is_alive = True
        proc_2.is_frozen = False

        proc_3 = MagicMock()
        proc_3.id = 3
        proc_3.is_alive = True
        proc_3.is_frozen = False

        processes = {1: proc_1, 2: proc_2, 3: proc_3}

        def get(id):
            return processes[id]

        with patch(PIPELINE_PROCESS_GET, get):
            healer.heal()

            self.assertEqual(doctor_1_confirm_count["count"], 3)
            self.assertEqual(doctor_2_confirm_count["count"], 2)
            self.assertEqual(doctor_3_confirm_count["count"], 1)

            doctor_1.cure.assert_called_once_with(proc_1)
            doctor_2.cure.assert_called_once_with(proc_2)
            doctor_3.cure.assert_called_once_with(proc_3)

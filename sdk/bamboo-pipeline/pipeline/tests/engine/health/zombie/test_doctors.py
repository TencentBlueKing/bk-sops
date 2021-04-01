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

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from pipeline.core.pipeline import Pipeline
from pipeline.engine import signals
from pipeline.engine.health.zombie.doctors import RunningNodeZombieDoctor
from pipeline.engine.models import Status
from pipeline.tests.engine.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa


class RunningNodeZombieDoctorTestCase(TestCase):
    def test_confirm__proc_current_node_id_is_none(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        proc.current_node_id = None
        self.assertFalse(doctor.confirm(proc))

    @patch(PIPELINE_STATUS_GET, MagicMock(side_effect=Status.DoesNotExist))
    def test_confirm__status_not_exist(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))

    def test_confirm__status_refresh_at_is_none(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state_refresh_at = None
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            self.assertFalse(doctor.confirm(proc))

    def test_confirm__status_is_not_running(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state = "FINISHED"
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            self.assertFalse(doctor.confirm(proc))

    def test_confirm__not_detect_schedule_wait_callback(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state = "RUNNING"
        schedule = MagicMock()
        schedule.wait_callback = True
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=schedule)):
                self.assertFalse(doctor.confirm(proc))

    def test_confirm__detect_schedule_wait_callback(self):
        doctor = RunningNodeZombieDoctor(1, True)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state = "RUNNING"
        schedule = MagicMock()
        schedule.wait_callback = True
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=schedule)):
                self.assertFalse(doctor.confirm(proc))

    def test_confirm__detect_schedule_wait_callback_overtime(self):
        doctor = RunningNodeZombieDoctor(1, True)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state = "RUNNING"
        status.state_refresh_at = timezone.now() - timedelta(seconds=2)
        schedule = MagicMock()
        schedule.wait_callback = True
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=schedule)):
                self.assertTrue(doctor.confirm(proc))

    def test_confirm__stuck_time_less_than_max_stuck_time(self):
        doctor = RunningNodeZombieDoctor(100)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state_refresh_at = timezone.now() - timedelta(seconds=2)
        schedule = MagicMock()
        schedule.wait_callback = False
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=schedule)):
                self.assertFalse(doctor.confirm(proc))

    def test_confirm(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        self.assertFalse(doctor.confirm(proc))
        status = MagicMock()
        status.state_refresh_at = timezone.now() - timedelta(seconds=2)
        schedule = MagicMock()
        schedule.wait_callback = False
        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=schedule)):
                self.assertFalse(doctor.confirm(proc))

    @patch(PIPELINE_STATUS_RAW_FAIL, MagicMock(side_effect=Exception))
    def test_cure__raw_fail_raise(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        doctor.cure(proc)

    def test_cure__raw_fail_failed(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        result = MagicMock()
        result.result = False

        with patch(PIPELINE_STATUS_RAW_FAIL, MagicMock(return_value=result)):
            doctor.cure(proc)

    @mock.patch(ENGINE_ACTIVITY_FAIL_SIGNAL, mock.MagicMock())
    def test_cure(self):
        doctor = RunningNodeZombieDoctor(1)
        proc = MagicMock()
        proc.id = "proc"
        proc.is_sleep = False
        proc.root_pipeline_id = uniqid()
        proc.current_node_id = uniqid()
        status = MagicMock()
        status.version = None
        revoke = MagicMock()
        result = MagicMock()
        result.result = True
        result.extra = status

        with patch(PIPELINE_STATUS_RAW_FAIL, MagicMock(return_value=result)):
            with patch(PIPELINE_CELERYTASK_REVOKE, revoke):
                doctor.cure(proc)

                self.assertIsNotNone(status.version)
                status.save.assert_called_once()
                revoke.assert_called_once_with(proc.id, kill=True)
                proc.adjust_status.assert_called_once()
                self.assertTrue(proc.is_sleep)
                proc.save.assert_called_once()
                signals.activity_failed.send.assert_called_with(
                    sender=Pipeline, pipeline_id=proc.root_pipeline_id, pipeline_activity_id=proc.current_node_id
                )

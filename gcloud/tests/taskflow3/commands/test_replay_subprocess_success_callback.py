# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from bamboo_engine import states as bamboo_states
from django.test import SimpleTestCase

from gcloud.taskflow3.management.commands.replay_subprocess_success_callback import Command


class ReplaySubprocessSuccessCallbackCommandTestCase(SimpleTestCase):
    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.CallbackData")
    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.BambooDjangoRuntime")
    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.TaskFlowInstance")
    def test_inspect_candidate_allows_failed_subprocess_node_with_latest_success_callback(
        self, taskflow_cls, runtime_cls, callback_data_cls
    ):
        task = MagicMock()
        task.id = 129568046
        task.engine_ver = 2
        task.pipeline_instance.instance_id = "nbbf48c8619e3e858a338072abeb11f3"
        taskflow_cls.objects.filter.return_value.select_related.return_value.first.return_value = task

        runtime = runtime_cls.return_value
        state = MagicMock()
        state.name = bamboo_states.FAILED
        state.version = "v668546486bc04d1fa1733a596c49e9b2"
        runtime.get_state.return_value = state
        runtime.get_node.return_value = MagicMock(code="subprocess_plugin", version="1.0.0", name="subprocess")
        runtime.get_schedule_with_node_and_version.return_value = MagicMock(id=342957720, finished=False, expired=True)
        runtime.get_sleep_process_info_with_current_node_id.return_value = MagicMock(
            process_id=189270456, root_pipeline_id="nbbf48c8619e3e858a338072abeb11f3"
        )

        callback_data_cls.objects.filter.return_value.order_by.return_value = [
            MagicMock(id=234568563, data=json.dumps({"task_success": True, "task_id": 129570155})),
            MagicMock(id=234568504, data=json.dumps({"task_success": False, "task_id": 129570155})),
        ]

        candidate = Command().inspect_candidate(129568046, "n954ea0446fb3641b5990232fc896259", None)

        self.assertTrue(candidate["safe_to_replay"])
        self.assertEqual(candidate["state"], bamboo_states.FAILED)
        self.assertEqual(candidate["latest_success_callback_data_id"], 234568563)
        self.assertEqual(candidate["schedule_id"], 342957720)
        self.assertEqual(candidate["live_process_id"], 189270456)

    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.transaction.atomic")
    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.DBSchedule")
    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.NodeCommandDispatcher")
    @patch("gcloud.taskflow3.management.commands.replay_subprocess_success_callback.BambooDjangoRuntime")
    def test_apply_replay_restores_failed_node_before_dispatch(
        self, runtime_cls, dispatcher_cls, db_schedule_cls, atomic
    ):
        runtime = runtime_cls.return_value
        dispatcher = dispatcher_cls.return_value
        dispatcher.dispatch.return_value = {"result": True, "message": "ok", "data": None}

        candidate = {
            "task_id": 129568046,
            "node_id": "n954ea0446fb3641b5990232fc896259",
            "version": "v668546486bc04d1fa1733a596c49e9b2",
            "state": bamboo_states.FAILED,
            "schedule_id": 342957720,
            "latest_success_callback_data_id": 234568563,
            "latest_success_callback_data": {"task_success": True, "task_id": 129570155},
            "engine_ver": 2,
            "safe_to_replay": True,
            "blockers": [],
        }

        result = Command().apply_replay(candidate)

        atomic.assert_called_once_with()
        db_schedule_cls.objects.filter.assert_called_once_with(id=342957720)
        db_schedule_cls.objects.filter.return_value.update.assert_called_once_with(expired=False)
        runtime.set_state.assert_any_call(
            node_id="n954ea0446fb3641b5990232fc896259",
            version="v668546486bc04d1fa1733a596c49e9b2",
            to_state=bamboo_states.READY,
        )
        runtime.set_state.assert_any_call(
            node_id="n954ea0446fb3641b5990232fc896259",
            version="v668546486bc04d1fa1733a596c49e9b2",
            to_state=bamboo_states.RUNNING,
        )
        dispatcher.dispatch.assert_called_once_with(
            command="callback",
            operator="system",
            version="v668546486bc04d1fa1733a596c49e9b2",
            data={"task_success": True, "task_id": 129570155},
        )
        self.assertEqual(result["message"], "ok")

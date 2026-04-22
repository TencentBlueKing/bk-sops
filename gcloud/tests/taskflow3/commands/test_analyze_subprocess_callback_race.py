# -*- coding: utf-8 -*-
import json

from django.test import SimpleTestCase
from pipeline.eri.models import CallbackData, Process, Schedule, State

from gcloud.taskflow3.management.commands.analyze_subprocess_callback_race import Command
from gcloud.taskflow3.models import TaskCallBackRecord


class AnalyzeSubprocessCallbackRaceCommandTestCase(SimpleTestCase):
    @staticmethod
    def _table(records):
        return {"count": len(records), "records": records}

    def test_analyze_payload_detects_subprocess_callback_race_candidate(self):
        payload = {
            "meta": {
                "exported_at": "2026-04-22T10:00:00",
                "command": "export_taskflow_related_records",
                "engine_versions": [2],
                "warnings": [],
            },
            "scope": {
                "input_task_id": 129568046,
                "root_task_id": 129568046,
                "task_ids": [129568046, 129570155],
                "pipeline_instance_ids": ["nbbf48c8619e3e858a338072abeb11f3"],
                "node_ids": ["n954ea0446fb3641b5990232fc896259"],
            },
            "tables": {
                TaskCallBackRecord._meta.db_table: self._table(
                    [
                        {
                            "id": 269651,
                            "task_id": 129570155,
                            "url": "",
                            "create_time": "2026-04-20T15:00:00",
                            "status": "success",
                            "extra_info": json.dumps(
                                {
                                    "source": "subprocess task 129570155",
                                    "node_id": "n954ea0446fb3641b5990232fc896259",
                                    "node_version": "v668546486bc04d1fa1733a596c49e9b2",
                                    "engine_ver": 2,
                                }
                            ),
                            "callback_time": "2026-04-20T15:13:58",
                        }
                    ]
                ),
                CallbackData._meta.db_table: self._table(
                    [
                        {
                            "id": 234568504,
                            "node_id": "n954ea0446fb3641b5990232fc896259",
                            "version": "v668546486bc04d1fa1733a596c49e9b2",
                            "data": json.dumps({"task_success": False, "task_id": 129570155}),
                        },
                        {
                            "id": 234568563,
                            "node_id": "n954ea0446fb3641b5990232fc896259",
                            "version": "v668546486bc04d1fa1733a596c49e9b2",
                            "data": json.dumps({"task_success": True, "task_id": 129570155}),
                        },
                    ]
                ),
                Schedule._meta.db_table: self._table(
                    [
                        {
                            "id": 342957720,
                            "type": 1,
                            "process_id": 189270456,
                            "node_id": "n954ea0446fb3641b5990232fc896259",
                            "finished": False,
                            "expired": False,
                            "scheduling": False,
                            "version": "v668546486bc04d1fa1733a596c49e9b2",
                            "schedule_times": 1,
                        }
                    ]
                ),
                State._meta.db_table: self._table(
                    [
                        {
                            "id": 1,
                            "node_id": "n954ea0446fb3641b5990232fc896259",
                            "root_id": "nbbf48c8619e3e858a338072abeb11f3",
                            "parent_id": "nbbf48c8619e3e858a338072abeb11f3",
                            "name": "FAILED",
                            "version": "v668546486bc04d1fa1733a596c49e9b2",
                            "loop": 1,
                            "inner_loop": 1,
                            "retry": 1,
                            "skip": False,
                            "error_ignored": False,
                            "created_time": "2026-04-20T15:00:00",
                            "started_time": "2026-04-20T15:00:00",
                            "archived_time": "2026-04-20T15:13:57",
                        }
                    ]
                ),
                Process._meta.db_table: self._table(
                    [
                        {
                            "id": 189270456,
                            "parent_id": 189270383,
                            "ack_num": 0,
                            "need_ack": 0,
                            "asleep": True,
                            "suspended": False,
                            "frozen": False,
                            "dead": False,
                            "last_heartbeat": "2026-04-20T15:14:00",
                            "destination_id": "nb5f7a4c93ef37aca8ca721ae68d68af",
                            "current_node_id": "n954ea0446fb3641b5990232fc896259",
                            "root_pipeline_id": "nbbf48c8619e3e858a338072abeb11f3",
                            "suspended_by": "",
                        }
                    ]
                ),
            },
        }

        analysis = Command().analyze_payload(payload)

        self.assertEqual(analysis["summary"]["race_candidates"], 1)
        candidate = analysis["candidates"][0]
        self.assertEqual(candidate["node_id"], "n954ea0446fb3641b5990232fc896259")
        self.assertEqual(candidate["version"], "v668546486bc04d1fa1733a596c49e9b2")
        self.assertEqual(candidate["latest_success_callback_data_id"], 234568563)
        self.assertEqual(candidate["latest_failed_callback_data_id"], 234568504)
        self.assertTrue(candidate["safe_to_replay"])

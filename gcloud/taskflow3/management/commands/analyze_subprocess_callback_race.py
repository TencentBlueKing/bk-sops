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
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from django.core.management import BaseCommand, CommandError
from pipeline.eri.models import CallbackData, Process, Schedule, State

from gcloud.taskflow3.models import TaskCallBackRecord


class SubprocessCallbackRaceAnalyzer(object):
    def __init__(self, payload):
        self.payload = payload
        self.tables = payload.get("tables", {})
        self.callback_records = self._records(TaskCallBackRecord)
        self.callback_data = self._records(CallbackData)
        self.schedules = self._records(Schedule)
        self.states = self._records(State)
        self.processes = self._records(Process)

        self.callback_data_by_node_version = defaultdict(list)
        for record in self.callback_data:
            self.callback_data_by_node_version[(record.get("node_id"), record.get("version"))].append(record)

        self.active_schedules_by_node_version = defaultdict(list)
        for schedule in self.schedules:
            if schedule.get("finished") or schedule.get("expired"):
                continue
            self.active_schedules_by_node_version[(schedule.get("node_id"), schedule.get("version"))].append(schedule)

        self.state_by_node_version = {(record.get("node_id"), record.get("version")): record for record in self.states}
        self.live_processes_by_node_id = defaultdict(list)
        for process in self.processes:
            if process.get("dead"):
                continue
            self.live_processes_by_node_id[process.get("current_node_id")].append(process)

    def analyze(self):
        candidates = []

        for record in self.callback_records:
            callback_info = self._parse_json(record.get("extra_info"))
            if not callback_info:
                continue

            node_id = callback_info.get("node_id")
            version = callback_info.get("node_version")
            if not node_id or not version:
                continue

            matched_callback_data = sorted(
                self.callback_data_by_node_version.get((node_id, version), []),
                key=lambda item: item.get("id", 0),
            )
            if len(matched_callback_data) < 2:
                continue

            latest_failed = None
            latest_success = None
            for callback_data in matched_callback_data:
                callback_payload = self._parse_json(callback_data.get("data")) or {}
                if callback_payload.get("task_success") is True:
                    latest_success = callback_data
                elif callback_payload.get("task_success") is False:
                    latest_failed = callback_data

            if not latest_failed or not latest_success:
                continue

            active_schedules = self.active_schedules_by_node_version.get((node_id, version), [])
            total_schedule_times = sum(schedule.get("schedule_times") or 0 for schedule in active_schedules)
            if total_schedule_times >= len(matched_callback_data):
                continue

            state = self.state_by_node_version.get((node_id, version)) or {}
            live_processes = self.live_processes_by_node_id.get(node_id, [])

            replay_blockers = []
            if not active_schedules:
                replay_blockers.append("当前节点没有未结束 schedule")
            if len(live_processes) != 1:
                replay_blockers.append("当前节点对应的存活 process 数量不是 1")
            if state.get("name") not in {"RUNNING", "FAILED"}:
                replay_blockers.append("当前节点状态不是 RUNNING/FAILED")

            candidates.append(
                {
                    "task_id": record.get("task_id"),
                    "callback_record_id": record.get("id"),
                    "node_id": node_id,
                    "version": version,
                    "callback_data_count": len(matched_callback_data),
                    "active_schedule_ids": [schedule.get("id") for schedule in active_schedules],
                    "active_schedule_times": total_schedule_times,
                    "latest_failed_callback_data_id": latest_failed.get("id"),
                    "latest_success_callback_data_id": latest_success.get("id"),
                    "state": state.get("name"),
                    "live_process_ids": [process.get("id") for process in live_processes],
                    "safe_to_replay": not replay_blockers,
                    "replay_blockers": replay_blockers,
                    "evidence": {
                        "callback_record_status": record.get("status"),
                        "callback_record_callback_time": record.get("callback_time"),
                    },
                }
            )

        candidates.sort(key=lambda item: (item["safe_to_replay"] is False, item["task_id"] or 0, item["node_id"]))
        return {
            "meta": {
                "analyzed_at": datetime.now().isoformat(),
                "command": "analyze_subprocess_callback_race",
                "source_command": self.payload.get("meta", {}).get("command"),
                "source_exported_at": self.payload.get("meta", {}).get("exported_at"),
            },
            "scope": self.payload.get("scope", {}),
            "summary": {
                "race_candidates": len(candidates),
                "safe_to_replay": len([candidate for candidate in candidates if candidate["safe_to_replay"]]),
                "unsafe_to_replay": len([candidate for candidate in candidates if not candidate["safe_to_replay"]]),
            },
            "candidates": candidates,
        }

    def _records(self, model):
        table = self.tables.get(model._meta.db_table, {})
        return list(table.get("records", []))

    @staticmethod
    def _parse_json(raw):
        if isinstance(raw, dict):
            return raw
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception:
            return {}


class Command(BaseCommand):
    help = "根据导出的任务关联记录，识别独立子流程 callback false/true 竞态及是否可安全重放"

    def add_arguments(self, parser):
        parser.add_argument("export_file", help="export_taskflow_related_records 生成的 JSON 文件路径")
        parser.add_argument("--output", default="", help="分析结果输出目录或 JSON 文件路径，默认仅打印")

    def handle(self, *args, **options):
        export_file = Path(options["export_file"]).expanduser()
        if not export_file.exists():
            raise CommandError("export file {} does not exist".format(export_file))

        payload = self._load_payload(export_file)
        analysis = self.analyze_payload(payload)
        self.stdout.write(json.dumps(analysis, ensure_ascii=False, indent=2))

        if options["output"]:
            output_path = self._resolve_output_path(options["output"], export_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS("analysis also written to {}".format(output_path)))

    @staticmethod
    def _load_payload(export_file):
        try:
            payload = json.loads(export_file.read_text(encoding="utf-8"))
        except Exception as e:
            raise CommandError("failed to load export file {}: {}".format(export_file, e))

        for key in ("meta", "scope", "tables"):
            if key not in payload:
                raise CommandError("export file {} missing key '{}'".format(export_file, key))
        return payload

    def analyze_payload(self, payload):
        return SubprocessCallbackRaceAnalyzer(payload).analyze()

    @staticmethod
    def _resolve_output_path(output, export_file):
        candidate = Path(output).expanduser()
        if candidate.suffix.lower() == ".json":
            return candidate
        return candidate / "{}_subprocess_callback_race.json".format(export_file.stem)

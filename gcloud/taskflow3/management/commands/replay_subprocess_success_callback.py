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

from bamboo_engine import states as bamboo_states
from django.db import transaction
from django.core.management import BaseCommand, CommandError
from pipeline.eri.models import CallbackData
from pipeline.eri.models import Schedule as DBSchedule
from pipeline.eri.runtime import BambooDjangoRuntime

from gcloud.taskflow3.domains.dispatchers.node import NodeCommandDispatcher
from gcloud.taskflow3.models import TaskFlowInstance


class Command(BaseCommand):
    help = "安全重放独立子流程节点最新一条成功 callback，默认 dry-run"

    def add_arguments(self, parser):
        parser.add_argument("task_id", type=int, help="父任务实例 ID")
        parser.add_argument("node_id", help="独立子流程节点 ID")
        parser.add_argument("--version", default="", help="节点版本，不传则取当前 State.version")
        parser.add_argument("--apply", action="store_true", help="确认执行重放，默认仅检查不执行")

    def handle(self, *args, **options):
        candidate = self.inspect_candidate(options["task_id"], options["node_id"], options.get("version") or None)
        self.stdout.write(json.dumps(candidate, ensure_ascii=False, indent=2))

        if not options["apply"]:
            return

        if not candidate["safe_to_replay"]:
            raise CommandError("candidate is not safe to replay: {}".format("; ".join(candidate["blockers"])))

        result = self.apply_replay(candidate)
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))

    def inspect_candidate(self, task_id, node_id, version=None):
        task = TaskFlowInstance.objects.filter(id=task_id).select_related("pipeline_instance").first()
        if not task:
            raise CommandError("taskflow instance {} does not exist".format(task_id))

        runtime = BambooDjangoRuntime()
        state = runtime.get_state(node_id)
        version = version or state.version
        node = runtime.get_node(node_id)
        schedule = runtime.get_schedule_with_node_and_version(node_id, version)

        blockers = []
        process_info = None
        try:
            process_info = runtime.get_sleep_process_info_with_current_node_id(node_id)
        except Exception as e:
            blockers.append(str(e))

        if task.engine_ver != 2:
            blockers.append("仅支持 bamboo-engine v2 任务")
        if getattr(node, "code", "") != "subprocess_plugin":
            blockers.append("当前节点不是 subprocess_plugin")
        if state.version != version:
            blockers.append("当前 state.version 与待重放版本不一致")
        if state.name not in {bamboo_states.RUNNING, bamboo_states.FAILED}:
            blockers.append("当前节点状态不是 RUNNING/FAILED")
        if schedule.finished:
            blockers.append("当前 schedule 已 finished")
        # expired schedule is replayable here: apply_replay will reactivate it before dispatching
        # the latest success callback through the formal engine callback path.
        if process_info and getattr(task.pipeline_instance, "instance_id", None) != process_info.root_pipeline_id:
            blockers.append("任务实例与节点所属 root pipeline 不匹配")

        latest_success_callback = None
        for callback_data in CallbackData.objects.filter(node_id=node_id, version=version).order_by("-id"):
            payload = self._parse_json(callback_data.data)
            if payload.get("task_success") is True:
                latest_success_callback = {"id": callback_data.id, "data": payload}
                break
        if not latest_success_callback:
            blockers.append("未找到可重放的成功 callback_data")

        return {
            "task_id": task.id,
            "engine_ver": task.engine_ver,
            "node_id": node_id,
            "version": version,
            "state": state.name,
            "schedule_id": schedule.id,
            "schedule_finished": schedule.finished,
            "schedule_expired": schedule.expired,
            "live_process_id": getattr(process_info, "process_id", None),
            "root_pipeline_id": getattr(process_info, "root_pipeline_id", None),
            "latest_success_callback_data_id": latest_success_callback["id"] if latest_success_callback else None,
            "latest_success_callback_data": latest_success_callback["data"] if latest_success_callback else None,
            "safe_to_replay": not blockers,
            "blockers": blockers,
        }

    def apply_replay(self, candidate):
        if not candidate["safe_to_replay"]:
            raise CommandError("candidate is not safe to replay")

        runtime = BambooDjangoRuntime()
        if candidate["state"] == bamboo_states.FAILED:
            with transaction.atomic():
                DBSchedule.objects.filter(id=candidate["schedule_id"]).update(expired=False)
                runtime.set_state(
                    node_id=candidate["node_id"], version=candidate["version"], to_state=bamboo_states.READY
                )
                runtime.set_state(
                    node_id=candidate["node_id"], version=candidate["version"], to_state=bamboo_states.RUNNING
                )

        dispatcher = NodeCommandDispatcher(
            engine_ver=candidate["engine_ver"],
            node_id=candidate["node_id"],
            taskflow_id=candidate["task_id"],
        )
        return dispatcher.dispatch(
            command="callback",
            operator="system",
            version=candidate["version"],
            data=candidate["latest_success_callback_data"],
        )

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

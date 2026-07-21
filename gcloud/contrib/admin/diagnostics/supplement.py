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

补充检测：bk-sops 侧任务处于"运行中"（pipeline 已启动、未完成、未撤销），但引擎侧已无存活进程。
这类是 root 级 last_heartbeat 扫描覆盖不到的场景（进程已消失，没有 heartbeat 可比），
用任务视角兜底立案。仅只读产案例，不做任何写操作。
"""
from django.conf import settings
from pipeline.contrib.diagnostics.cases import upsert_case
from pipeline.contrib.diagnostics.types import DiagnosticHit
from pipeline.eri.models import Process

from gcloud.taskflow3.models import TaskFlowInstance

STUCK_TYPE_NO_LIVE_PROCESS = "running_task_without_live_process"


def _running_root_ids(batch):
    ids = (
        TaskFlowInstance.objects.filter(
            pipeline_instance__is_started=True,
            pipeline_instance__is_finished=False,
            pipeline_instance__is_revoked=False,
        )
        .select_related("pipeline_instance")
        .values_list("pipeline_instance__instance_id", flat=True)[:batch]
    )
    return [rid for rid in ids if rid]


def _has_live_process(root_pipeline_id):
    return Process.objects.filter(root_pipeline_id=root_pipeline_id, dead=False).exists()


def _hit(root_pipeline_id):
    return DiagnosticHit(
        type=STUCK_TYPE_NO_LIVE_PROCESS,
        severity="critical",
        confidence=0.9,
        evidence={"root_pipeline_id": root_pipeline_id},
        related_objects={"root_pipeline_id": root_pipeline_id, "node_id": ""},
        recommended_actions=["inspect_node_runtime_readiness"],
        forbidden_actions=[],
        message="Running task {} has no live engine process".format(root_pipeline_id),
    )


def scan_running_tasks_without_live_process(batch=None):
    batch = batch if batch is not None else getattr(settings, "DIAGNOSTICS_SUPPLEMENT_BATCH", 200)
    cases = []
    for root_pipeline_id in _running_root_ids(batch):
        if not _has_live_process(root_pipeline_id):
            case = upsert_case(root_pipeline_id, "", _hit(root_pipeline_id))
            if case is not None:
                cases.append(case)
    return cases

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

误判防线（引擎正常收尾时先写 is_finished 再把进程置 dead，两步之间任务看起来就是"运行中且无进程"）：
1. 运行时长门槛：只看已经运行超过门槛的任务，短命任务的正常收尾不进候选；
2. 批量进程判定：一次查询判完整批候选，不再逐个查询，把整批的判定窗口从分钟级压到一次查询；
3. 立案前二次确认：重新读一次任务态，扫描期间跑完的任务不立案。
"""
import datetime
import logging

from django.conf import settings
from django.utils import timezone

# _resolve_one 复用引擎侧的案例关闭语义（(root, node, type, status) 唯一，已有 resolved 同键时合并命中再删本行）。
from pipeline.contrib.diagnostics.cases import _resolve_one, upsert_case
from pipeline.contrib.diagnostics.models import DiagnosticCase
from pipeline.contrib.diagnostics.types import DiagnosticHit
from pipeline.eri.models import Process

from gcloud.core.models import EngineConfig
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("celery")

STUCK_TYPE_NO_LIVE_PROCESS = "running_task_without_live_process"

DEFAULT_SUPPLEMENT_BATCH = 200
DEFAULT_MIN_RUNNING_SECONDS = 3600
DEFAULT_CLOSE_BATCH = 500

# "运行中"的判据。engine_ver 限 v2：v1 任务不用 eri_process，无存活进程属正常。
# is_expired 排除：运行时数据被定期清理的任务本就没有进程，不是卡住。
RUNNING_TASK_FILTER = {
    "is_deleted": False,
    "engine_ver": EngineConfig.ENGINE_VER_V2,
    "pipeline_instance__is_started": True,
    "pipeline_instance__is_finished": False,
    "pipeline_instance__is_revoked": False,
    "pipeline_instance__is_expired": False,
}


def _setting(name, default):
    value = getattr(settings, name, default)
    return default if value is None else value


def _running_root_ids(batch, started_before):
    """取候选 root：运行中且启动时间早于 started_before。

    不加 order by：start_time 无索引，排序会退化成 filesort 全量物化，而不排序时 limit 可提前终止。
    候选池超出 batch 的部分本轮不看，下一轮再看；候选池长期大于 batch 时调大
    BKAPP_DIAGNOSTICS_SUPPLEMENT_BATCH 即可，存活进程判定已是批量查询，候选数不再放大查询次数。
    """
    ids = TaskFlowInstance.objects.filter(
        pipeline_instance__start_time__lt=started_before, **RUNNING_TASK_FILTER
    ).values_list("pipeline_instance__instance_id", flat=True)[:batch]
    return [rid for rid in ids if rid]


def _roots_with_live_process(root_pipeline_ids):
    """一次查询拿到仍有存活进程的 root。"""
    if not root_pipeline_ids:
        return set()
    return set(
        Process.objects.filter(root_pipeline_id__in=root_pipeline_ids, dead=False).values_list(
            "root_pipeline_id", flat=True
        )
    )


def _still_running(root_pipeline_id):
    return TaskFlowInstance.objects.filter(
        pipeline_instance__instance_id=root_pipeline_id, **RUNNING_TASK_FILTER
    ).exists()


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


def scan_running_tasks_without_live_process(batch=None, min_running_seconds=None, now=None):
    batch = batch if batch is not None else _setting("DIAGNOSTICS_SUPPLEMENT_BATCH", DEFAULT_SUPPLEMENT_BATCH)
    if min_running_seconds is None:
        min_running_seconds = _setting("DIAGNOSTICS_SUPPLEMENT_MIN_RUNNING_SECONDS", DEFAULT_MIN_RUNNING_SECONDS)
    now = now or timezone.now()
    started_before = now - datetime.timedelta(seconds=min_running_seconds)

    candidates = _running_root_ids(batch, started_before)
    live_roots = _roots_with_live_process(candidates)

    cases = []
    for root_pipeline_id in candidates:
        if root_pipeline_id in live_roots:
            continue
        if not _still_running(root_pipeline_id):
            continue
        case = upsert_case(root_pipeline_id, "", _hit(root_pipeline_id))
        if case is not None:
            cases.append(case)
    return cases


def _open_cases_queryset():
    return DiagnosticCase.objects.filter(stuck_type=STUCK_TYPE_NO_LIVE_PROCESS, status=DiagnosticCase.STATUS_OPEN)


def _pick_closable(open_cases):
    """挑出已不再满足判据的案例：任务已完成/撤销/过期/删除/记录不存在，或进程已恢复。"""
    root_ids = [case.root_pipeline_id for case in open_cases]
    still_running = set(
        TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=root_ids, **RUNNING_TASK_FILTER).values_list(
            "pipeline_instance__instance_id", flat=True
        )
    )
    live_roots = _roots_with_live_process(root_ids)
    return [
        case
        for case in open_cases
        if not (case.root_pipeline_id in still_running and case.root_pipeline_id not in live_roots)
    ]


def _close(cases, now):
    closed = 0
    for case in cases:
        try:
            _resolve_one(case, now)
        except Exception:
            logger.exception("[diagnostics] close supplemental case %s failed", case.id)
            continue
        closed += 1
    return closed


def close_recovered_cases(batch=None, now=None):
    """随补充检测同轮收敛：把已不再满足判据的案例改为已解决，看板只留真正待治理的。

    引擎侧 close_stale_cases 以 heartbeat 恢复为判据，覆盖不到本检测（这里的 root 根本没有进程），
    且它被 Layer0 扫描开关挡住，因此单独实现。
    """
    batch = batch if batch is not None else _setting("DIAGNOSTICS_SUPPLEMENT_CLOSE_BATCH", DEFAULT_CLOSE_BATCH)
    now = now or timezone.now()

    open_cases = list(_open_cases_queryset().order_by("last_seen_at")[:batch])
    if not open_cases:
        return 0
    return _close(_pick_closable(open_cases), now)


def sweep_recovered_cases(chunk=None, now=None, dry_run=False):
    """全量清算存量案例，返回 (扫描数, 可关闭/已关闭数)。

    按 id 游标翻页，不受关闭动作改变 status 的影响；周期任务只看时间窗口，清算存量用这个。
    """
    chunk = chunk if chunk is not None else _setting("DIAGNOSTICS_SUPPLEMENT_CLOSE_BATCH", DEFAULT_CLOSE_BATCH)
    now = now or timezone.now()

    last_id = 0
    scanned = 0
    closed = 0
    while True:
        open_cases = list(_open_cases_queryset().filter(id__gt=last_id).order_by("id")[:chunk])
        if not open_cases:
            break
        last_id = open_cases[-1].id
        scanned += len(open_cases)
        closable = _pick_closable(open_cases)
        closed += len(closable) if dry_run else _close(closable, now)
    return scanned, closed

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

治理窗口：只看启动时间落在 [now-max, now-min] 之间的任务。
- 下界（min）挡误判：引擎正常收尾时先写 is_finished 再把进程置 dead，两步之间任务看起来就是"运行中且无进程"，
  短命任务会大量踩这个窗口，因此只看已经运行足够久的；
- 上界（max）挡历史僵尸：跑了几百天、引擎侧数据早已不存在的任务永远不会完成也永远不会有进程，
  既治不了也关不掉，会长期占满取样批次，让新问题排不进来。

另两道误判防线：
- 批量进程判定：一次查询判完整批候选，不再逐个查询，把整批的判定窗口从分钟级压到一次查询；
- 立案前二次确认：重新读一次任务态，扫描期间跑完的任务不立案。
"""
import datetime
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from pipeline.contrib.diagnostics.cases import upsert_case
from pipeline.contrib.diagnostics.models import DiagnosticCase
from pipeline.contrib.diagnostics.types import DiagnosticHit
from pipeline.eri.models import Process

from gcloud.core.models import EngineConfig
from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("celery")

STUCK_TYPE_NO_LIVE_PROCESS = "running_task_without_live_process"

DEFAULT_SUPPLEMENT_BATCH = 200
DEFAULT_MIN_RUNNING_SECONDS = 3600
DEFAULT_MAX_RUNNING_SECONDS = 7 * 24 * 3600
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


def _min_running_seconds(value=None):
    if value is not None:
        return value
    return _setting("DIAGNOSTICS_SUPPLEMENT_MIN_RUNNING_SECONDS", DEFAULT_MIN_RUNNING_SECONDS)


def _max_running_seconds(value=None):
    if value is not None:
        return value
    return _setting("DIAGNOSTICS_SUPPLEMENT_MAX_RUNNING_SECONDS", DEFAULT_MAX_RUNNING_SECONDS)


def _running_root_ids(batch, started_after, started_before):
    """取候选 root：运行中且启动时间落在治理窗口内。

    不加 order by：start_time 无索引，排序会退化成 filesort 全量物化，而不排序时 limit 可提前终止。
    候选池超出 batch 的部分本轮不看，下一轮再看；候选池长期大于 batch 时调大
    BKAPP_DIAGNOSTICS_SUPPLEMENT_BATCH 即可，存活进程判定已是批量查询，候选数不再放大查询次数。
    """
    ids = TaskFlowInstance.objects.filter(
        pipeline_instance__start_time__lt=started_before,
        pipeline_instance__start_time__gte=started_after,
        **RUNNING_TASK_FILTER
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


def scan_running_tasks_without_live_process(batch=None, min_running_seconds=None, max_running_seconds=None, now=None):
    batch = batch if batch is not None else _setting("DIAGNOSTICS_SUPPLEMENT_BATCH", DEFAULT_SUPPLEMENT_BATCH)
    now = now or timezone.now()
    started_before = now - datetime.timedelta(seconds=_min_running_seconds(min_running_seconds))
    started_after = now - datetime.timedelta(seconds=_max_running_seconds(max_running_seconds))

    candidates = _running_root_ids(batch, started_after, started_before)
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


def _classify(open_cases, started_after):
    """把 open 案例分成两堆终态，其余保持 open。

    - recovered：任务已完成/撤销/过期/删除/记录不存在，或进程已恢复，收敛为 resolved；
    - aged_out：任务确实还卡着，但已经超出治理窗口，收敛为 ignored（治不了了，不该继续占看板）。
    """
    root_ids = [case.root_pipeline_id for case in open_cases]
    running_start_time = dict(
        TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=root_ids, **RUNNING_TASK_FILTER).values_list(
            "pipeline_instance__instance_id", "pipeline_instance__start_time"
        )
    )
    live_roots = _roots_with_live_process(root_ids)

    recovered = []
    aged_out = []
    for case in open_cases:
        root_pipeline_id = case.root_pipeline_id
        if root_pipeline_id not in running_start_time or root_pipeline_id in live_roots:
            recovered.append(case)
            continue
        start_time = running_start_time[root_pipeline_id]
        if start_time is not None and start_time < started_after:
            aged_out.append(case)
    return recovered, aged_out


def _close_case(case, status, now):
    """把 open 案例改成终态。

    (root_pipeline_id, node_id, stuck_type, status) 唯一，已有同键终态记录时把命中并进去再删本行。
    """
    with transaction.atomic():
        twin = (
            DiagnosticCase.objects.filter(
                root_pipeline_id=case.root_pipeline_id,
                node_id=case.node_id,
                stuck_type=case.stuck_type,
                status=status,
            )
            .exclude(id=case.id)
            .first()
        )
        if twin is None:
            case.status = status
            case.last_seen_at = now
            case.save(update_fields=["status", "last_seen_at", "updated_at"])
            return

        twin.hit_count = (twin.hit_count or 0) + (case.hit_count or 0)
        if case.last_seen_at and case.last_seen_at > twin.last_seen_at:
            twin.last_seen_at = case.last_seen_at
        twin.save(update_fields=["hit_count", "last_seen_at", "updated_at"])
        case.delete()


def _close(cases, status, now):
    closed = 0
    for case in cases:
        try:
            _close_case(case, status, now)
        except Exception:
            logger.exception("[diagnostics] close supplemental case %s as %s failed", case.id, status)
            continue
        closed += 1
    return closed


def close_recovered_cases(batch=None, max_running_seconds=None, now=None):
    """随补充检测同轮收敛，返回 (resolved 数, ignored 数)。

    引擎侧 close_stale_cases 以 heartbeat 恢复为判据，覆盖不到本检测（这里的 root 根本没有进程），
    且它被 Layer0 扫描开关挡住，因此单独实现。
    """
    batch = batch if batch is not None else _setting("DIAGNOSTICS_SUPPLEMENT_CLOSE_BATCH", DEFAULT_CLOSE_BATCH)
    now = now or timezone.now()
    started_after = now - datetime.timedelta(seconds=_max_running_seconds(max_running_seconds))

    open_cases = list(_open_cases_queryset().order_by("last_seen_at")[:batch])
    if not open_cases:
        return 0, 0

    recovered, aged_out = _classify(open_cases, started_after)
    return (
        _close(recovered, DiagnosticCase.STATUS_RESOLVED, now),
        _close(aged_out, DiagnosticCase.STATUS_IGNORED, now),
    )


def sweep_recovered_cases(chunk=None, max_running_seconds=None, now=None, dry_run=False):
    """全量清算存量案例，返回 (扫描数, resolved 数, ignored 数)。

    按 id 游标翻页，不受关闭动作改变 status 的影响；周期任务只看时间窗口，清算存量用这个。
    """
    chunk = chunk if chunk is not None else _setting("DIAGNOSTICS_SUPPLEMENT_CLOSE_BATCH", DEFAULT_CLOSE_BATCH)
    now = now or timezone.now()
    started_after = now - datetime.timedelta(seconds=_max_running_seconds(max_running_seconds))

    last_id = 0
    scanned = 0
    resolved_total = 0
    aged_out_total = 0
    while True:
        open_cases = list(_open_cases_queryset().filter(id__gt=last_id).order_by("id")[:chunk])
        if not open_cases:
            break
        last_id = open_cases[-1].id
        scanned += len(open_cases)

        recovered, aged_out = _classify(open_cases, started_after)
        if dry_run:
            resolved_total += len(recovered)
            aged_out_total += len(aged_out)
        else:
            resolved_total += _close(recovered, DiagnosticCase.STATUS_RESOLVED, now)
            aged_out_total += _close(aged_out, DiagnosticCase.STATUS_IGNORED, now)
    return scanned, resolved_total, aged_out_total

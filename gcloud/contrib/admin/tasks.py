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
import logging
from datetime import timedelta
from uuid import uuid4

from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

logger = logging.getLogger("celery")

# 诊断能力随 bamboo-pipeline>=3.24.12 提供；未升级依赖时相关周期任务惰性降级为 no-op。
try:
    from pipeline.contrib.diagnostics.scanner import scan_stalled_roots
except ImportError:  # pragma: no cover - depends on engine version
    scan_stalled_roots = None

# 三期检测扫描器随 bamboo-pipeline>=3.24.20 提供；旧版本下窗口扫描回落到 M1 取样，另两个周期任务为 no-op。
try:
    from pipeline.contrib.diagnostics.callback_scan import scan_callbacks
    from pipeline.contrib.diagnostics.signature_scan import scan_signatures
    from pipeline.contrib.diagnostics.window_scan import scan_silence_windows
except ImportError:  # pragma: no cover - depends on engine version
    scan_callbacks = scan_signatures = scan_silence_windows = None

_SCAN_LOCK_KEY = "diagnostics_scan_lock"
_SCAN_LOCK_EXPIRE = 30 * 60
_SIGNATURE_LOCK_KEY = "diagnostics_signature_scan_lock"
_CALLBACK_LOCK_KEY = "diagnostics_callback_scan_lock"
_FAST_SCAN_LOCK_EXPIRE = 5 * 60


def _acquire_singleflight(key, expire):
    """非阻塞单例锁：抢到返回 token，抢不到返回 None（另一 worker 正在跑，直接跳过）。"""
    token = uuid4().hex
    if settings.redis_inst.set(name=key, value=token, nx=True, ex=expire):
        return token
    return None


def _release_singleflight(key, token):
    """仅当持有者是自己时释放，避免误删他人锁。"""
    try:
        current = settings.redis_inst.get(key)
        current = current.decode() if isinstance(current, bytes) else current
        if current == token:
            settings.redis_inst.delete(key)
    except Exception:  # pragma: no cover - best effort release
        logger.exception("[diagnostics] release scan lock failed")


def _scan_roots():
    """窗口扫描开启后替代 M1 取样扫描：两者判定的是同一件事（root 静默），同时跑只会重复立案。"""
    if scan_silence_windows is not None and settings.PIPELINE_DIAGNOSTICS_WINDOW_SCAN_ENABLED:
        return sum(report.cases for report in scan_silence_windows())
    return len(scan_stalled_roots())


def _run_singleflight(name, key, enabled, scan):
    """开关关闭时不碰 redis；抢不到锁说明上一轮还没跑完，直接跳过；扫描异常只记日志，不影响下一轮。"""
    if scan is None or not enabled:
        return
    token = _acquire_singleflight(key, _FAST_SCAN_LOCK_EXPIRE)
    if token is None:
        logger.info("[diagnostics] %s skipped: another run holds the lock", name)
        return
    try:
        scan()
    except Exception:
        logger.exception("[diagnostics] %s failed", name)
    finally:
        _release_singleflight(key, token)


@periodic_task(run_every=(crontab(*settings.DIAGNOSTICS_SCAN_CRON)), ignore_result=True, queue="task_data_clean")
def scan_stuck_diagnostics():
    """周期扫描停滞 root，只读产出诊断案例（写操作默认关闭）。"""
    if scan_stalled_roots is None:
        return

    token = _acquire_singleflight(_SCAN_LOCK_KEY, _SCAN_LOCK_EXPIRE)
    if token is None:
        logger.info("[diagnostics] scan_stuck_diagnostics skipped: another run holds the lock")
        return

    try:
        cases = _scan_roots()
        logger.info("[diagnostics] scan_stuck_diagnostics upserted cases: %s", cases)

        try:
            from gcloud.contrib.admin.diagnostics.supplement import (
                close_recovered_cases,
                scan_running_tasks_without_live_process,
            )

            supplemented = scan_running_tasks_without_live_process()
            logger.info("[diagnostics] supplemental cases: %s", len(supplemented))
            # 与补充检测同轮收敛：任务恢复或跑完后关成 resolved，超出治理窗口的关成 ignored。
            resolved, aged_out = close_recovered_cases()
            logger.info("[diagnostics] supplemental cases closed: resolved=%s aged_out=%s", resolved, aged_out)
        except ImportError:  # pragma: no cover - depends on engine version
            pass
        except Exception:
            logger.exception("[diagnostics] supplemental scan failed")
    finally:
        _release_singleflight(_SCAN_LOCK_KEY, token)


@periodic_task(
    run_every=(crontab(*settings.DIAGNOSTICS_SIGNATURE_SCAN_CRON)), ignore_result=True, queue="task_data_clean"
)
def scan_stuck_signatures():
    """按进程形态快检消息丢失（执行、轮询、父子进程），只立案不重放。"""
    _run_singleflight(
        "scan_stuck_signatures",
        _SIGNATURE_LOCK_KEY,
        settings.PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED,
        scan_signatures,
    )


@periodic_task(
    run_every=timedelta(seconds=settings.DIAGNOSTICS_CALLBACK_SCAN_INTERVAL),
    ignore_result=True,
    queue="task_data_clean",
)
def scan_stuck_callbacks():
    """推进回调水位，确认"回调已落库但调度没消费"的案例，只立案不重放。"""
    _run_singleflight(
        "scan_stuck_callbacks",
        _CALLBACK_LOCK_KEY,
        settings.PIPELINE_DIAGNOSTICS_CALLBACK_SCAN_ENABLED,
        scan_callbacks,
    )


@periodic_task(run_every=(crontab(*settings.DIAGNOSTICS_CLEANUP_CRON)), ignore_result=True, queue="task_data_clean")
def cleanup_diagnostics():
    """按保留期清理诊断事件/案例/审计（复用引擎侧 cleanup_diagnostics 命令）。"""
    if scan_stalled_roots is None:
        return

    from django.core.management import call_command

    try:
        call_command("cleanup_diagnostics")
    except Exception:
        logger.exception("[diagnostics] cleanup_diagnostics failed")

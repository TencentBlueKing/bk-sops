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

_SCAN_LOCK_KEY = "diagnostics_scan_lock"
_SCAN_LOCK_EXPIRE = 30 * 60


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
        cases = scan_stalled_roots()
        logger.info("[diagnostics] scan_stuck_diagnostics upserted cases: %s", len(cases))

        try:
            from gcloud.contrib.admin.diagnostics.supplement import scan_running_tasks_without_live_process

            supplemented = scan_running_tasks_without_live_process()
            logger.info("[diagnostics] supplemental cases: %s", len(supplemented))
        except ImportError:  # pragma: no cover - depends on engine version
            pass
        except Exception:
            logger.exception("[diagnostics] supplemental scan failed")
    finally:
        _release_singleflight(_SCAN_LOCK_KEY, token)


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

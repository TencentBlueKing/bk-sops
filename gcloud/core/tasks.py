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

import datetime
import logging
import time
import traceback
from contextlib import contextmanager
from time import monotonic

import dateutil.relativedelta
from blueapps.contrib.celery_tools.periodic import periodic_task
from celery import current_app
from celery.schedules import crontab
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils import timezone
from django_celery_beat.models import PeriodicTask as DjangoCeleryBeatPeriodicTask
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab
from pipeline.engine.core.data.api import _backend, _candidate_backend
from pipeline.engine.core.data.redis_backend import RedisDataBackend

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.project import sync_projects_from_cmdb
from gcloud.periodictask.models import PeriodicTask
from gcloud.shortcuts.message.send_msg import send_message
from packages.bkapi.bk_user.shortcuts import get_client_by_username

logger = logging.getLogger("celery")

LOCK_EXPIRE = 60 * 10
LOCK_ID = "cmdb_business_sync_lock"


@contextmanager
def redis_lock(lock_id, task_id):
    timeout_at = monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, task_id, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # advantage of using add() for atomic locking
        if monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@periodic_task(run_every=TzAwareCrontab(minute="*/2"))
def cmdb_business_sync_task():
    task_id = cmdb_business_sync_task.request.id
    with redis_lock(LOCK_ID, task_id) as acquired:
        if acquired:
            logger.info("Start sync business from cmdb...")
            try:
                client = get_client_by_username(
                    username=settings.SYSTEM_USE_API_ACCOUNT, stage=settings.BK_APIGW_STAGE_NAME
                )
                result = client.api.list_tenant(headers={"X-Bk-Tenant-Id": "system"})
                for tenant in result["data"]:
                    if tenant["status"] != "enabled":
                        continue
                    sync_projects_from_cmdb(
                        username=settings.SYSTEM_USE_API_ACCOUNT, use_cache=False, tenant_id=tenant["id"]
                    )
            except exceptions.APIError as e:
                logger.error(
                    "An error occurred when sync cmdb business, message: {msg}, trace: {trace}".format(
                        msg=str(e), trace=traceback.format_exc()
                    )
                )
        else:
            logger.info("Can not get sync_business lock, sync operation abandon")


@periodic_task(run_every=TzAwareCrontab(**settings.EXPIRED_SESSION_CLEAN_CRON))
def clean_django_sessions():
    """
    Clean expired sessions from the database.
    采用小批量删除方式，防止存量数据过大的情况
    """
    logger.info("Start clean django sessions...")
    start_time = time.time()
    try:
        max_clean_num = settings.MAX_EXPIRED_SESSION_CLEAN_NUM
        session_keys = list(
            Session.objects.filter(expire_date__lt=timezone.now()).values_list("session_key", flat=True)[:max_clean_num]
        )
        result = Session.objects.filter(session_key__in=session_keys).delete()
        logger.info(f"Clean django sessions result: {result}, cost time: {time.time() - start_time}")
    except Exception as e:
        logger.exception(f"Clean django sessions error: {e}")


@current_app.task
def migrate_pipeline_parent_data_task():
    """
    将 pipeline 的 schedule_parent_data 从 _backend(redis) 迁移到 _candidate_backend(mysql)
    """
    if not isinstance(_backend, RedisDataBackend):
        logger.error("[migrate_pipeline_parent_data] _backend should be RedisDataBackend")
        return

    if _candidate_backend is None:
        logger.error(
            "[migrate_pipeline_parent_data]_candidate_backend is None, "
            "please set env variable(BKAPP_PIPELINE_DATA_CANDIDATE_BACKEND) first"
        )
        return

    r = settings.redis_inst
    pipeline_data_keys = list(r.scan_iter("*_schedule_parent_data"))
    keys_len = len(pipeline_data_keys)
    logger.info("[migrate_pipeline_parent_data] start to migrate {} keys.".format(keys_len))
    for i, key in enumerate(pipeline_data_keys, 1):
        try:
            logger.info("[migrate_pipeline_parent_data] process[{}/{}]".format(i, keys_len))
            value = _backend.get_object(key)
            _candidate_backend.set_object(key, value)
            r.expire(key, 60 * 60 * 24)  # expire in 1 day
        except Exception:
            logger.exception("[migrate_pipeline_parent_data] {} key migrate err.".format(i))

    logger.info("[migrate_pipeline_parent_data] migrate done!")


@periodic_task(run_every=TzAwareCrontab(minute=1, hour="*/4"))
def cmdb_business_sync_shutdown_periodic_task():
    task_id = cmdb_business_sync_shutdown_periodic_task.request.id
    with redis_lock(LOCK_ID, task_id) as acquired:
        if acquired:
            try:
                task_ids = [
                    item["task__celery_task__id"]
                    for item in PeriodicTask.objects.filter(project__is_disable=True).values("task__celery_task__id")
                ]
                logger.info("[shutdown_periodic_task] disabled the deleted periodic task: {}".format(task_ids))
                DjangoCeleryBeatPeriodicTask.objects.filter(id__in=task_ids).update(enabled=False)
            except Exception as e:
                logger.exception(
                    "[shutdown_periodic_task] closing periodic task from cmdb, message: {msg}".format(msg=str(e))
                )
        else:
            logger.info("[shutdown_periodic_task] Can not get sync_business lock, sync operation abandon")


@current_app.task
def send_periodic_task_notify(executor, notify_type, receivers, title, content):
    try:
        send_message(executor, notify_type, receivers, title, content)
    except Exception as e:
        logger.exception(f"send periodic task notify error: {e}")


@periodic_task(run_every=(crontab(*settings.PERIODIC_TASK_REMINDER_SCAN_CRON)))
def scan_periodic_task(is_send_notify: bool = True):
    if not settings.PERIODIC_TASK_REMINDER_SWITCH:
        return
    title = "【标准运维 APP 提醒】请确认您正在运行的周期任务状态"
    # 以执行人维度发邮件通知
    periodic_tasks = (
        PeriodicTask.objects.filter(task__celery_task__enabled=True)
        .values(
            "id",
            "task__creator",
            "project__id",
            "project__name",
            "create_time",
            "edit_time",
            "task__last_run_at",
            "task__name",
            "task__total_run_count",
        )
        .order_by("-edit_time")
    )
    data = {}
    user_task_id = {}
    for p_task in periodic_tasks:
        last_month_time = datetime.datetime.now() + dateutil.relativedelta.relativedelta(
            months=-int(settings.PERIODIC_TASK_REMINDER_TIME)
        )
        edit_time = p_task["edit_time"] if p_task["edit_time"] else p_task["create_time"]
        if edit_time and last_month_time.timestamp() < edit_time.timestamp():
            continue
        creator = p_task["task__creator"]
        project_name = p_task["project__name"]
        task_dict = {
            "edit_time": p_task["edit_time"],
            "last_run_at": p_task["task__last_run_at"],
            "name": p_task["task__name"],
            "total_run_count": p_task["task__total_run_count"],
            "task_link": settings.BK_SOPS_HOST.rstrip("/")
            + f"/taskflow/home/periodic/{p_task['project__id']}/?limit=15&page=1&task_id={p_task['id']}",
        }
        if creator in data:
            if project_name in data[creator]:
                data[creator][project_name].append(task_dict)
            else:
                data[creator][project_name] = [task_dict]
            user_task_id[creator].add(p_task["id"])
        else:
            data[creator] = {project_name: [task_dict]}
            user_task_id[creator] = {p_task["id"]}
    # 发送通知
    if is_send_notify:
        for notifier, tasks in data.items():
            logger.info(f"{notifier} has {user_task_id[notifier]} tasks")
            try:
                mail_content = render_to_string(
                    "core/period_task_notice_mail.html",
                    {
                        "notifier": notifier,
                        "period_task_times": settings.PERIODIC_TASK_REMINDER_TIME,
                        "task_projects": tasks,
                    },
                )
                send_periodic_task_notify.delay(
                    "admin", settings.PERIODIC_TASK_REMINDER_NOTIFY_TYPE, notifier, title, mail_content
                )
            except Exception as e:
                logger.exception(f"send periodic task notify error: {e}")
    return data

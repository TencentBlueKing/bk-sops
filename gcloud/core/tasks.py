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

import dateutil.relativedelta
from celery import task
from celery.five import monotonic
from celery.task import periodic_task
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import timezone
from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab
from pipeline.engine.core.data.api import _backend, _candidate_backend
from pipeline.engine.core.data.redis_backend import RedisDataBackend

from gcloud import exceptions
from gcloud.conf import settings
from gcloud.core.api_adapter.user_info import get_user_info
from gcloud.core.apis.drf.serilaziers.periodic_task import PeriodicTaskMailInfoSerializer
from gcloud.core.models import Project
from gcloud.core.project import sync_projects_from_cmdb
from gcloud.core.utils.sites.open.utils import get_user_business_list
from gcloud.periodictask.models import PeriodicTask
from gcloud.shortcuts.message.send_msg import send_message

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
                sync_projects_from_cmdb(username=settings.SYSTEM_USE_API_ACCOUNT, use_cache=False)
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


@task
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


@periodic_task(run_every=TzAwareCrontab(minute="*/2"))
def cmdb_business_sync_shutdown_period_task():
    task_id = cmdb_business_sync_shutdown_period_task.request.id
    with redis_lock(LOCK_ID, task_id) as acquired:
        if acquired:
            logger.info("Start sync business from cmdb...")
            try:
                biz_list = get_user_business_list(username=settings.SYSTEM_USE_API_ACCOUNT, use_cache=False)
                all_biz_cc_ids = set()
                archived_biz_cc_ids = set()
                for biz in biz_list:
                    if biz["bk_biz_name"] == "资源池":
                        continue
                    biz_cc_id = biz["bk_biz_id"]
                    biz_status = biz.get("bk_data_status", "enable")
                    all_biz_cc_ids.add(biz_cc_id)
                    if biz_status == "disabled":
                        archived_biz_cc_ids.add(biz_cc_id)
                exist_sync_biz_cc_ids = set(Project.objects.filter(from_cmdb=True).values_list("bk_biz_id", flat=True))
                deleted_biz_cc_ids = exist_sync_biz_cc_ids - all_biz_cc_ids
                archived_cc_ids = archived_biz_cc_ids | deleted_biz_cc_ids
                period_tasks = PeriodicTask.objects.filter(project__id__in=archived_cc_ids).all()
                for period_task in period_tasks:
                    period_task.set_enabled(False)
            except exceptions.APIError as e:
                logger.error(
                    "An error occurred when sync cmdb business, message: {msg}, trace: {trace}".format(
                        msg=str(e), trace=traceback.format_exc()
                    )
                )
        else:
            logger.info("Can not get sync_business lock, sync operation abandon")


@task
def send_period_task_notify(executor, notify_type, receivers, title, content):
    try:
        send_message(executor, notify_type, receivers, title, content)
    except Exception as e:
        logger.exception(f"send period task notify error: {e}")


@periodic_task(run_every=TzAwareCrontab(**settings.EXPIRED_SESSION_PERIOD_TASK_SCAN))
def scan_period_task():
    title = "【标准运维 APP 提醒】请确认您正在运行的周期任务状态"
    # 以执行人维度发邮件通知
    queryset = PeriodicTask.objects.filter(task__celery_task__enabled=True).order_by("-edit_time")
    task_creators = queryset.values("task__creator").distinct()
    data = {}
    for task_creator in task_creators:
        data[task_creator["task__creator"]] = []
        # 超过一个月周期任务
        last_month_time = datetime.datetime.now() + dateutil.relativedelta.relativedelta(
            months=-int(settings.PERIOD_TASK_TIMES)
        )
        queryset = queryset.select_related("task").filter(
            task__creator=task_creator["task__creator"], edit_time__lt=last_month_time
        )
        task_projects = queryset.values("project__name").annotate(count=Count("project__name"))
        for task_project in task_projects:
            tasks = queryset.filter(project__name=task_project["project__name"])
            serializer = PeriodicTaskMailInfoSerializer(instance=tasks, many=True)
            data[task_creator["task__creator"]].append(
                {"project_name": task_project["project__name"], "tasks": serializer.data}
            )
    # 发送通知
    for notifier, tasks in data.items():
        user_info = get_user_info(notifier)
        mail_content = render_to_string(
            "core/period_task_notice_mail.html",
            {
                "notifier": notifier,
                "ch_notifier": user_info["data"]["bk_username"],
                "period_task_times": settings.PERIOD_TASK_TIMES,
                "task_projects": data[notifier],
            },
        )
        try:
            send_period_task_notify.delay(
                "admin", settings.PERIOD_TASK_MESSAGE_NOTIFY_TYPE, notifier, title, mail_content
            )
        except Exception as e:
            logger.exception(f"send period task notify error: {e}")

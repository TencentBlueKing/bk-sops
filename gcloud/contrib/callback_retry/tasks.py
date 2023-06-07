# -*- coding: utf-8 -*-
import datetime
import logging

from celery.task import periodic_task
from django.conf import settings
from celery.schedules import crontab

from gcloud.contrib.callback_retry.models import CallbackRetryTask, CallbackStatus
from gcloud.core.models import EngineConfig
from gcloud.taskflow3.domains.dispatchers import NodeCommandDispatcher
from gcloud.utils.decorators import time_record

logger = logging.getLogger("root")


@periodic_task(run_every=(crontab(*settings.CALLBACK_RETRY_CRON)), ignore_result=True, queue="task_data_clean")
@time_record(logger)
def run_callback_retry():
    if not settings.ENABLE_CALLBACK_RETRY_TASK:
        logger.info("Skip callback retry task")

    # 需要定义这一次批量处理的节点数量
    tasks = CallbackRetryTask.objects.filter(status=CallbackStatus.READY.value)
    logger.info("[run_callback_retry] found {} tasks need to callback retry".format(tasks.count()))
    for task in tasks:
        node_id = task.node_id
        node_version = task.version
        callback_data = task.data

        dispatchers = NodeCommandDispatcher(
            engine_ver=EngineConfig.ENGINE_VER_V2, node_id=node_id, taskflow_id=task.task_id
        )

        callback_result = dispatchers.dispatch(
            command="callback", operator="", version=node_version, data=callback_data
        )

        # 回调失败的情况
        task.count = task.count + 1

        if not callback_result["result"]:
            logger.info(
                "[run_callback_retry] callback retry failed, task_id = {}, result = {}".format(task.id, callback_result)
            )
            task.error = callback_result.get("message")
            if task.count > settings.MAX_CALLBACK_RETRY_TIMES:
                task.status = CallbackStatus.FAILED.value
        else:
            task.status = CallbackStatus.SUCCESS.value
            task.finish_time = datetime.datetime.now()

    CallbackRetryTask.objects.bulk_update(tasks, ["count", "error", "status", "finish_time"])

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import traceback
import logging
import contextlib

from django.db import transaction

from pipeline.engine import signals, states, exceptions
from pipeline.engine.core.data import get_schedule_parent_data, set_schedule_data, delete_parent_data
from pipeline.engine.models import ScheduleService, Data, Status, PipelineProcess
from django_signal_valve import valve

logger = logging.getLogger('celery')


@contextlib.contextmanager
def schedule_exception_handler(process_id, schedule_id):
    try:
        yield
    except Exception as e:
        activity_id = schedule_id[:ScheduleService.SCHEDULE_ID_SPLIT_DIVISION]
        version = schedule_id[ScheduleService.SCHEDULE_ID_SPLIT_DIVISION:]
        if Status.objects.filter(id=activity_id, version=version).exists():
            logger.error(traceback.format_exc(e))
            process = PipelineProcess.objects.get(id=process_id)
            process.exit_gracefully(e)
        else:
            logger.warning('schedule(%s - %s) forced exit.' % (activity_id, version))

        delete_parent_data(schedule_id)


def schedule(process_id, schedule_id):
    """
    调度服务主函数
    :param process_id: 被调度的节点所属的 PipelineProcess
    :param schedule_id: 调度 ID
    :return:
    """
    with schedule_exception_handler(process_id, schedule_id):
        ScheduleService.objects.filter(id=schedule_id).update(is_scheduling=True)
        sched_service = ScheduleService.objects.get(id=schedule_id)
        service_act = sched_service.service_act
        act_id = sched_service.activity_id
        version = sched_service.version

        if not Status.objects.filter(id=act_id, version=version).exists():
            # forced failed
            logger.warning('schedule service failed, schedule(%s - %s) had been forced exit.' % (act_id, version))
            sched_service.destroy()
            return

        # get data
        parent_data = get_schedule_parent_data(sched_service.id)
        if parent_data is None:
            raise exceptions.DataRetrieveError(
                'child process(%s) retrieve parent_data error, sched_id: %s' % (process_id, schedule_id))

        # schedule
        ex_data = None
        success = False
        try:
            success = service_act.schedule(parent_data, sched_service.callback_data)
            if success is None:
                success = True
        except Exception as e:
            if service_act.error_ignorable:
                success = True
                service_act.ignore_error()
                service_act.finish_schedule()

            ex_data = traceback.format_exc(e)
            logging.error(ex_data)

        sched_service.schedule_times += 1
        set_schedule_data(sched_service.id, parent_data)

        # schedule failed
        if not success:
            if not Status.objects.transit(id=act_id, version=version, to_state=states.FAILED).result:
                # forced failed
                logger.warning('FAILED transit failed, schedule(%s - %s) had been forced exit.' % (act_id, version))
                sched_service.destroy()
                return

            if service_act.timeout:
                signals.service_activity_timeout_monitor_end.send(sender=service_act.__class__,
                                                                  node_id=service_act.id,
                                                                  version=version)
                logger.info('node %s %s timeout monitor revoke' % (service_act.id, version))

            Data.objects.write_node_data(service_act, ex_data=ex_data)
            process = PipelineProcess.objects.get(id=sched_service.process_id)
            process.adjust_status()

            # send activity error signal

            try:
                service_act.schedule_fail()
            except Exception as e:
                logger.error('schedule_fail handler fail: %s' % traceback.format_exc(e))

            signals.service_schedule_fail.send(sender=ScheduleService,
                                               activity_shell=service_act,
                                               schedule_service=sched_service,
                                               ex_data=ex_data)

            valve.send(signals, 'activity_failed',
                       sender=process.root_pipeline,
                       pipeline_id=process.root_pipeline_id,
                       pipeline_activity_id=service_act.id)
            return

        # schedule execute finished or callback finished
        if service_act.is_schedule_done() or sched_service.wait_callback:
            error_ignorable = not service_act.get_result_bit()
            if not Status.objects.transit(id=act_id, version=version, to_state=states.FINISHED).result:
                # forced failed
                logger.warning('FINISHED transit failed, schedule(%s - %s) had been forced exit.' % (act_id, version))
                sched_service.destroy()
                return

            if service_act.timeout:
                signals.service_activity_timeout_monitor_end.send(sender=service_act.__class__,
                                                                  node_id=service_act.id,
                                                                  version=version)
                logger.info('node %s %s timeout monitor revoke' % (service_act.id, version))

            Data.objects.write_node_data(service_act)
            if error_ignorable:
                s = Status.objects.get(id=act_id)
                s.error_ignorable = True
                s.save()

            # sync parent data
            with transaction.atomic():
                process = PipelineProcess.objects.select_for_update().get(id=sched_service.process_id)
                if not process.is_alive:
                    logger.warning('schedule(%s - %s) revoked.' % (act_id, version))
                    sched_service.destroy()
                    return

                process.top_pipeline.data.update_outputs(parent_data.get_outputs())
                # extract outputs
                process.top_pipeline.context.extract_output(service_act)
                process.save(save_snapshot=True)

            # clear temp data
            delete_parent_data(sched_service.id)
            # save schedule service
            sched_service.finish()

            signals.service_schedule_success.send(sender=ScheduleService,
                                                  activity_shell=service_act,
                                                  schedule_service=sched_service)

            valve.send(signals, 'wake_from_schedule',
                       sender=ScheduleService,
                       process_id=sched_service.process_id,
                       activity_id=sched_service.activity_id)
        else:
            sched_service.set_next_schedule()

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

from __future__ import absolute_import
import logging
import traceback

from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.data.hydration import hydrate_node_data
from pipeline.engine import signals
from pipeline.engine.models import (
    Status,
    Data,
    ScheduleService,
)
from django_signal_valve import valve

from .base import FlowElementHandler

logger = logging.getLogger('celery')

__all__ = ['ServiceActivityHandler']


class ServiceActivityHandler(FlowElementHandler):

    @staticmethod
    def element_cls():
        return ServiceActivity

    def handle(self, process, element, status):
        success = False
        exception_occurred = False
        monitoring = False
        version = status.version
        root_pipeline = process.root_pipeline

        # rerun mode
        if status.loop > 1 and not element.on_retry():
            element.prepare_rerun_data()
            process.top_pipeline.context.recover_variable()

        elif element.on_retry():
            element.retry_at_current_exec()

        # set loop to data
        element.data.inputs._loop = status.loop - 1
        element.data.outputs._loop = status.loop - 1

        # pre output extract
        process.top_pipeline.context.extract_output(element)

        # hydrate inputs
        hydrate_node_data(element)

        if element.timeout:
            logger.info('node %s %s start timeout monitor, timeout: %s' % (element.id, version, element.timeout))
            signals.service_activity_timeout_monitor_start.send(sender=element.__class__,
                                                                node_id=element.id,
                                                                version=version,
                                                                root_pipeline_id=root_pipeline.id,
                                                                countdown=element.timeout)
            monitoring = True

        # execute service
        try:
            success = element.execute(root_pipeline.data)
        except Exception as e:
            if element.error_ignorable:
                # ignore exception
                success = True
                exception_occurred = True
                element.ignore_error()
            ex_data = traceback.format_exc(e)
            element.data.outputs.ex_data = ex_data
            logger.error(ex_data)

        # process result
        if success is False:
            ex_data = element.data.get_one_of_outputs('ex_data')
            Status.objects.fail(element, ex_data)
            try:
                element.failure_handler(root_pipeline.data)
            except Exception as e:
                logger.error('failure_handler(%s) failed: %s' % (element.id, traceback.format_exc(e)))

            if monitoring:
                signals.service_activity_timeout_monitor_end.send(sender=element.__class__,
                                                                  node_id=element.id,
                                                                  version=version)
                logger.info('node %s %s timeout monitor revoke' % (element.id, version))

            # send activity error signal
            valve.send(signals, 'activity_failed', sender=root_pipeline,
                       pipeline_id=root_pipeline.id,
                       pipeline_activity_id=element.id)

            return self.HandleResult(next_node=None, should_return=False, should_sleep=True)
        else:
            is_error_ignored = element.error_ignorable and not element.get_result_bit()
            if element.need_schedule() and not exception_occurred and not is_error_ignored:
                # write data before schedule
                Data.objects.write_node_data(element)
                # set schedule
                ScheduleService.objects.set_schedule(element.id,
                                                     service_act=element.shell(),
                                                     process_id=process.id,
                                                     version=version,
                                                     parent_data=process.top_pipeline.data)
                return self.HandleResult(next_node=None, should_return=True, should_sleep=True)

            process.top_pipeline.context.extract_output(element)
            error_ignorable = not element.get_result_bit()

            if monitoring:
                signals.service_activity_timeout_monitor_end.send(sender=element.__class__,
                                                                  node_id=element.id,
                                                                  version=version)
                logger.info('node %s %s timeout monitor revoke' % (element.id, version))

            if not Status.objects.finish(element, error_ignorable):
                # has been forced failed
                return self.HandleResult(next_node=None, should_return=False, should_sleep=True)
            return self.HandleResult(next_node=element.next(), should_return=False, should_sleep=False)

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

from abc import ABCMeta, abstractmethod
from copy import deepcopy

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.base import FlowNode
from collections import namedtuple


def _empty_method(data, parent_data):
    return


class Activity(FlowNode):
    __metaclass__ = ABCMeta

    def __init__(self, id, name=None, data=None, failure_handler=None):
        super(Activity, self).__init__(id, name, data)
        self._failure_handler = failure_handler or _empty_method

    def next(self):
        return self.outgoing.unique_one().target

    def failure_handler(self, parent_data):
        return self._failure_handler(data=self.data, parent_data=parent_data)

    def skip(self):
        raise NotImplementedError()

    def prepare_rerun_data(self):
        raise NotImplementedError()


class ServiceActivity(Activity):
    result_bit = '_result'
    loop = '_loop'
    ON_RETRY = '_on_retry'

    def __init__(self,
                 id,
                 service,
                 name=None,
                 data=None,
                 error_ignorable=False,
                 failure_handler=None,
                 skippable=True,
                 can_retry=True,
                 timeout=None):
        super(ServiceActivity, self).__init__(id, name, data, failure_handler)
        self.service = service
        self.error_ignorable = error_ignorable
        self.skippable = skippable
        self.can_retry = can_retry
        self.timeout = timeout

        if data:
            self._prepared_inputs = self.data.inputs_copy()
            self._prepared_outputs = self.data.outputs_copy()

    def execute(self, parent_data):
        self.service.logger = self.logger
        self.service.id = self.id
        result = self.service.execute(self.data, parent_data)

        # set result
        self.set_result_bit(result)

        if self.error_ignorable:
            return True
        return result

    def set_result_bit(self, result):
        if result is False:
            self.data.set_outputs(self.result_bit, False)
        else:
            self.data.set_outputs(self.result_bit, True)

    def get_result_bit(self):
        return self.data.get_one_of_outputs(self.result_bit, False)

    def skip(self):
        self.set_result_bit(True)
        return True

    def ignore_error(self):
        self.set_result_bit(False)
        return True

    def clear_outputs(self):
        self.data.reset_outputs({})

    def need_schedule(self):
        return self.service.need_schedule()

    def schedule(self, parent_data, callback_data=None):
        self.service.logger = self.logger
        self.service.id = self.id
        result = self.service.schedule(self.data, parent_data, callback_data)
        self.set_result_bit(result)

        if result is False:
            if self.error_ignorable:
                self.service.finish_schedule()
                return True

        return result

    def is_schedule_done(self):
        return self.service.is_schedule_finished()

    def finish_schedule(self):
        self.service.finish_schedule()

    def shell(self):
        shell = ServiceActivity(id=self.id, service=self.service, name=self.name, data=self.data,
                                error_ignorable=self.error_ignorable, timeout=self.timeout)
        return shell

    def schedule_fail(self):
        return

    def schedule_success(self):
        return

    def prepare_rerun_data(self):
        self.data.override_inputs(deepcopy(self._prepared_inputs))
        self.data.override_outputs(deepcopy(self._prepared_outputs))


class SubProcess(Activity):
    def __init__(self, id, pipeline, name=None):
        super(SubProcess, self).__init__(id, name, pipeline.data)
        self.pipeline = pipeline
        self._prepared_inputs = self.pipeline.data.inputs_copy()
        self._prepared_outputs = self.pipeline.data.outputs_copy()

    def prepare_rerun_data(self):
        self.data.override_inputs(deepcopy(self._prepared_inputs))
        self.data.override_outputs(deepcopy(self._prepared_outputs))


class Service(object):
    __metaclass__ = ABCMeta

    ScheduleResultAttr = '__schedule_finish__'
    ScheduleDetermineAttr = '__need_schedule__'
    OutputItem = namedtuple('OutputItem', 'name key type')
    interval = None
    _result_output = OutputItem(name=_(u'执行结果'), key='_result', type='bool')

    def __init__(self, name=None):
        self.name = name

    @abstractmethod
    def execute(self, data, parent_data):
        # get params from data
        pass

    @abstractmethod
    def outputs_format(self):
        pass

    def outputs(self):
        custom_format = self.outputs_format()
        assert isinstance(custom_format, list)
        custom_format.append(self._result_output)
        return custom_format

    def need_schedule(self):
        return getattr(self, Service.ScheduleDetermineAttr, False)

    def schedule(self, data, parent_data, callback_data=None):
        return True

    def finish_schedule(self):
        setattr(self, self.ScheduleResultAttr, True)

    def is_schedule_finished(self):
        return getattr(self, self.ScheduleResultAttr, False)

    def __getstate__(self):
        if 'logger' in self.__dict__:
            del self.__dict__['logger']
        return self.__dict__

    def clean_status(self):
        setattr(self, self.ScheduleResultAttr, False)


class AbstractIntervalGenerator(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1


class DefaultIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super(DefaultIntervalGenerator, self).next()
        return self.count ** 2


class NullIntervalGenerator(AbstractIntervalGenerator):
    pass


class StaticIntervalGenerator(AbstractIntervalGenerator):
    def __init__(self, interval):
        super(StaticIntervalGenerator, self).__init__()
        self.interval = interval

    def next(self):
        super(StaticIntervalGenerator, self).next()
        return self.interval

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

from abc import ABCMeta
from pipeline.core.flow.base import FlowNode


class Event(FlowNode):
    __metaclass__ = ABCMeta

    def __init__(self, id, name=None, data=None):
        super(Event, self).__init__(id, name, data)

    def next(self):
        return self.outgoing.unique_one().target


class ThrowEvent(Event):
    __metaclass__ = ABCMeta


class CatchEvent(Event):
    __metaclass__ = ABCMeta


class EndEvent(ThrowEvent):
    __metaclass__ = ABCMeta

    def pipeline_finish(self, root_pipeline_id):
        return


class StartEvent(CatchEvent):
    __metaclass__ = ABCMeta


class EmptyStartEvent(StartEvent):
    pass


class EmptyEndEvent(EndEvent):
    def pipeline_finish(self, root_pipeline_id):
        from pipeline.models import PipelineInstance  # noqa
        try:
            PipelineInstance.objects.set_finished(root_pipeline_id)
        except PipelineInstance.DoesNotExist:  # task which do not belong to any instance
            pass

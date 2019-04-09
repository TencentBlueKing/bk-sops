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

import json
from abc import ABCMeta

from pipeline.core.flow.base import FlowNode
from pipeline.core.data.expression import ConstantTemplate, deformat_constant_key
from pipeline.exceptions import (
    InvalidOperationException,
    ConditionExhaustedException,
    EvaluationException
)
from pipeline.utils.boolrule import BoolRule


class Gateway(FlowNode):
    __metaclass__ = ABCMeta


class ExclusiveGateway(Gateway):
    def __init__(self, id, conditions=None, name=None, data=None):
        super(ExclusiveGateway, self).__init__(id, name, data)
        self.conditions = conditions or []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def next(self, data=None):
        default_flow = self.outgoing.default_flow()
        next_flow = self._determine_next_flow_with_boolrule(data)

        if not next_flow:  # determine fail
            if not default_flow:  # try to use default flow
                raise ConditionExhaustedException('all conditions of branches are False '
                                                  'while default flow is not appointed')
            return default_flow.target

        return next_flow.target

    def target_for_sequence_flow(self, flow_id):
        flow_to_target = {c.sequence_flow.id: c.sequence_flow.target for c in self.conditions}
        if flow_id not in flow_to_target:
            raise InvalidOperationException('sequence flow(%s) does not exist.' % flow_id)
        return flow_to_target[flow_id]

    def _determine_next_flow_with_boolrule(self, data):
        """
        根据当前传入的数据判断下一个应该流向的 flow （ 不使用 eval 的版本）
        :param data:
        :return:
        """
        for condition in self.conditions:
            deformatted_data = {deformat_constant_key(key): value for key, value in data.items()}
            try:
                resolved_evaluate = ConstantTemplate(condition.evaluate).resolve_data(deformatted_data)
                result = BoolRule(resolved_evaluate).test(data)
            except Exception as e:
                raise EvaluationException(
                    'evaluate[%s] fail with data[%s] message: %s' % (
                        condition.evaluate,
                        json.dumps(deformatted_data),
                        e.message
                    )
                )
            if result:
                return condition.sequence_flow

        return None

    def skip(self):
        return True


class ParallelGateway(Gateway):
    def __init__(self, id, converge_gateway_id, name=None, data=None):
        super(ParallelGateway, self).__init__(id, name, data)
        self.converge_gateway_id = converge_gateway_id

    def next(self):
        raise InvalidOperationException('can not determine next node for parallel gateway.')


class ConditionalParallelGateway(Gateway):
    def __init__(self, id, converge_gateway_id, conditions=None, name=None, data=None):
        super(ConditionalParallelGateway, self).__init__(id, name, data)
        self.converge_gateway_id = converge_gateway_id
        self.conditions = conditions or []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def targets_meet_condition(self, data):

        targets = []

        for condition in self.conditions:
            deformatted_data = {deformat_constant_key(key): value for key, value in data.items()}
            try:
                resolved_evaluate = ConstantTemplate(condition.evaluate).resolve_data(deformatted_data)
                result = BoolRule(resolved_evaluate).test(data)
            except Exception as e:
                raise EvaluationException(
                    'evaluate[%s] fail with data[%s] message: %s' % (
                        condition.evaluate,
                        json.dumps(deformatted_data),
                        e.message
                    )
                )
            if result:
                targets.append(condition.sequence_flow.target)

        if not targets:
            raise ConditionExhaustedException('all conditions of branches are False')

        return targets

    def next(self):
        raise InvalidOperationException('can not determine next node for conditional parallel gateway.')

    def skip(self):
        raise InvalidOperationException('can not skip conditional parallel gateway.')


class ConvergeGateway(Gateway):
    def next(self):
        return self.outgoing.unique_one().target

    def skip(self):
        raise InvalidOperationException('can not skip conditional converge gateway.')


class Condition(object):
    def __init__(self, evaluate, sequence_flow):
        self.evaluate = evaluate
        self.sequence_flow = sequence_flow

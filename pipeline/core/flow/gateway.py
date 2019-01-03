# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
from abc import ABCMeta

from pipeline.core.flow.base import FlowNode
from pipeline.core.data.expression import ConstantTemplate, deformat_constant_key
from pipeline.exceptions import (InvalidOperationException, ConditionExhaustedException, EvaluationException,
                                 SourceKeyException)
from pipeline.utils.boolrule import BoolRule


class Gateway(FlowNode):
    __metaclass__ = ABCMeta


class ExclusiveGateway(Gateway):
    def __init__(self, id, conditions=None, name=None, data=None, data_source=None):
        super(ExclusiveGateway, self).__init__(id, name, data)
        self.conditions = conditions or []
        self.data_source = data_source

    def add_condition(self, condition):
        self.conditions.append(condition)

    def next(self, data=None):
        self.logger.error('from exg')
        default_flow = self.outgoing.default_flow()

        try:
            next_flow = self._determine_next_flow_with_boolrule(data)
        except:
            raise

        if not next_flow:  # determine fail
            if not default_flow:  # try to use default flow
                raise ConditionExhaustedException('default flow is not appointed when data is exhausted.')
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
            try:
                deformatted_data = {deformat_constant_key(key): value for key, value in data.items()}
                resolved_evaluate = ConstantTemplate(condition.evaluate).resolve_data(deformatted_data)
                result = BoolRule(resolved_evaluate).test(data)
            except Exception as e:
                raise EvaluationException('evaluate[%s] fail with data[%s] message: %s' % (condition.evaluate,
                                                                                           json.dumps(data),
                                                                                           e.message))
            if result:
                return condition.sequence_flow

        return None

    def _determine_next_flow(self, data):
        """
        根据当前传入的数据判断下一个应该流向的 flow
        :param data:
        :return:
        """
        for condition in self.conditions:
            try:
                local = {'result': eval(condition.source_key, {}, {'data': data.get_outputs()})}
            except KeyError:
                raise SourceKeyException('%s does not exist in %s' % (condition.source_key, data.get_outputs()))

            try:
                result = eval(condition.evaluate, {}, local)
            except Exception as e:
                raise EvaluationException('%s fail with message: %s' % (condition.evaluate, e.message))
            if result:
                return condition.sequence_flow

        return None


class ParallelGateway(Gateway):
    def __init__(self, id, converge_gateway_id, name=None, data=None):
        super(ParallelGateway, self).__init__(id, name, data)
        self.converge_gateway_id = converge_gateway_id

    def next(self):
        raise InvalidOperationException('can not determine next node for parallel gateway.')


class ConvergeGateway(Gateway):
    def next(self):
        return self.outgoing.unique_one().target


class Condition(object):
    def __init__(self, evaluate, sequence_flow):
        self.evaluate = evaluate
        self.sequence_flow = sequence_flow

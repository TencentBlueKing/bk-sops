# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import abc
import six

from .constants import OP


@six.add_metaclass(abc.ABCMeta)
class Operator(object):
    def __init__(self, op):
        self.op = op

    @abc.abstractmethod
    def expr(self):
        pass

    def __repr__(self):
        return "operator:{}".format(self.op)


@six.add_metaclass(abc.ABCMeta)
class LogicalOperator(Operator):
    def __init__(self, op, content):
        super(LogicalOperator, self).__init__(op)

        # TODO: valid the content, should be list
        self.content = content

    def expr(self):
        separator = " %s " % self.op
        return "(%s)" % separator.join([c.expr() for c in self.content])

    def render(self, obj_set):
        separator = " %s " % self.op
        return "(%s)" % separator.join([c.render(obj_set) for c in self.content])

    @abc.abstractmethod
    def eval(self, obj_set):
        pass

    # TODO: expr with values, should change
    # @abc.abstractmethod
    # def expr_translate()


class AndOperator(LogicalOperator):
    def __init__(self, content):
        super(AndOperator, self).__init__(OP.AND, content)

    def eval(self, obj_set):
        # return all([c.eval(obj_set) for c in self.content])
        # Short-circuit evaluation
        for c in self.content:
            if not c.eval(obj_set):
                return False
        return True


class OrOperator(LogicalOperator):
    def __init__(self, content):
        super(OrOperator, self).__init__(OP.OR, content)

    def eval(self, obj_set):
        # return any([c.eval(obj_set) for c in self.content])
        # Short-circuit evaluation
        for c in self.content:
            if c.eval(obj_set):
                return True
        return False


@six.add_metaclass(abc.ABCMeta)
class BinaryOperator(Operator):
    def __init__(self, op, field, value):
        super(BinaryOperator, self).__init__(op)
        self.field = field
        self.value = value

    def render(self, obj_set):
        value = self.value
        if isinstance(self.value, six.string_types):
            value = "'%s'" % self.value

        attr = obj_set.get(self.field)
        if isinstance(attr, six.string_types):
            attr = "'%s'" % attr

        return "(%s %s %s)" % (attr, self.op, value)

    def expr(self):
        value = self.value
        if isinstance(self.value, six.string_types):
            value = "'%s'" % self.value

        return "(%s %s %s)" % (self.field, self.op, value)

    @abc.abstractmethod
    def calculate(self, left, right):
        pass

    def _eval_positive(self, attr, attr_is_array, value, value_is_array):  # NOQA
        """
        positive:
        - 1   hit: return True
        - all miss: return False

        e.g.
        op = eq => one of attr equals one of value

        attr = 1; value = 1; True
        attr = 1; value = [1, 2]; True
        attr = [1, 2]; value = 2; True
        attr = [1, 2]; value = [5, 1]; True

        attr = [1, 2]; value = [3, 4]; False
        """
        if self.op == OP.ANY:
            return self.calculate(attr, value)

        # 1. IN/NOT_IN value is a list, just only check attr
        if self.op in (OP.IN,):
            if attr_is_array:
                for a in attr:
                    if self.calculate(a, value):
                        return True
                return False

            return self.calculate(attr, value)

        # 2. CONTAINS/NOT_CONTAINS attr is a list, just check value
        if self.op in (OP.CONTAINS,):
            if value_is_array:
                for v in value:
                    if self.calculate(attr, v):
                        return True
                return False

            return self.calculate(attr, value)

        # 3. Others, check both attr and value
        # 3.1 both not array, the most common situation
        if not (value_is_array or attr_is_array):
            return self.calculate(attr, value)

        # 3.2 only value is array, the second common situation
        if value_is_array and (not attr_is_array):
            for v in value:
                # return early if hit
                if self.calculate(attr, v):
                    return True
            return False

        # 3.3 only attr value is array
        if (not value_is_array) and attr_is_array:
            for a in attr:
                # return early if hit
                if self.calculate(a, value):
                    return True
            return False

        # 4. both array
        for a in attr:
            for v in value:
                # return early if hit
                if self.calculate(a, v):
                    return True
        return False

    def _eval_negative(self, attr, attr_is_array, value, value_is_array):  # NOQA
        """
        negative:
        - 1   miss: return False
        - all hit: return True

        e.g.
        op = not_eq => all of attr should not_eq to all of the value

        attr = 1; value = 2; True
        attr = 1; value = [2]; True
        attr = [1, 2]; value = [3, 4]; True
        attr = [1, 2]; value = 3; True

        attr = [1, 2]; value = [2, 3]; False
        """
        # 1. IN/NOT_IN value is a list, just only check attr
        if self.op in (OP.NOT_IN,):
            if attr_is_array:
                for a in attr:
                    if not self.calculate(a, value):
                        return False
                return True

            return self.calculate(attr, value)

        # 2. CONTAINS/NOT_CONTAINS attr is a list, just check value
        if self.op in (OP.NOT_CONTAINS,):
            if value_is_array:
                for v in value:
                    if not self.calculate(attr, v):
                        return False
                return True

            return self.calculate(attr, value)

        # 3. Others, check both attr and value
        # 3.1 both not array, the most common situation
        if not (value_is_array or attr_is_array):
            return self.calculate(attr, value)

        # 3.2 only value is array, the second common situation
        if value_is_array and (not attr_is_array):
            for v in value:
                if not self.calculate(attr, v):
                    return False
            return True

        # 3.3 only attr value is array
        if (not value_is_array) and attr_is_array:
            for a in attr:
                if not self.calculate(a, value):
                    return False
            return True

        # 4. both array
        for a in attr:
            for v in value:
                # return early if hit
                if not self.calculate(a, v):
                    return False
        return True

    def eval(self, obj_set):
        """
        type: str/numberic/boolean
        the value support `type` or `[type]`
        the obj_set.get(self.field) support `type` or `[type]`

        if one of them is array, or both array
        calculate each item in array
        """
        attr = obj_set.get(self.field)
        value = self.value

        attr_is_array = isinstance(attr, (list, tuple))
        value_is_array = isinstance(value, (list, tuple))

        # positive and negative operator
        # ==  命中一个即返回
        # !=  需要全部遍历完, 确认全部不等于才返回?
        if self.op.startswith("not_"):
            return self._eval_negative(attr, attr_is_array, value, value_is_array)
        else:
            return self._eval_positive(attr, attr_is_array, value, value_is_array)


class EqualOperator(BinaryOperator):
    def __init__(self, field, value):
        super(EqualOperator, self).__init__(OP.EQ, field, value)

    def calculate(self, left, right):
        return left == right


class NotEqualOperator(BinaryOperator):
    def __init__(self, field, value):
        super(NotEqualOperator, self).__init__(OP.NOT_EQ, field, value)

    def calculate(self, left, right):
        return left != right


class InOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be list or string(sequence?)
        super(InOperator, self).__init__(OP.IN, field, value)

    def calculate(self, left, right):
        return left in right


class NotInOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be list or string(sequence?)
        super(NotInOperator, self).__init__(OP.NOT_IN, field, value)

    def calculate(self, left, right):
        return left not in right


class ContainsOperator(BinaryOperator):
    def __init__(self, field, value):
        super(ContainsOperator, self).__init__(OP.CONTAINS, field, value)

    def calculate(self, left, right):
        return right in left


class NotContainsOperator(BinaryOperator):
    def __init__(self, field, value):
        super(NotContainsOperator, self).__init__(OP.NOT_CONTAINS, field, value)

    def calculate(self, left, right):
        return right not in left


class StartsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be string?
        super(StartsWithOperator, self).__init__(OP.STARTS_WITH, field, value)

    def calculate(self, left, right):
        return left.startswith(right)


class NotStartsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be string?
        super(NotStartsWithOperator, self).__init__(OP.NOT_STARTS_WITH, field, value)

    def calculate(self, left, right):
        return not left.startswith(right)


class EndsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be string?
        super(EndsWithOperator, self).__init__(OP.ENDS_WITH, field, value)

    def calculate(self, left, right):
        return left.endswith(right)


class NotEndsWithOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: value should be string?
        super(NotEndsWithOperator, self).__init__(OP.NOT_ENDS_WITH, field, value)

    def calculate(self, left, right):
        return not left.endswith(right)


class LTOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(LTOperator, self).__init__(OP.LT, field, value)

    def calculate(self, left, right):
        return left < right


class LTEOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(LTEOperator, self).__init__(OP.LTE, field, value)

    def calculate(self, left, right):
        return left <= right


class GTOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(GTOperator, self).__init__(OP.GT, field, value)

    def calculate(self, left, right):
        return left > right


class GTEOperator(BinaryOperator):
    def __init__(self, field, value):
        # TODO: field / value should be numberic
        super(GTEOperator, self).__init__(OP.GTE, field, value)

    def calculate(self, left, right):
        return left >= right


class AnyOperator(BinaryOperator):
    def __init__(self, field, value):
        super(AnyOperator, self).__init__(OP.ANY, field, value)

    def calculate(self, left, right):
        return True


BINARY_OPERATORS = {
    OP.EQ: EqualOperator,
    OP.NOT_EQ: NotEqualOperator,
    OP.IN: InOperator,
    OP.NOT_IN: NotInOperator,
    OP.CONTAINS: ContainsOperator,
    OP.NOT_CONTAINS: NotContainsOperator,
    OP.STARTS_WITH: StartsWithOperator,
    OP.NOT_STARTS_WITH: NotStartsWithOperator,
    OP.ENDS_WITH: EndsWithOperator,
    OP.NOT_ENDS_WITH: NotEndsWithOperator,
    OP.LT: LTOperator,
    OP.LTE: LTEOperator,
    OP.GT: GTOperator,
    OP.GTE: GTEOperator,
    OP.ANY: AnyOperator,
}

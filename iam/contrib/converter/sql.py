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

import six

from iam import OP
from iam.eval.expression import field_value_convert
from .base import Converter


"""
convert the expression into sql where clause

FIXME:
- sql injection via value
- single quote `'` in the value string, sql syntax error
"""


class SQLConverter(Converter):
    def __init__(self, key_mapping=None):
        super(SQLConverter, self).__init__(key_mapping)

    def _to_str_present(self, value, wrap_str):
        if not wrap_str:
            return value

        # FIXME: current not support the value with single quote '
        if isinstance(value, six.string_types):
            return "'%s'" % value
        return value

    def _positive(self, fmt, left, right, wrap_str=True):
        """
        if right is an array, [1, 2, 3]
        should be
        (left == 1 OR left == 2 OR left == 3)
        (left LIKE '1%' OR left LIKE '2%' OR left LIKE '3%')
        """
        is_array = isinstance(right, (list, tuple))
        if is_array:
            condition = " OR ".join([fmt.format(left, self._to_str_present(i, wrap_str)) for i in right])
            return "({})".format(condition)

        return fmt.format(left, self._to_str_present(right, wrap_str))

    def _negative(self, fmt, left, right, wrap_str=True):
        """
        if right is an array, [1, 2, 3]
        should be
        (left != 1 AND left != 2 AND left != 3)
        (left NOT LIKE '1%' AND left NOT LIKE '2%' and left NOT LIKE '3%')
        """
        is_array = isinstance(right, (list, tuple))
        if is_array:
            condition = " AND ".join([fmt.format(left, self._to_str_present(i, wrap_str)) for i in right])
            return "({})".format(condition)

        return fmt.format(left, self._to_str_present(right, wrap_str))

    def _eq(self, left, right):
        return self._positive("{} == {}", left, right)

    def _not_eq(self, left, right):
        return self._negative("{} != {}", left, right)

    def _in(self, left, right):
        # TODO: right shuld be a list
        right = [self._to_str_present(r, True) for r in right]
        return "{} IN ({})".format(left, ",".join([str(r) for r in right]))

    def _not_in(self, left, right):
        # TODO: right shuld be a list
        right = [self._to_str_present(r, True) for r in right]
        return "{} NOT IN ({})".format(left, ",".join([str(r) for r in right]))

    def _contains(self, left, right):
        raise NotImplementedError

    def _not_contains(self, left, right):
        raise NotImplementedError

    def _starts_with(self, left, right):
        # FIXME: right with single quote, will fail
        return self._positive("{} LIKE '{}%'", left, right, False)

    def _not_starts_with(self, left, right):
        return self._negative("{} NOT LIKE '{}%'", left, right, False)

    def _ends_with(self, left, right):
        return self._positive("{} LIKE '%{}'", left, right, False)

    def _not_ends_with(self, left, right):
        return self._negative("{} NOT LIKE '%{}'", left, right, False)

    def _lt(self, left, right):
        return self._positive("{} < {}", left, right)

    def _lte(self, left, right):
        return self._positive("{} <= {}", left, right)

    def _gt(self, left, right):
        return self._positive("{} > {}", left, right)

    def _gte(self, left, right):
        return self._positive("{} >= {}", left, right)

    def _any(self, left, right):
        return "1 == 1"

    def _and(self, content):
        condition = " AND ".join([self.convert(c) for c in content])
        return "(%s)" % condition

    def _or(self, content):
        condition = " OR ".join([self.convert(c) for c in content])
        return "(%s)" % condition

    def convert(self, data):
        op = data["op"]

        if op == OP.AND:
            return self._and(data["content"])
        elif op == OP.OR:
            return self._or(data["content"])

        op_func = {
            OP.EQ: self._eq,
            OP.NOT_EQ: self._not_eq,
            OP.IN: self._in,
            OP.NOT_IN: self._not_in,
            OP.CONTAINS: self._contains,
            OP.NOT_CONTAINS: self._not_contains,
            OP.STARTS_WITH: self._starts_with,
            OP.NOT_STARTS_WITH: self._not_starts_with,
            OP.ENDS_WITH: self._ends_with,
            OP.NOT_ENDS_WITH: self._not_ends_with,
            OP.LT: self._lt,
            OP.LTE: self._lte,
            OP.GT: self._gt,
            OP.GTE: self._gte,
            OP.ANY: self._any,
        }.get(op)

        if op_func is None:
            raise ValueError("invalid op %s" % op)

        value = data["value"]
        field = data["field"]

        # 权限中心保留字预处理
        field, value = field_value_convert(op, field, value)

        if self.key_mapping and field in self.key_mapping:
            field = self.key_mapping.get(field)

        return op_func(field, value)

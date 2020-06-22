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

from .constants import OP, KEYWORD_BK_IAM_PATH_FIELD_SUFFIX
from .operators import AndOperator, OrOperator, BINARY_OPERATORS


def _parse_bk_iam_path(value):
    new_value = value
    # /biz,1/set,*/ -> /biz,1/set,
    # resource._bk_iam_path_ startswith /biz,1/set,
    if isinstance(value, six.string_types):
        if value.endswith(",*/"):
            new_value = value[:-2]
    elif isinstance(value, (list, tuple)):
        striped_value = []
        for v in value:
            if isinstance(v, six.string_types) and v.endswith(",*/"):
                striped_value.append(v[:-2])
            else:
                striped_value.append(v)

        new_value = striped_value
    else:
        pass

    return new_value


def field_value_convert(operator, field, value):
    if operator == OP.STARTS_WITH and field.endswith(KEYWORD_BK_IAM_PATH_FIELD_SUFFIX):
        value = _parse_bk_iam_path(value)
        return field, value
    # do nothing
    return field, value


def make_expression(data):
    op = data["op"]

    if op == OP.AND:
        return AndOperator([make_expression(c) for c in data["content"]])
    elif op == OP.OR:
        return OrOperator([make_expression(c) for c in data["content"]])

    if op not in BINARY_OPERATORS:
        raise ValueError("operator %s not supported" % op)

    operator = BINARY_OPERATORS[op]

    field = data["field"]
    value = data["value"]

    field, value = field_value_convert(op, field, value)

    return operator(field, value)

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

from .__version__ import __version__  # noqa

from .eval.object import DictObject, ObjectSet  # noqa
from .eval.constants import OP  # noqa
from .eval.expression import make_expression  # noqa
from .eval.operators import (  # noqa
    AndOperator,
    OrOperator,
    EqualOperator,
    NotEqualOperator,
    InOperator,
    NotInOperator,
    ContainsOperator,
    NotContainsOperator,
    StartsWithOperator,
    NotStartsWithOperator,
    EndsWithOperator,
    NotEndsWithOperator,
    LTOperator,
    LTEOperator,
    GTOperator,
    GTEOperator,
    AnyOperator,
    Operator,
    LogicalOperator,
    BinaryOperator,
)

from .contrib.converter.base import Converter  # noqa
from .contrib.converter.sql import SQLConverter  # noqa
from .contrib.converter.queryset import DjangoQuerySetConverter, PathEqDjangoQuerySetConverter  # noqa

from .auth.models import Subject, Action, Resource  # noqa
from .auth.models import Request, MultiActionRequest  # noqa

from .iam import IAM  # noqa

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())

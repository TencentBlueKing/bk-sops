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


class OP(object):
    """
    NOTE: don't want to use Enum
    """

    AND = "AND"
    OR = "OR"

    EQ = "eq"
    NOT_EQ = "not_eq"

    IN = "in"
    NOT_IN = "not_in"

    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"

    STARTS_WITH = "starts_with"
    NOT_STARTS_WITH = "not_starts_with"

    ENDS_WITH = "ends_with"
    NOT_ENDS_WITH = "not_ends_with"

    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"

    ANY = "any"

    ALLOWED_OPERATORS = {
        "string": [
            EQ,
            NOT_EQ,
            IN,
            NOT_IN,
            CONTAINS,
            NOT_CONTAINS,
            STARTS_WITH,
            NOT_STARTS_WITH,
            ENDS_WITH,
            NOT_ENDS_WITH,
            ANY,
        ],
        "numberic": [EQ, NOT_EQ, IN, NOT_IN, LT, LTE, GT, GTE],
        "boolean": [EQ, NOT_EQ, IN, NOT_IN],
    }


# iam keywords

KEYWORD_BK_IAM_PATH = "_bk_iam_path_"

KEYWORD_BK_IAM_PATH_FIELD_SUFFIX = ".%s" % KEYWORD_BK_IAM_PATH

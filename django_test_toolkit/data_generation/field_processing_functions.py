# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import random

from django_test_toolkit.data_generation.constants import (
    PROCESSING_CHAR_FIELD_DEFAULT_MIN_LENGTH,
    PROCESSING_CHAR_FIELD_DEFAULT_MAX_LENGTH,
)


def text_provider_char_field_processing(field):
    """获取字段的最大最小长度约束作为数据生成的参数，控制生成的text数据单词个数"""
    default = {
        "min_length": PROCESSING_CHAR_FIELD_DEFAULT_MIN_LENGTH,
        "max_length": PROCESSING_CHAR_FIELD_DEFAULT_MAX_LENGTH,
    }
    for validator in field.validators:
        if validator.code in ["min_length", "max_length"]:
            default[validator.code] = validator.limit_value
    return {"max_nb_chars": random.randint(default["min_length"], default["max_length"])}


def random_int_provider_integer_field_processing(field):
    """获取字段的最大最小值约束作为数据生成的参数，控制生成的int范围"""
    extra_kwargs = {}
    for validator in field.validators:
        if validator.code in ["min_value", "max_value"]:
            extra_kwargs[validator.code.replace("_value", "")] = validator.limit_value
    return extra_kwargs

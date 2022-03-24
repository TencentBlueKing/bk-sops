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
import pytz

from django_test_toolkit.data_generation.constants import (
    DEFAULT_RETRY_TOLERANCE,
    DEFAULT_DEFAULT_VALUE_FACTOR,
)
from django_test_toolkit.data_generation.field_processing_functions import (
    text_provider_char_field_processing,
    random_int_provider_integer_field_processing,
)


DEFAULT_FIELD_TO_FAKER_CONFIG = {
    "fields": {
        "CharField": {"provider": "text", "processing_func": text_provider_char_field_processing},
        "TextField": {"provider": "text"},
        "IntegerField": {"provider": "random_int", "processing_func": random_int_provider_integer_field_processing},
        "DateTimeField": {
            "provider": "date_time_this_month",
            "extra_kwargs": {"tzinfo": pytz.utc, "before_now": True},
        },
    },
    "default_value_factor": DEFAULT_DEFAULT_VALUE_FACTOR,
    "unique_field_duplicate_retry_tolerance": DEFAULT_RETRY_TOLERANCE,
}

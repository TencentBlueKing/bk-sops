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

# FIELD_TO_FAKER配置相关
FIELD_TO_FAKER_CONFIG = "field_to_faker_config"
FIELDS = "fields"
DEFAULT_VALUE_FACTOR = "default_value_factor"
FAKER_LOCALE = "faker_data_locale"
DEFAULT_DEFAULT_VALUE_FACTOR = 0.8
UNIQUE_FIELD_DUPLICATE_RETRY_TOLERANCE = "unique_field_duplicate_retry_tolerance"
DEFAULT_RETRY_TOLERANCE = 50

# FIELD配置相关
FIELD_PROCESSING_FUNC = "processing_func"
FIELD_PROVIDER = "provider"
USER_FIELD_PROVIDER = "user_provider_class"
FIELD_EXTRA_KWARGS = "extra_kwargs"

# Provider处理函数相关
PROCESSING_CHAR_FIELD_DEFAULT_MIN_LENGTH = 5
PROCESSING_CHAR_FIELD_DEFAULT_MAX_LENGTH = 100

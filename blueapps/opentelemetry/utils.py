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
from typing import Tuple


def inject_logging_trace_info(
    logging: dict, inject_formatters: Tuple[str], trace_format: str, format_keywords: Tuple[str] = ("format", "fmt")
):
    """往logging配置中动态注入trace信息，直接修改logging数据"""
    formatters = {name: formatter for name, formatter in logging["formatters"].items() if name in inject_formatters}
    for name, formatter in formatters.items():
        matched_keywords = set(format_keywords).intersection(set(formatter.keys()))
        for keyword in matched_keywords:
            formatter.update({keyword: formatter[keyword].strip() + f" {trace_format}\n"})

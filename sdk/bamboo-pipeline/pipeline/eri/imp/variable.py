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

from typing import Callable, Any, Type

from bamboo_engine.eri import Variable as VariableInterface

from pipeline.core.data.var import Variable


class VariableProxy:
    def __init__(self, orginal_value: Variable, get_value: Callable, pipeline_data: dict):
        self.get_value = get_value
        self.orginal_value = orginal_value
        self.pipeline_data = pipeline_data

    def get(self) -> Any:
        self.value = self.orginal_value.get()
        return self.get_value(self)


class VariableWrapper(VariableInterface):
    def __init__(self, orginal_value: Variable, var_cls: Type, additional_data: dict):
        self.var = VariableProxy(
            orginal_value=orginal_value, get_value=var_cls.get_value, pipeline_data=additional_data
        )

    def get(self) -> Any:
        return self.var.get()

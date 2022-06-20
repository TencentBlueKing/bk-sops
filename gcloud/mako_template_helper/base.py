# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import List

from gcloud.constants import Type


class MakoParam:
    def __init__(self, name: str, type: Type) -> None:
        self.name = name
        self.type = type

    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type.value}


class MakoOperator:
    def __init__(self, name: str, type: Type) -> None:
        self.name = name
        self.type = type

    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type.value}


class MakoTemplateOperation:
    def __init__(
        self, name: str, operators: List[MakoOperator], params: List[MakoParam], template: List[str], mako_template: str
    ) -> None:
        self.name = name
        self.operators = operators
        self.params = params
        self.template = template
        self.mako_template = mako_template

        self._validate()

    def _validate(self):
        operator_names = ["{%s}" % op.name for op in self.operators]
        param_names = ["{%s}" % param.name for param in self.params]

        if len(set(operator_names)) != len(operator_names):
            raise ValueError("MakoTemplateOperation %s found duplicate operator" % self.name)

        if len(set(param_names)) != len(param_names):
            raise ValueError("MakoTemplateOperation %s found duplicate param" % self.name)

        for names in [operator_names, param_names]:
            for n in names:
                if n not in " ".join(self.template):
                    raise ValueError("MakoTemplateOperation %s's operator %s miss in template" % (self.name, n))

                if n not in self.mako_template:
                    raise ValueError("MakoTemplateOperation %s's operator %s miss in mako_template" % (self.name, n))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "operators": [op.to_dict() for op in self.operators],
            "params": [param.to_dict() for param in self.params],
            "template": self.template,
            "mako_template": self.mako_template,
        }

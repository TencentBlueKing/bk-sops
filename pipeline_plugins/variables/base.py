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


class FieldExplain:
    def __init__(self, key: str, type: Type, description: str):
        self.key = key
        self.type = type
        self.description = description

    def to_dict(self):
        return {"key": self.key, "type": self.type.value, "description": self.description}


class SelfExplainVariable:
    @classmethod
    def self_explain(cls, **kwargs) -> dict:
        return {"tag": cls.tag, "fields": [field.to_dict() for field in cls._self_explain(**kwargs)]}

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        raise NotImplementedError()

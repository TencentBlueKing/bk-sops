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

from django.test import TestCase

from gcloud.constants import Type
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable


class BaseTaseCase(TestCase):
    def test_field_explain_to_dict(self):
        explain = FieldExplain(key="key", type=Type.STRING, description="desc")
        self.assertEqual(explain.to_dict(), {"key": "key", "type": "string", "description": "desc"})

    def test_self_explain(self):
        class Var(SelfExplainVariable):
            tag = "my_tag"

            @classmethod
            def _self_explain(cls, **kwargs):
                return [FieldExplain(key=kwargs["key"], type=Type.STRING, description="desc")]

        self.assertEqual(
            Var.self_explain(key="my_key"),
            {"tag": "my_tag", "fields": [{"key": "my_key", "type": "string", "description": "desc"}]},
        )

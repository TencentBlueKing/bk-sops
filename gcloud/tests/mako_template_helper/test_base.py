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
from gcloud.mako_template_helper.base import MakoParam, MakoOperator, MakoTemplateOperation


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.validate_op = MakoTemplateOperation(
            name="字符串分割后拼接",
            operators=[MakoOperator(name="caller", type=Type.STRING)],
            params=[MakoParam(name="split_string", type=Type.STRING), MakoParam(name="join_string", type=Type.STRING)],
            template=["将 {caller}", "以 {split_string} 分割后", "以 {join_string} 拼接"],
            mako_template='${"{join_string}".join({caller}.split("{split_string}"))}',
        )

    def test_mako_param_to_dict(self):
        param = MakoParam(name="name", type=Type.STRING)
        self.assertEqual(param.to_dict(), {"name": "name", "type": "string"})

    def test_mako_operator_to_dict(self):
        op = MakoOperator(name="name", type=Type.STRING)
        self.assertEqual(op.to_dict(), {"name": "name", "type": "string"})

    def test_mako_template_operation_to_dict(self):
        op = MakoTemplateOperation(
            name="字符串分割后拼接",
            operators=[MakoOperator(name="caller", type=Type.STRING)],
            params=[MakoParam(name="split_string", type=Type.STRING), MakoParam(name="join_string", type=Type.STRING)],
            template=["将 {caller}", "以 {split_string} 分割后", "以 {join_string} 拼接"],
            mako_template='${"{join_string}".join({caller}.split("{split_string}"))}',
        )
        self.assertEqual(
            op.to_dict(),
            {
                "name": "字符串分割后拼接",
                "operators": [{"name": "caller", "type": "string"}],
                "params": [{"name": "split_string", "type": "string"}, {"name": "join_string", "type": "string"}],
                "template": ["将 {caller}", "以 {split_string} 分割后", "以 {join_string} 拼接"],
                "mako_template": '${"{join_string}".join({caller}.split("{split_string}"))}',
            },
        )

    def test_mako_template_operation__validate__duplicate_operators(self):
        self.validate_op.operators = [
            MakoOperator(name="caller", type=Type.STRING),
            MakoOperator(name="caller", type=Type.STRING),
        ]
        try:
            self.validate_op._validate()
        except ValueError as e:
            self.assertEqual(str(e), "MakoTemplateOperation 字符串分割后拼接 found duplicate operator")

    def test_mako_template_operation__validate__duplicate_params(self):
        self.validate_op.params = [
            MakoParam(name="split_string", type=Type.STRING),
            MakoParam(name="split_string", type=Type.STRING),
        ]
        try:
            self.validate_op._validate()
        except ValueError as e:
            self.assertEqual(str(e), "MakoTemplateOperation 字符串分割后拼接 found duplicate param")

    def test_mako_template_operation__validate__operator_not_exist_in_template(self):
        self.validate_op.operators = [MakoOperator(name="not_exist", type=Type.STRING)]
        try:
            self.validate_op._validate()
        except ValueError as e:
            self.assertEqual(str(e), "MakoTemplateOperation 字符串分割后拼接's operator {not_exist} miss in template")

    def test_mako_template_operation__validate__param_not_exist_in_template(self):
        self.validate_op.params = [MakoParam(name="not_exist", type=Type.STRING)]

        try:
            self.validate_op._validate()
        except ValueError as e:
            self.assertEqual(str(e), "MakoTemplateOperation 字符串分割后拼接's operator {not_exist} miss in template")

    def test_mako_template_operation__validate__operator_not_exist_in_makio_template(self):
        self.validate_op.operators = [MakoOperator(name="not_exist", type=Type.STRING)]
        self.validate_op.template = ["{not_exist} template"]

        try:
            self.validate_op._validate()
        except ValueError as e:
            self.assertEqual(str(e), "MakoTemplateOperation 字符串分割后拼接's operator {not_exist} miss in mako_template")

    def test_mako_template_operation__validate__param_not_exist_in_makio_template(self):
        self.validate_op.params = [MakoParam(name="not_exist", type=Type.STRING)]
        self.validate_op.template = ["{caller} {not_exist} template"]

        try:
            self.validate_op._validate()
        except ValueError as e:
            self.assertEqual(str(e), "MakoTemplateOperation 字符串分割后拼接's operator {not_exist} miss in mako_template")

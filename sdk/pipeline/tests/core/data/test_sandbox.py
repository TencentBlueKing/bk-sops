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

from django.test import TestCase

from pipeline.core.data import sandbox


def _test(*arg, **kwargs):
    return "called"


class TestSandbox(TestCase):
    def test_mock_str_meta(self):
        class MockTest(metaclass=sandbox.MockStrMeta):
            call = _test
            str_return = "_test"

        print(sandbox.SANDBOX["_test"])
        self.assertEqual(sandbox.SANDBOX["_test"], MockTest)

        self.assertEqual(MockTest(), "called")

    def test_shield_words(self):
        _sandbox = {}
        sandbox._shield_words(_sandbox, ["compile", "exec"])
        self.assertDictEqual(_sandbox, {"compile": None, "exec": None})

    def test_import_modules(self):
        _sandbox = {}
        sandbox._import_modules(_sandbox, {"datetime": "datetime", "pipeline.core": "core"})
        self.assertEqual(type(_sandbox["datetime"]).__name__, "module")
        self.assertEqual(type(_sandbox["core"]).__name__, "module")

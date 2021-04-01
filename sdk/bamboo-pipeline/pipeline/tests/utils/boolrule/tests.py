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

from pipeline.utils.boolrule import BoolRule


class BoolRuleTests(TestCase):
    def test_eq(self):
        self.assertTrue(BoolRule("1 == 1").test())
        self.assertTrue(BoolRule('"1" == 1').test())

        self.assertTrue(BoolRule("True == true").test())
        self.assertTrue(BoolRule("False == false").test())

        self.assertTrue(BoolRule("1 == True").test())
        self.assertTrue(BoolRule("0 == False").test())
        self.assertTrue(BoolRule('"1" == True').test())
        self.assertTrue(BoolRule('"0" == False').test())
        self.assertTrue(BoolRule('"3.14" == 3.14').test())

        self.assertTrue(BoolRule('"abc" == "abc"').test())

        self.assertFalse(BoolRule("1 == 2").test())
        self.assertFalse(BoolRule('123 == "123a"').test())
        self.assertFalse(BoolRule('1 == "2"').test())

        self.assertFalse(BoolRule('True == "true"').test())
        self.assertFalse(BoolRule('False == "false"').test())

    def test_ne(self):
        self.assertTrue(BoolRule("1 != 2").test())
        self.assertTrue(BoolRule('"1" != 2').test())

        self.assertTrue(BoolRule('True != "true"').test())

        self.assertTrue(BoolRule('"abc" != "cba"').test())

        self.assertFalse(BoolRule("1 != 1").test())

    def test_gt(self):
        self.assertTrue(BoolRule("2 > 1").test())
        self.assertTrue(BoolRule('"2" > 1').test())

        self.assertFalse(BoolRule("1 > 2").test())
        self.assertFalse(BoolRule('"1" > 2').test())

    def test_lt(self):
        self.assertTrue(BoolRule("1 < 2").test())
        self.assertTrue(BoolRule('"1" < 2').test())

        self.assertFalse(BoolRule("2 < 1").test())
        self.assertFalse(BoolRule("2 < 2").test())

    def test_in(self):
        self.assertTrue(BoolRule("1 in (1, 2)").test())
        self.assertTrue(BoolRule('1 in ("1", "2")').test())
        self.assertTrue(BoolRule('"1" in (1, 2)').test())
        self.assertTrue(BoolRule('"1" in ("1", "2")').test())

        self.assertFalse(BoolRule("1 in (0, 2)").test())
        self.assertFalse(BoolRule('1 in ("11", 2)').test())

    def test_notin(self):
        self.assertTrue(BoolRule("1 notin (0, 2)").test())
        self.assertTrue(BoolRule('1 notin ("0", "2")').test())
        self.assertTrue(BoolRule('"abc" notin (0, 2)').test())

    def test_and(self):
        self.assertTrue(BoolRule("1 < 2 and 2 < 3").test())
        self.assertTrue(BoolRule('"a" < "s" and 2 < 3').test())

        self.assertFalse(BoolRule("1 > 2 and 2 > 1").test())
        self.assertFalse(BoolRule("2 > 1 and 1 > 2").test())
        self.assertFalse(BoolRule("2 > 1 and 1 > 2").test())
        self.assertFalse(BoolRule('"s" > "s" and 2 < 3').test())
        self.assertFalse(BoolRule('"s" < "s" and 2 < 3').test())

    def test_or(self):
        self.assertTrue(BoolRule("1 < 2 or 2 < 3").test())
        self.assertTrue(BoolRule("1 < 2 or 2 < 1").test())
        self.assertTrue(BoolRule("1 > 2 or 2 > 1").test())
        self.assertTrue(BoolRule('"s" > "s" or "su" > "st"').test())

        self.assertFalse(BoolRule("1 > 2 or 2 > 3").test())
        self.assertFalse(BoolRule('"a" > "s" or "s" > "st"').test())

    def test_context(self):
        context = {"${v1}": 1, "${v2}": "1"}
        self.assertTrue(BoolRule("${v1} == ${v2}").test(context))
        self.assertTrue(BoolRule("${v1} == 1").test(context))
        self.assertTrue(BoolRule('${v1} == "1"').test(context))
        self.assertTrue(BoolRule('${v2} == "1"').test(context))
        self.assertTrue(BoolRule('${v2} == "1"').test(context))

        self.assertTrue(BoolRule('${v1} in ("1")').test(context))

    def test_gt_or_equal(self):
        context = {"${v1}": 1, "${v2}": "1"}
        self.assertTrue(BoolRule("${v1} >= ${v2}").test(context))
        self.assertTrue(BoolRule("${v1} >= 1").test(context))
        self.assertTrue(BoolRule('${v1} >= "1"').test(context))
        self.assertTrue(BoolRule("${v1} >= 0").test(context))
        self.assertTrue(BoolRule('${v1} >= "0"').test(context))

        # self.assertTrue(BoolRule('${v1} >= 2').test(context))
        self.assertFalse(BoolRule('${v2} >= "2"').test(context))

    def test_lt_or_equal(self):
        context = {"${v1}": 1, "${v2}": "1"}
        self.assertTrue(BoolRule("${v1} <= ${v2}").test(context))
        self.assertTrue(BoolRule("${v1} <= 1").test(context))
        self.assertTrue(BoolRule('${v1} <= "2"').test(context))
        self.assertTrue(BoolRule('${v1} <= "123456789111"').test(context))
        self.assertTrue(BoolRule("${v1} <= 123456789111").test(context))
        self.assertFalse(BoolRule("${v1} <= 0").test(context))
        self.assertFalse(BoolRule('${v1} <= "0"').test(context))
        self.assertTrue(BoolRule('"a" <= "b"').test(context))
        self.assertFalse(BoolRule('"a" <= "49"').test(context))

    def test_true_equal(self):
        context = {"${v1}": True, "${v2}": "True"}
        # 下面的表达式测试不符合预期
        # self.assertTrue(BoolRule('${v1} == ${v2}').test(context))
        self.assertTrue(BoolRule("${v1} == True").test(context))
        self.assertTrue(BoolRule("${v1} == true").test(context))
        self.assertTrue(BoolRule("${v1} == ${v1}").test(context))
        self.assertTrue(BoolRule("${v1} == 1").test(context))
        self.assertTrue(BoolRule('${v1} == "1"').test(context))

        self.assertFalse(BoolRule('${v1} == "s"').test(context))
        self.assertFalse(BoolRule("${v1} == 0").test(context))
        self.assertFalse(BoolRule('${v1} == "0"').test(context))
        self.assertFalse(BoolRule("${v1} == false").test(context))
        self.assertFalse(BoolRule("${v1} == False").test(context))
        self.assertFalse(BoolRule('${v1} == "false"').test(context))
        self.assertFalse(BoolRule('${v1} == "False"').test(context))

    def test_false_equal(self):
        context = {"${v1}": False, "${v2}": "False"}
        # 下面的表达式测试不符合预期
        # self.assertTrue(BoolRule('${v1} == "False"').test(context))
        self.assertTrue(BoolRule("${v1} == ${v1}").test(context))
        self.assertTrue(BoolRule("${v1} == false").test(context))
        self.assertTrue(BoolRule("${v1} == False").test(context))
        self.assertTrue(BoolRule('${v1} == "0"').test(context))
        self.assertTrue(BoolRule("${v1} == 0").test(context))
        self.assertTrue(BoolRule('${v1} == "0"').test(context))

        self.assertFalse(BoolRule('${v1} == "1"').test(context))
        self.assertFalse(BoolRule("${v1} == true").test(context))
        self.assertFalse(BoolRule('${v1} == "true"').test(context))
        self.assertFalse(BoolRule("${v1} == True").test(context))
        self.assertFalse(BoolRule('${v1} == "True"').test(context))
        self.assertFalse(BoolRule('${v1} == "s"').test(context))

    def test_multi_or(self):
        self.assertTrue(BoolRule('("s" > "s" or "su" > "st") or (1 > 3 and 2 < 3)').test())
        self.assertTrue(BoolRule('(1 > 3 and 2 < 3)  or ("s" > "s" or "su" > "st")').test())
        self.assertTrue(BoolRule('(1 < 3 and 2 < 3)  or ("s" > "s" or "su" > "st")').test())
        self.assertTrue(BoolRule('(1 > 2 or 2 > 3) or ("s" > "s" or "su" > "st") or (4  > 5 and 5 < 6)').test())

        self.assertFalse(BoolRule('(1 > 2 or 2 > 3) or ("s" > "s" or "su" < "st")').test())
        self.assertFalse(BoolRule('(1 > 2 or 2 > 3) or ("s" > "s" or "su" < "st") or (4  > 5 and 5 < 6)').test())

    def test_multi_and(self):
        self.assertTrue(BoolRule('("s" > "s" or "su" > "st") and (1 < 3 and 2 < 3)').test())

        self.assertFalse(BoolRule('(1 < 2 or 2 > 3) and ("s" > "s" or "su" < "st")').test())
        self.assertFalse(BoolRule('(1 > 2 or 2 > 3) and ("s" > "s" or "su" > "st")').test())
        self.assertFalse(BoolRule('(1 > 2 or 2 > 3) and ("s" > "s" or "su" < "st")').test())
        self.assertFalse(BoolRule('(1 < 3 and 2 < 3)  and ("s" > "s" or "su" > "st") and (4 > 5 and 5 < 6)').test())

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

from bamboo_engine.utils.boolrule.boolrule import BoolRule


def test_eq():
    assert BoolRule("1 == 1").test() == True
    assert BoolRule('"1" == 1').test() == True

    assert BoolRule("True == true").test() == True
    assert BoolRule("False == false").test() == True

    assert BoolRule("1 == True").test() == True
    assert BoolRule("0 == False").test() == True
    assert BoolRule('"1" == True').test() == True
    assert BoolRule('"0" == False').test() == True
    assert BoolRule('"3.14" == 3.14').test() == True

    assert BoolRule('"abc" == "abc"').test() == True

    assert BoolRule("1 == 2").test() == False
    assert BoolRule('123 == "123a"').test() == False
    assert BoolRule('1 == "2"').test() == False

    assert BoolRule('True == "true"').test() == False
    assert BoolRule('False == "false"').test() == False


def test_ne():
    assert BoolRule("1 != 2").test() == True
    assert BoolRule('"1" != 2').test() == True

    assert BoolRule('True != "true"').test() == True

    assert BoolRule('"abc" != "cba"').test() == True

    assert BoolRule("1 != 1").test() == False


def test_gt():
    assert BoolRule("2 > 1").test() == True
    assert BoolRule('"2" > 1').test() == True

    assert BoolRule("1 > 2").test() == False
    assert BoolRule('"1" > 2').test() == False


def test_lt():
    assert BoolRule("1 < 2").test() == True
    assert BoolRule('"1" < 2').test() == True

    assert BoolRule("2 < 1").test() == False
    assert BoolRule("2 < 2").test() == False


def test_in():
    assert BoolRule("1 in (1, 2)").test() == True
    assert BoolRule('1 in ("1", "2")').test() == True
    assert BoolRule('"1" in (1, 2)').test() == True
    assert BoolRule('"1" in ("1", "2")').test() == True

    assert BoolRule("1 in (0, 2)").test() == False
    assert BoolRule('1 in ("11", 2)').test() == False


def test_notin():
    assert BoolRule("1 notin (0, 2)").test() == True
    assert BoolRule('1 notin ("0", "2")').test() == True
    assert BoolRule('"abc" notin (0, 2)').test() == True


def test_and():
    assert BoolRule("1 < 2 and 2 < 3").test() == True
    assert BoolRule('"a" < "s" and 2 < 3').test() == True

    assert BoolRule("1 > 2 and 2 > 1").test() == False
    assert BoolRule("2 > 1 and 1 > 2").test() == False
    assert BoolRule("2 > 1 and 1 > 2").test() == False
    assert BoolRule('"s" > "s" and 2 < 3').test() == False
    assert BoolRule('"s" < "s" and 2 < 3').test() == False


def test_or():
    assert BoolRule("1 < 2 or 2 < 3").test() == True
    assert BoolRule("1 < 2 or 2 < 1").test() == True
    assert BoolRule("1 > 2 or 2 > 1").test() == True
    assert BoolRule('"s" > "s" or "su" > "st"').test() == True

    assert BoolRule("1 > 2 or 2 > 3").test() == False
    assert BoolRule('"a" > "s" or "s" > "st"').test() == False


def test_context():
    context = {"${v1}": 1, "${v2}": "1"}
    assert BoolRule("${v1} == ${v2}").test(context) == True
    assert BoolRule("${v1} == 1").test(context) == True
    assert BoolRule('${v1} == "1"').test(context) == True
    assert BoolRule('${v2} == "1"').test(context) == True
    assert BoolRule('${v2} == "1"').test(context) == True

    assert BoolRule('${v1} in ("1")').test(context) == True


def test_gt_or_equal():
    context = {"${v1}": 1, "${v2}": "1"}
    assert BoolRule("${v1} >= ${v2}").test(context) == True
    assert BoolRule("${v1} >= 1").test(context) == True
    assert BoolRule('${v1} >= "1"').test(context) == True
    assert BoolRule("${v1} >= 0").test(context) == True
    assert BoolRule('${v1} >= "0"').test(context) == True

    # assert BoolRule('${v1} >= 2').test(context) == True
    assert BoolRule('${v2} >= "2"').test(context) == False


def test_lt_or_equal():
    context = {"${v1}": 1, "${v2}": "1"}
    assert BoolRule("${v1} <= ${v2}").test(context) == True
    assert BoolRule("${v1} <= 1").test(context) == True
    assert BoolRule('${v1} <= "2"').test(context) == True
    assert BoolRule('${v1} <= "123456789111"').test(context) == True
    assert BoolRule("${v1} <= 123456789111").test(context) == True
    assert BoolRule("${v1} <= 0").test(context) == False
    assert BoolRule('${v1} <= "0"').test(context) == False
    assert BoolRule('"a" <= "b"').test(context) == True
    assert BoolRule('"a" <= "49"').test(context) == False


def test_true_equal():
    context = {"${v1}": True, "${v2}": "True"}
    # 下面的表达式测试不符合预期
    # assert BoolRule('${v1} == ${v2}').test(context) == True
    assert BoolRule("${v1} == True").test(context) == True
    assert BoolRule("${v1} == true").test(context) == True
    assert BoolRule("${v1} == ${v1}").test(context) == True
    assert BoolRule("${v1} == 1").test(context) == True
    assert BoolRule('${v1} == "1"').test(context) == True

    assert BoolRule('${v1} == "s"').test(context) == False
    assert BoolRule("${v1} == 0").test(context) == False
    assert BoolRule('${v1} == "0"').test(context) == False
    assert BoolRule("${v1} == false").test(context) == False
    assert BoolRule("${v1} == False").test(context) == False
    assert BoolRule('${v1} == "false"').test(context) == False
    assert BoolRule('${v1} == "False"').test(context) == False


def test_false_equal():
    context = {"${v1}": False, "${v2}": "False"}
    # 下面的表达式测试不符合预期
    # assert BoolRule('${v1} == "False"').test(context) == True
    assert BoolRule("${v1} == ${v1}").test(context) == True
    assert BoolRule("${v1} == false").test(context) == True
    assert BoolRule("${v1} == False").test(context) == True
    assert BoolRule('${v1} == "0"').test(context) == True
    assert BoolRule("${v1} == 0").test(context) == True
    assert BoolRule('${v1} == "0"').test(context) == True

    assert BoolRule('${v1} == "1"').test(context) == False
    assert BoolRule("${v1} == true").test(context) == False
    assert BoolRule('${v1} == "true"').test(context) == False
    assert BoolRule("${v1} == True").test(context) == False
    assert BoolRule('${v1} == "True"').test(context) == False
    assert BoolRule('${v1} == "s"').test(context) == False


def test_multi_or():
    assert BoolRule('("s" > "s" or "su" > "st") or (1 > 3 and 2 < 3)').test() == True
    assert BoolRule('(1 > 3 and 2 < 3)  or ("s" > "s" or "su" > "st")').test() == True
    assert BoolRule('(1 < 3 and 2 < 3)  or ("s" > "s" or "su" > "st")').test() == True
    assert (
        BoolRule(
            '(1 > 2 or 2 > 3) or ("s" > "s" or "su" > "st") or (4  > 5 and 5 < 6)'
        ).test()
        == True
    )

    assert BoolRule('(1 > 2 or 2 > 3) or ("s" > "s" or "su" < "st")').test() == False
    assert (
        BoolRule(
            '(1 > 2 or 2 > 3) or ("s" > "s" or "su" < "st") or (4  > 5 and 5 < 6)'
        ).test()
        == False
    )


def test_multi_and():
    assert BoolRule('("s" > "s" or "su" > "st") and (1 < 3 and 2 < 3)').test() == True

    assert BoolRule('(1 < 2 or 2 > 3) and ("s" > "s" or "su" < "st")').test() == False
    assert BoolRule('(1 > 2 or 2 > 3) and ("s" > "s" or "su" > "st")').test() == False
    assert BoolRule('(1 > 2 or 2 > 3) and ("s" > "s" or "su" < "st")').test() == False
    assert (
        BoolRule(
            '(1 < 3 and 2 < 3)  and ("s" > "s" or "su" > "st") and (4 > 5 and 5 < 6)'
        ).test()
        == False
    )

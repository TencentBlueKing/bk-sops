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

import copy
import datetime

from django.test import TestCase

from pipeline.core.data import expression, sandbox
from pipeline.core.data.expression import format_constant_key, deformat_constant_key


class TestConstantTemplate(TestCase):
    def setUp(self):
        pass

    def test_format_constant_key(self):
        self.assertEqual(format_constant_key("a"), "${a}")

    def test_deformat_constant_key(self):
        self.assertEqual(deformat_constant_key("${a}"), "a")

    def test_get_reference(self):
        all_in_cons_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(set(all_in_cons_template.get_reference()), {"a", "b", "int"})

        comma_exclude_template = expression.ConstantTemplate(['${a["c"]}', ['${"%s" % a}', "${a+int(b)}"]])
        self.assertEqual(set(comma_exclude_template.get_reference()), {"a", "b", "int"})

    def test_get_templates(self):
        cons_tmpl = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(set(cons_tmpl.get_templates()), {"${a+int(b)}", "${a}"})

    def test_resolve_data(self):
        list_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(list_template.resolve_data({"a": 2, "b": "3"}), [2, [2, "5"]])

        tuple_template = expression.ConstantTemplate(("${a}", ("${a}", "${a+int(b)}")))
        self.assertEqual(tuple_template.resolve_data({"a": 2, "b": "3"}), (2, (2, "5")))

        dict_template = expression.ConstantTemplate({"aaaa": {"a": "${a}", "b": "${a+int(b)}"}})
        self.assertEqual(dict_template.resolve_data({"a": 2, "b": "3"}), {"aaaa": {"a": 2, "b": "5"}})

    def test_get_string_templates(self):
        cons_tmpl = expression.ConstantTemplate("")
        self.assertEqual(cons_tmpl.get_string_templates("${a}"), ["${a}"])

    def test_resolve_string(self):
        cons_tmpl = expression.ConstantTemplate("")
        one_template = "${a}"
        self.assertEqual(cons_tmpl.resolve_string(one_template, {"a": "1"}), "1")

    def test_get_template_reference(self):
        cons_tmpl = expression.ConstantTemplate("")
        self.assertEqual(cons_tmpl.get_template_reference("${a}"), ["a"])

    def test_resolve_template(self):
        cons_tmpl = expression.ConstantTemplate("")
        simple = "${a}"
        self.assertEqual(cons_tmpl.resolve_template(simple, {"a": "1"}), "1")

        calculate = "${a+int(b)}"
        self.assertEqual(cons_tmpl.resolve_template(calculate, {"a": 2, "b": "3"}), "5")

        split = "${a[0]}"
        self.assertEqual(cons_tmpl.resolve_template(split, {"a": [1, 2]}), "1")

        dict_item = '${a["b"]}'
        self.assertEqual(cons_tmpl.resolve_template(dict_item, {"a": {"b": 1}}), "1")

        not_exists = "{a}"
        self.assertEqual(cons_tmpl.resolve_template(not_exists, {}), not_exists)

        resolve_syntax_error = "${a.b}"
        self.assertEqual(cons_tmpl.resolve_template(resolve_syntax_error, {}), resolve_syntax_error)

        template_syntax_error = "${a:b}"
        self.assertEqual(cons_tmpl.resolve_template(template_syntax_error, {}), template_syntax_error)

    def test_resolve_template__with_sandbox(self):

        r1 = expression.ConstantTemplate.resolve_template("""${exec(print(''))}""", {})
        self.assertEqual(r1, """${exec(print(''))}""")

        if "datetime" in expression.SANDBOX:
            expression.SANDBOX.pop("datetime")
        r2 = expression.ConstantTemplate.resolve_template("""${datetime.datetime.now().strftime("%Y")}""", {})
        self.assertEqual(r2, """${datetime.datetime.now().strftime("%Y")}""")

        sandbox._shield_words(expression.SANDBOX, ["exec", "compile"])
        sandbox._import_modules(expression.SANDBOX, {"datetime": "datetime"})

        r1 = expression.ConstantTemplate.resolve_template("""${exec(print(''))}""", {})
        self.assertEqual(r1, """${exec(print(''))}""")

        r2 = expression.ConstantTemplate.resolve_template("""${datetime.datetime.now().strftime("%Y")}""", {})
        year = datetime.datetime.now().strftime("%Y")
        self.assertEqual(r2, year)

        # clean
        expression.SANDBOX.pop("exec")
        expression.SANDBOX.pop("compile")

    def test_resolve(self):
        list_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(list_template.resolve_data({"a": 2, "b": "3"}), [2, [2, "5"]])

        tuple_template = expression.ConstantTemplate(("${a}", ("${a}", "${a+int(b)}")))
        self.assertEqual(tuple_template.resolve_data({"a": 2, "b": "3"}), (2, (2, "5")))

        dict_template = expression.ConstantTemplate({"aaaa": {"a": "${a}", "b": "${a+int(b)}"}})
        self.assertEqual(dict_template.resolve_data({"a": 2, "b": "3"}), {"aaaa": {"a": 2, "b": "5"}})

    def test_get_reference_complex(self):
        all_in_cons_template = expression.ConstantTemplate(["${a}", ["${a}", "${a+int(b)}"]])
        self.assertEqual(set(all_in_cons_template.get_reference()), set(["a", "b", "int"]))

        comma_exclude_template = expression.ConstantTemplate(['${a["c"]}', ['${"%s" % a}', "${a+int(b)}"]])
        self.assertEqual(set(comma_exclude_template.get_reference()), set(["a", "b", "int"]))

    def test_built_in_functions__without_args(self):
        int_template = expression.ConstantTemplate("${int}")
        self.assertEqual(int_template.resolve_data({}), "int")

        int_template = expression.ConstantTemplate("${str}")
        self.assertEqual(int_template.resolve_data({}), "str")

    def test_built_in_functions__with_args(self):
        int_template = expression.ConstantTemplate("${int(111)}")
        self.assertEqual(int_template.resolve_data({}), "111")

        int_template = expression.ConstantTemplate("${str('aaa')}")
        self.assertEqual(int_template.resolve_data({}), "aaa")

    def test_built_in_functions__cover(self):
        int_template = expression.ConstantTemplate("${int}")
        self.assertEqual(int_template.resolve_data({"int": "cover"}), "cover")

    def test_template_join(self):
        template = expression.ConstantTemplate("a-${1 if t else 2}-${a}")
        self.assertEqual(template.resolve_data({"t": False, "a": "c"}), "a-2-c")
        template = expression.ConstantTemplate("${'a-%s-c' % 1 if t else 2}")
        self.assertEqual(template.resolve_data({"t": True}), "a-1-c")

    def test_mako_attack(self):
        sandbox_copy = copy.deepcopy(sandbox.SANDBOX)
        shield_words = [
            "ascii",
            "bytearray",
            "bytes",
            "callable",
            "chr",
            "classmethod",
            "compile",
            "delattr",
            "dir",
            "divmod",
            "exec",
            "eval",
            "filter",
            "frozenset",
            "getattr",
            "globals",
            "hasattr",
            "hash",
            "help",
            "id",
            "input",
            "isinstance",
            "issubclass",
            "iter",
            "locals",
            "map",
            "memoryview",
            "next",
            "object",
            "open",
            "print",
            "property",
            "repr",
            "setattr",
            "staticmethod",
            "super",
            "type",
            "vars",
            "__import__",
        ]
        sandbox._shield_words(sandbox.SANDBOX, shield_words)
        attack_templates = [
            '${"".__class__.__mro__[-1].__subclasses__()[127].__init__.__globals__["system"]("whoami")}',  # noqa
            '${getattr("", dir(0)[0][0] + dir(0)[0][0] + "class" + dir(0)[0][0]+ dir(0)[0][0])}',  # noqa
            'a-${__import__("os").system("whoami")}',
            "${while True: pass}",
            """<% import json %> ${json.codecs.builtins.exec('import os; os.system("whoami")')}""",  # noqa
        ]
        for at in attack_templates:
            self.assertEqual(expression.ConstantTemplate(at).resolve_data({}), at)

        sandbox.SANDBOX = sandbox_copy

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

import datetime

from bamboo_engine.config import Settings
from bamboo_engine.template import Template


def test_get_reference():
    t = Template(["${a}", ["${a}", "${a+int(b)}"]])
    assert t.get_reference() == {"${a}", "${b}", "${int}"}

    t = Template(['${a["c"]}', ['${"%s" % a}', "${a+int(b)}"]])
    assert t.get_reference() == {"${a}", "${b}", "${int}"}

    t = Template("a-${1 if t else 2}-${a}")
    assert t.render({"t": False, "a": "c"}) == "a-2-c"
    t = Template("${'a-%s-c' % 1 if t else 2}")
    assert t.render({"t": True}) == "a-1-c"


def test_get_templates():
    t = Template(["${a}", ["${a}", "${a+int(b)}"]])
    assert set(t.get_templates()) == {"${a+int(b)}", "${a}"}


def test_render():
    list_template = Template(["${a}", ["${a}", "${a+int(b)}"]])
    assert list_template.render({"a": 2, "b": "3"}), [2, [2, "5"]]

    tuple_template = Template(("${a}", ("${a}", "${a+int(b)}")))
    assert tuple_template.render({"a": 2, "b": "3"}), (2, (2, "5"))

    dict_template = Template({"aaaa": {"a": "${a}", "b": "${a+int(b)}"}})
    assert dict_template.render({"a": 2, "b": "3"}), {"aaaa": {"a": 2, "b": "5"}}

    simple_template = Template("${a}")
    assert simple_template.render({"a": "1"}) == "1"

    calculate_template = Template("${a+int(b)}")
    assert calculate_template.render({"a": 2, "b": "3"}) == "5"

    split_template = Template("${a[0]}")
    assert split_template.render({"a": [1, 2]}) == "1"

    dict_item_template = Template('${a["b"]}')
    assert dict_item_template.render({"a": {"b": 1}}) == "1"

    not_exists_template = Template("${a}")
    assert not_exists_template.render({}) == "${a}"

    syntax_error_template = Template("${a.b}")
    assert syntax_error_template.render({}) == "${a.b}"

    syntax_error_template = Template("${a:b}")
    assert syntax_error_template.render({}) == "${a:b}"


def test_render__with_sandbox():

    r1 = Template("""${exec(print(''))}""").render({})
    assert r1 == """${exec(print(''))}"""

    r2 = Template("""${datetime.datetime.now().strftime("%Y")}""").render({})
    assert r2 == """${datetime.datetime.now().strftime("%Y")}"""

    Settings.MAKO_SANDBOX_IMPORT_MODULES = {"datetime": "datetime"}

    r2 = Template("""${datetime.datetime.now().strftime("%Y")}""").render({})
    year = datetime.datetime.now().strftime("%Y")
    assert r2 == year

    Settings.MAKO_SANDBOX_IMPORT_MODULES = {}

    r3 = Template("""${exec(print(''))}""").render({})
    assert r1 == """${exec(print(''))}"""


def test_render__built_in_functions__with_args():
    int_template = Template("${int(111)}")
    assert int_template.render({}) == "111"

    int_template = Template("${str('aaa')}")
    assert int_template.render({}) == "aaa"


def test_redner__built_in_functions__cover():
    int_template = Template("${int}")
    assert int_template.render({"int": "cover"}) == "cover"


def test_mako_attack():
    attack_templates = [
        '${"".__class__.__mro__[-1].__subclasses__()[127].__init__.__globals__["system"]("whoami")}',  # noqa
        '${getattr("", dir(0)[0][0] + dir(0)[0][0] + "class" + dir(0)[0][0]+ dir(0)[0][0])}',  # noqa
        'a-${__import__("os").system("whoami")}',
        "${while True: pass}",
        """<% import json %> ${json.codecs.builtins.exec('import os; os.system("whoami")')}""",  # noqa
    ]
    for at in attack_templates:
        assert Template(at).render({}) == at

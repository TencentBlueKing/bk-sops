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

bk-sops 端 Mako 根标识符白名单回归。

`bksops-security-review-independent.md` §三 SOPS-01 的"撤回"判断在 Mako 保留命名空间
（`self / context / local / parent / next / caller / pageargs`）这条路径上不成立——
攻击者通过 ``${self.module.cache.util.os.popen(...)}`` 即可在 ``check_mako_template_safety``
后照常渲染并触发命令执行。

本测试套件钉死以下不变量：

1. ``MAKO_TEMPLATE_NAME_WHITELIST_MODE = enforce`` 时 PoC 与各种 Mako 保留命名空间链路
   都被拦截，渲染原样回显；
2. ``_system / _loop`` 等 ``MAKO_TEMPLATE_NAME_EXTRA_WHITELIST`` 中声明的根名仍能正常使用；
3. 业务侧常见 pattern（变量方法 / 模块别名 / 推导式 / lambda）在 enforce 下不会误伤；
4. ``MAKO_TEMPLATE_NAME_WHITELIST_MODE = off`` 时 PoC 仍能执行——保留这条用例是为了
   未来一旦上游 deny-list 加强了对保留命名空间的拦截，能立刻提示重新评估白名单的必要性。
"""

from bamboo_engine.config import Settings as BambooSettings
from bamboo_engine.template import Template
from django.test import TestCase, override_settings


class MakoNameWhitelistEnforceTestCase(TestCase):
    """``enforce`` 模式：Mako 保留命名空间被拦，业务模式不受影响。"""

    def setUp(self):
        self._original_mode = BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE
        self._original_extra = BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = "enforce"
        BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST = frozenset({"_system", "_loop"})

    def tearDown(self):
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = self._original_mode
        BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST = self._original_extra

    def test_self_module_cache_util_os_popen_is_blocked(self):
        """SOPS-01 真实 PoC：通过 ``self.module.cache`` 触达 ``os.popen``。

        ``enforce`` 下应该被白名单拦截，``Template.render`` 输出原样回显，
        不应包含 ``echo`` 命令的执行结果 ``PWNED``。
        """
        payload = '${self.module.cache.util.os.popen("echo PWNED").read()}'
        rendered = Template({"probe": payload}).render({})
        self.assertEqual(rendered, {"probe": payload})
        # payload 原文含 ``echo PWNED``，只能断言执行结果没有单独回写
        self.assertNotEqual(rendered["probe"].strip(), "PWNED")

    def test_other_reserved_namespaces_are_blocked(self):
        for payload in [
            '${local.module.cache.util.os.popen("echo PWNED").read()}',
            '${parent.module.cache.util.os.popen("echo PWNED").read()}',
            "${caller.body()}",
        ]:
            with self.subTest(payload=payload):
                rendered = Template({"p": payload}).render({})
                self.assertEqual(rendered["p"], payload)

    def test_bare_caller_and_user_module_attr_render(self):
        # ``${caller}`` 会被 ``Template.render`` 按 context 键短路，AST 走不到 visitor。
        self.assertEqual(Template("${caller}").render({"caller": "alice"}), "alice")
        # 用 ``${parent + ''}`` 迫使白名单检查命中（与引擎 Task 3 一致）。
        self.assertEqual(Template("${parent + ''}").render({"parent": "alice"}), "alice")

        class Bag(object):
            def __init__(self):
                self._module = [{"gamesvr": "10.0.0.1"}]

        self.assertEqual(
            Template("${obj._module[0]['gamesvr']}").render({"obj": Bag()}),
            "10.0.0.1",
        )

    def test_self_module_blocked_even_with_self_in_context(self):
        payload = '${self.module.cache.util.os.popen("echo PWNED").read()}'
        rendered = Template({"probe": payload}).render({"self": "x"})
        self.assertEqual(rendered["probe"], payload)
        # payload 原文含 ``echo PWNED``，只能断言执行结果没有单独回写
        self.assertNotEqual(rendered["probe"].strip(), "PWNED")

    def test_business_patterns_render_normally(self):
        cases = [
            ("${name.upper()}", {"name": "hello"}, "HELLO"),
            ("${a + b}", {"a": 1, "b": 2}, "3"),
            ("${a[0]}", {"a": [10, 20]}, "10"),
            ("${len(xs)}", {"xs": [1, 2, 3]}, "3"),
            ("${[x.upper() for x in items]}", {"items": ["a", "b"]}, "['A', 'B']"),
            ("${(lambda v: v + 1)(n)}", {"n": 5}, "6"),
            ("${'/'.join([p for p in parts])}", {"parts": ["a", "b"]}, "a/b"),
            ("${'yes' if flag else 'no'}", {"flag": True}, "yes"),
        ]
        for tpl, ctx, expected in cases:
            with self.subTest(tpl=tpl):
                self.assertEqual(Template(tpl).render(ctx), expected)

    def test_extra_whitelist_underscore_names_still_usable(self):
        """``_system / _loop`` 是渲染期才注入的根标识符，必须能在表达式里被引用。"""
        # ``${_loop+1}`` 走完整 Mako 渲染，验证 ``_loop`` 通过白名单
        self.assertEqual(Template("loop=${_loop+1}").render({"_loop": 7}), "loop=8")
        # ``${_system.attr}`` 走完整渲染，验证 ``_system`` 通过白名单
        from engine_pickle_obj.context import SystemObject

        ctx = {"_system": SystemObject({"executor": "alice"})}
        self.assertEqual(Template("by=${_system.executor}").render(ctx), "by=alice")

    def test_imported_modules_render(self):
        """管理员通过导入表配置的别名，首段必须自动进入白名单。"""
        import datetime as _dt

        original = BambooSettings.MAKO_SANDBOX_IMPORT_MODULES
        BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = {
            "datetime": "datetime",
            "datetime.datetime": "datetime.datetime",
            "os.path": "os.path",
        }
        try:
            out = Template('${datetime.datetime.now().strftime("%Y")}').render({})
            self.assertEqual(out, _dt.datetime.now().strftime("%Y"))
            self.assertEqual(Template('${os.path.join("a", "b")}').render({}), "a/b")
        finally:
            BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = original


class MakoNameWhitelistOffTestCase(TestCase):
    """``off`` 模式：保持上游 deny-list 行为，PoC 仍能执行。

    这条用例锁住"漏洞存在的状态"。一旦未来 ``off`` 模式下 PoC 突然 inert，意味着
    上游 ``SingleLineNodeVisitor`` 已经把 Mako 保留命名空间也加入了 deny-list，
    届时本仓白名单的必要性应被重新评估（仍建议保留作为纵深防御）。
    """

    def setUp(self):
        self._original_mode = BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = "off"

    def tearDown(self):
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = self._original_mode

    def test_self_module_namespace_executes_when_off(self):
        payload = '${self.module.cache.util.os.popen("echo OFF_MODE").read()}'
        rendered = Template({"probe": payload}).render({})
        self.assertIn(
            "OFF_MODE",
            rendered["probe"],
            "off 模式下保留命名空间未被拦——若该用例失败，请检查上游 deny-list 是否新增" "对 self/context/local/... 的拦截，并同步评估白名单是否仍是必需。",
        )


@override_settings()
class MakoNameWhitelistConfigBindingTestCase(TestCase):
    """确认 ``config/default.py`` 中的配置正确流到 ``BambooSettings``。

    渲染链路读取 ``BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE``，
    所以这里直接断言绑定结果，避免有人改 ``settings.py`` 时没同步更新 ``BambooSettings``。
    """

    def test_settings_propagated_to_bamboo(self):
        # 默认 ``enforce``，且不得发明第四档 mode
        self.assertIn(BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE, {"off", "warn", "enforce"})
        # ``_system / _loop`` 必须出现在 extra
        self.assertIn("_system", BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST)
        self.assertIn("_loop", BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST)
        # 精确策略禁止靠 extra 名单救 ``_module`` / ``caller``
        self.assertNotIn("_module", BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST)
        self.assertNotIn("caller", BambooSettings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST)
        # 导入表默认空，只认 BKAPP_SOPS_MAKO_IMPORT_MODULES
        self.assertEqual(BambooSettings.MAKO_SANDBOX_IMPORT_MODULES, {})

    def test_default_import_table_is_empty(self):
        from django.conf import settings

        self.assertEqual(settings.MAKO_SANDBOX_IMPORT_MODULES, {})
        self.assertNotIn("datetime.datetime", settings.MAKO_SANDBOX_IMPORT_MODULES)
        self.assertNotIn("datetime", settings.MAKO_SANDBOX_IMPORT_MODULES)

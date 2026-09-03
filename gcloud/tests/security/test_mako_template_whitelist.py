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

from unittest import skipUnless

from bamboo_engine.config import Settings as BambooSettings
from bamboo_engine.template import Template
from bamboo_engine.template import sandbox as _engine_sandbox
from bamboo_engine.utils import mako_safety as _engine_mako_safety
from django.test import TestCase, override_settings

# 生成器帧反射 RCE 的加固落在引擎侧（bamboo-pipeline 3.24.17 / bamboo-engine 2.6.6+）。
# bk-sops 只钉不变量：装上含加固的引擎后，下面这条通用链路必须被拦死。未装到（当前 pin
# 仍是 3.24.16）时用例自动 skip，避免对旧引擎误报。
_HAS_FRAME_HARDENING = hasattr(_engine_mako_safety, "FRAME_INTROSPECTION_ATTRS") and hasattr(
    _engine_sandbox, "restricted_builtins"
)


def _probe_alwayson_hardening():
    """探测已安装引擎是否已把危险属性/保留命名空间链下沉到 always-on 层。

    直接用 always-on 的 ``SingleLineNodeVisitor`` 跑 ``${obj.os}``：加固后必抛异常。
    """
    try:
        from bamboo_engine.utils.mako_safety import SingleLinCodeExtractor, SingleLineNodeVisitor
        from bamboo_engine.utils.mako_utils.checker import check_mako_template_safety
        from bamboo_engine.utils.mako_utils.exceptions import ForbiddenMakoTemplateException
    except Exception:
        return False
    try:
        check_mako_template_safety("${obj.os}", SingleLineNodeVisitor(), SingleLinCodeExtractor())
        return False
    except ForbiddenMakoTemplateException:
        return True
    except Exception:
        return False


# always-on 收紧（危险属性 + 保留命名空间链，堵住 off/warn 的模块反向 pivot）落在引擎侧
# bamboo-pipeline 3.24.17 / bamboo-engine PR#284。装上后下面这组 off 模式不变量才生效；
# 当前 pin（3.24.16）未装到时自动 skip。
_HAS_ALWAYSON_HARDENING = _probe_alwayson_hardening()
# 注入模块 deny-list（``filter_import_modules``）同 PR#284。
_HAS_IMPORT_DENYLIST = hasattr(_engine_sandbox, "filter_import_modules")


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

    @skipUnless(
        not _HAS_ALWAYSON_HARDENING,
        "引擎已把危险属性/保留命名空间链下沉 always-on，off 模式不再执行 PoC，见 MakoAlwaysOnHardeningTestCase",
    )
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


@skipUnless(_HAS_FRAME_HARDENING, "当前安装的引擎未包含生成器帧反射加固（需 bamboo-pipeline 3.24.17+）")
class MakoGeneratorFrameGadgetTestCase(TestCase):
    """生成器帧反射 RCE 回归。

    ``${(i for i in [1]).gi_frame.f_builtins['eval'](...)}`` 经生成器帧拿到**真实**
    builtins，再用非 dunder 下标 ``['eval']`` 取执行原语——``gi_frame`` / ``f_builtins``
    都不是 ``__`` 前缀，也不在旧 deny-list 里，因此 off/warn/enforce 三档全部裸奔，且与
    ``MAKO_SANDBOX_IMPORT_MODULES`` 配置无关。

    引擎加固后本仓钉两条不变量：
    1. 该链路在三种模式下都被 inert（原样回显，不执行）；
    2. 渲染期受限 builtins 已摘掉 eval/exec 等直接执行原语（纵深防御，防未来新反射路径）。
    """

    def setUp(self):
        self._original_mode = BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE

    def tearDown(self):
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = self._original_mode

    def test_generator_frame_gadget_is_inert_in_all_modes(self):
        payload = "${(i for i in [1]).gi_frame.f_builtins['eval']" "(\"__import__('os').popen('echo PWNED').read()\")}"
        for mode in ("off", "warn", "enforce"):
            with self.subTest(mode=mode):
                BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = mode
                rendered = Template({"probe": payload}).render({})
                self.assertEqual(rendered["probe"], payload)
                self.assertNotEqual(rendered["probe"].strip(), "PWNED")

    def test_frame_introspection_attrs_are_blocked(self):
        for attr in ["gi_frame", "cr_frame", "ag_frame", "f_builtins", "f_globals", "f_back"]:
            with self.subTest(attr=attr):
                payload = "${obj.%s}" % attr
                self.assertEqual(Template({"p": payload}).render({})["p"], payload)

    def test_render_builtins_strip_execution_primitives(self):
        rb = _engine_sandbox.restricted_builtins()
        for name in ("eval", "exec", "compile", "open", "input", "breakpoint"):
            self.assertNotIn(name, rb)
        # 不能误伤安全内建与 C 扩展惰性 import 依赖的 __import__
        for name in ("len", "str", "range", "int", "__import__"):
            self.assertIn(name, rb)


@skipUnless(_HAS_ALWAYSON_HARDENING, "当前安装的引擎未把危险属性/保留命名空间链下沉 always-on（需 bamboo-pipeline 3.24.17+）")
class MakoAlwaysOnHardeningTestCase(TestCase):
    """always-on 收紧回归：off 模式也拦住模块反向 pivot 与 ``self.module...`` 链。

    此前危险属性名与保留命名空间链只在 enforce 白名单里挡，``off`` 模式下
    ``${self.module.cache.util.os.popen(...)}`` / ``${os.path.os.system(...)}`` /
    ``${json.codecs.builtins.exec(...)}`` 可反向 pivot 到真实模块拿 RCE。下沉 always-on 后
    三档全部 inert，且与白名单模式无关。
    """

    def setUp(self):
        self._original_mode = BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE

    def tearDown(self):
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = self._original_mode

    def test_self_module_chain_blocked_in_all_modes(self):
        payload = '${self.module.cache.util.os.popen("echo PWNED").read()}'
        for mode in ("off", "warn", "enforce"):
            with self.subTest(mode=mode):
                BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = mode
                rendered = Template({"probe": payload}).render({})
                self.assertEqual(rendered["probe"], payload)
                self.assertNotEqual(rendered["probe"].strip(), "PWNED")

    def test_module_reverse_pivot_blocked_in_all_modes(self):
        original = BambooSettings.MAKO_SANDBOX_IMPORT_MODULES
        BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = {
            "datetime": "datetime",
            "re": "re",
            "os.path": "os.path",
            "json": "json",
        }
        payloads = [
            '${os.path.os.system("echo PWNED")}',
            '${datetime.sys.modules["os"].popen("echo PWNED").read()}',
            '${json.codecs.builtins.exec("import os")}',
        ]
        try:
            for mode in ("off", "warn", "enforce"):
                for p in payloads:
                    with self.subTest(mode=mode, payload=p):
                        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = mode
                        self.assertEqual(Template({"x": p}).render({})["x"], p)
        finally:
            BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = original

    def test_reserved_namespace_chain_blocked_in_all_modes(self):
        for mode in ("off", "warn", "enforce"):
            for p in ("${context.lookup}", "${local.something}", "${parent.foo}"):
                with self.subTest(mode=mode, payload=p):
                    BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = mode
                    self.assertEqual(Template({"p": p}).render({})["p"], p)

    def test_business_patterns_still_render_off_mode(self):
        BambooSettings.MAKO_TEMPLATE_NAME_WHITELIST_MODE = "off"
        cases = [
            ("${name.upper()}", {"name": "hello"}, "HELLO"),
            ("${obj._module[0]['ip']}", {"obj": type("B", (), {"_module": [{"ip": "1.1.1.1"}]})()}, "1.1.1.1"),
            ("${[x * 2 for x in items]}", {"items": [1, 2]}, "[2, 4]"),
        ]
        for tpl, ctx, expected in cases:
            with self.subTest(tpl=tpl):
                self.assertEqual(Template(tpl).render(ctx), expected)


@skipUnless(_HAS_IMPORT_DENYLIST, "当前安装的引擎未提供注入模块 deny-list（需 bamboo-pipeline 3.24.17+）")
class MakoImportDenylistTestCase(TestCase):
    """注入模块 deny-list 回归：危险模块永远进不了 Mako 沙箱。"""

    def test_filter_import_modules_rejects_dangerous_keeps_safe(self):
        src = {
            "os": "os",
            "subprocess": "subprocess",
            "operator": "operator",
            "pickle": "pickle",
            "importlib": "importlib",
            "os.path": "os.path",
            "json": "json",
            "re": "re",
        }
        self.assertEqual(set(_engine_sandbox.filter_import_modules(src)), {"os.path", "json", "re"})

    def test_sandbox_get_does_not_expose_dangerous_module(self):
        original = BambooSettings.MAKO_SANDBOX_IMPORT_MODULES
        BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = {
            "os": "os",
            "subprocess": "subprocess",
            "os.path": "os.path",
            "json": "json",
        }
        try:
            data = _engine_sandbox.get()
            self.assertNotIn("subprocess", data)
            self.assertIsNone(getattr(data.get("os"), "system", None))
            self.assertIn("json", data)
        finally:
            BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = original

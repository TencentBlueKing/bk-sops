# -*- coding: utf-8 -*-
"""Exercise the real Mako settings section without starting unrelated Django apps."""
import ast
import importlib
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock

from bamboo_engine.config import Settings as BambooSettings
from bamboo_engine.template import Template, render_backend, sandbox
from bamboo_engine.utils import mako_safety

ROOT = Path(__file__).resolve().parents[3]
COMPAT_IMPORTS = "datetime,re,hashlib,random,time,os.path,config.mock.mock_json:json"


def load_mako_settings(environ=None, env_version=2):
    # Run the source statements, including the env_v2/v3 parsing and BambooSettings
    # assignments; avoid copying the configuration logic into the test.
    env_tree = ast.parse((ROOT / "env_v{}.py".format(env_version)).read_text())
    env_tree.body = [
        node
        for node in env_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id.startswith("SOPS_MAKO_") for target in node.targets)
    ]
    source = ROOT / "config/default.py"
    tree = ast.parse(source.read_text())
    boundaries = {}
    for index, node in enumerate(tree.body):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    boundaries[target.id] = index
    tree.body = tree.body[boundaries["MAKO_SANDBOX_SHIELD_WORDS"] : boundaries["ENABLE_EXAMPLE_COMPONENTS"]]
    with mock.patch.dict(os.environ, environ or {}, clear=True):
        env_scope = {"os": os}
        exec(compile(env_tree, str(ROOT / "env_v{}.py".format(env_version)), "exec"), env_scope)
        scope = {"os": os, "importlib": importlib, "env": SimpleNamespace(**env_scope)}
        scope["BambooSettings"] = SimpleNamespace()
        exec(compile(tree, str(source), "exec"), scope)
    return scope


class MakoDeploymentSettingsTestCase(TestCase):
    def test_required_engine_capabilities_are_installed(self):
        self.assertTrue(hasattr(sandbox, "resolve_import_object"))
        self.assertTrue(hasattr(sandbox, "filter_import_modules"))
        self.assertTrue(hasattr(mako_safety, "FRAME_INTROSPECTION_ATTRS"))
        self.assertTrue(hasattr(render_backend, "SubprocessPoolRenderBackend"))

    def test_defaults_are_inprocess_with_strict_isolation_if_enabled(self):
        scope = load_mako_settings()
        settings = scope["BambooSettings"]
        self.assertEqual(settings.MAKO_RENDER_BACKEND, "inprocess")
        self.assertEqual(settings.MAKO_TEMPLATE_NAME_WHITELIST_MODE, "enforce")
        self.assertEqual(settings.MAKO_SANDBOX_IMPORT_MODULES, {})
        self.assertFalse(settings.MAKO_RENDER_FALLBACK_INPROCESS)
        self.assertTrue(settings.MAKO_RENDER_NO_NETWORK)
        self.assertTrue(settings.MAKO_RENDER_OS_HARDEN)
        for name, value in vars(settings).items():
            self.assertEqual(scope[name], value, name)

    def test_backend_switch_and_typed_pool_options_reach_engine(self):
        scope = load_mako_settings(
            {
                "BKAPP_MAKO_RENDER_BACKEND": "subprocess",
                "BKAPP_MAKO_RENDER_POOL_SIZE": "2",
                "BKAPP_MAKO_RENDER_MAX_USES": "7",
                "BKAPP_MAKO_RENDER_TIMEOUT": "1.5",
                "BKAPP_MAKO_RENDER_FALLBACK_INPROCESS": "0",
                "BKAPP_MAKO_RENDER_OS_HARDEN": "0",
                "BKAPP_MAKO_RENDER_NO_NETWORK": "0",
                "BKAPP_MAKO_RENDER_RLIMIT_CPU": "10",
                "BKAPP_MAKO_RENDER_RLIMIT_AS_MB": "512",
                "BKAPP_MAKO_RENDER_ENV_SCRUB_EXTRA": " CUSTOM_SECRET, ANOTHER_SECRET, ",
            }
        )
        with mock.patch.multiple(BambooSettings, create=True, **vars(scope["BambooSettings"])):
            backend = render_backend._build_default_backend()
            try:
                self.assertIsInstance(backend, render_backend.SubprocessPoolRenderBackend)
                self.assertEqual(backend.pool_size, 2)
                self.assertEqual(backend.max_uses, 7)
                self.assertEqual(backend.timeout, 1.5)
                self.assertFalse(backend.fallback_inprocess)
                self.assertEqual(
                    backend._harden_opts,
                    {"enabled": False, "no_network": False, "rlimit_cpu": 10, "rlimit_as_mb": 512},
                )
                self.assertIn("CUSTOM_SECRET", backend._scrub_patterns)
                self.assertIn("ANOTHER_SECRET", backend._scrub_patterns)
            finally:
                backend.close()

    def test_invalid_backend_or_boolean_does_not_silently_disable_isolation(self):
        for name, value in [
            ("BKAPP_MAKO_RENDER_BACKEND", "subproces"),
            ("BKAPP_MAKO_RENDER_NO_NETWORK", "typo"),
            ("BKAPP_MAKO_RENDER_OS_HARDEN", "typo"),
            ("BKAPP_MAKO_RENDER_FALLBACK_INPROCESS", "typo"),
        ]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                load_mako_settings({name: value})

    def test_compatibility_env_in_both_paas_versions(self):
        for version in (2, 3):
            with self.subTest(version=version):
                scope = load_mako_settings(
                    {"BKAPP_SOPS_MAKO_IMPORT_MODULES": COMPAT_IMPORTS, "BKAPP_SOPS_MAKO_WHITELIST_MODE": "warn"},
                    env_version=version,
                )
                self.assertEqual(scope["MAKO_TEMPLATE_NAME_WHITELIST_MODE"], "warn")
                self.assertEqual(scope["MAKO_SANDBOX_IMPORT_MODULES"]["config.mock.mock_json"], "json")
                self.assertEqual(scope["MAKO_SANDBOX_IMPORT_MODULES"]["os.path"], "os.path")

    def test_format_and_compatibility_imports_in_both_engines(self):
        from pipeline.core.data import expression, sandbox_builder

        for mode in ("warn", "off", "enforce"):
            scope = load_mako_settings(
                {"BKAPP_SOPS_MAKO_IMPORT_MODULES": COMPAT_IMPORTS, "BKAPP_SOPS_MAKO_WHITELIST_MODE": mode}
            )
            imports = scope["MAKO_SANDBOX_IMPORT_MODULES"]
            shield = scope["MAKO_SANDBOX_SHIELD_WORDS"]
            with mock.patch.multiple(BambooSettings, create=True, **vars(scope["BambooSettings"])):
                with mock.patch.multiple(
                    expression,
                    MAKO_SANDBOX_IMPORT_MODULES=imports,
                    MAKO_SANDBOX_SHIELD_WORDS=shield,
                    SANDBOX=sandbox_builder.build_sandbox(shield, imports),
                ):
                    format_expr = "${pattern.format(name)}"
                    for renderer in (
                        lambda tpl, ctx: Template(tpl).render(ctx),
                        expression.ConstantTemplate.resolve_string,
                    ):
                        with self.subTest(mode=mode, renderer=renderer):
                            self.assertEqual(
                                renderer(format_expr, {"pattern": "hello {}", "name": "world"}),
                                format_expr if mode == "enforce" else "hello world",
                            )
                            self.assertEqual(renderer("${json.dumps([1, 2])}", {}), "[1, 2]")
                            self.assertEqual(renderer('${os.path.join("a", "b")}', {}), "a/b")

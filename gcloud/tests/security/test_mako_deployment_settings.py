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

    def test_defaults_use_subprocess_without_network_namespace_in_both_paas_versions(self):
        for version in (2, 3):
            with self.subTest(version=version):
                scope = load_mako_settings(env_version=version)
                settings = scope["BambooSettings"]
                self.assertEqual(settings.MAKO_RENDER_BACKEND, "subprocess")
                self.assertEqual(settings.MAKO_TEMPLATE_NAME_WHITELIST_MODE, "enforce")
                self.assertEqual(settings.MAKO_SANDBOX_IMPORT_MODULES, {})
                self.assertFalse(settings.MAKO_RENDER_FALLBACK_INPROCESS)
                self.assertFalse(settings.MAKO_RENDER_NO_NETWORK)
                self.assertTrue(settings.MAKO_RENDER_OS_HARDEN)
                for name, value in vars(settings).items():
                    self.assertEqual(scope[name], value, name)
                with mock.patch.multiple(BambooSettings, create=True, **vars(settings)):
                    backend = render_backend._build_default_backend()
                    try:
                        self.assertIsInstance(backend, render_backend.SubprocessPoolRenderBackend)
                        self.assertFalse(backend.fallback_inprocess)
                        self.assertFalse(backend._harden_opts["no_network"])
                        self.assertTrue(backend._harden_opts["enabled"])
                    finally:
                        backend.close()

    def test_explicit_network_isolation_reaches_worker_options_in_both_paas_versions(self):
        for version in (2, 3):
            with self.subTest(version=version):
                scope = load_mako_settings({"BKAPP_MAKO_RENDER_NO_NETWORK": "1"}, env_version=version)
                self.assertTrue(scope["MAKO_RENDER_NO_NETWORK"])
                self.assertTrue(scope["BambooSettings"].MAKO_RENDER_NO_NETWORK)
                with mock.patch.multiple(BambooSettings, create=True, **vars(scope["BambooSettings"])):
                    backend = render_backend._build_default_backend()
                    try:
                        self.assertIsInstance(backend, render_backend.SubprocessPoolRenderBackend)
                        self.assertTrue(backend._harden_opts["no_network"])
                        self.assertTrue(backend._harden_opts["enabled"])
                        self.assertFalse(backend.fallback_inprocess)
                    finally:
                        backend.close()

    def test_explicit_inprocess_override_in_both_paas_versions(self):
        for version in (2, 3):
            with self.subTest(version=version):
                scope = load_mako_settings({"BKAPP_MAKO_RENDER_BACKEND": "inprocess"}, env_version=version)
                self.assertEqual(scope["MAKO_RENDER_BACKEND"], "inprocess")
                with mock.patch.multiple(BambooSettings, create=True, **vars(scope["BambooSettings"])):
                    backend = render_backend._build_default_backend()
                    self.assertIsInstance(backend, render_backend.InProcessRenderBackend)

    def test_default_backend_renders_in_real_worker_without_host_fallback(self):
        from pipeline.core.data.expression import ConstantTemplate

        for version in (2, 3):
            with self.subTest(version=version):
                # Exercise deployment defaults with every Mako environment variable unset.
                scope = load_mako_settings(env_version=version)
                with mock.patch.multiple(BambooSettings, create=True, **vars(scope["BambooSettings"])):
                    backend = render_backend._build_default_backend()
                    try:
                        with mock.patch.object(render_backend, "_BACKEND", backend), mock.patch.object(
                            render_backend.InProcessRenderBackend, "render", side_effect=AssertionError("host fallback")
                        ):
                            self.assertEqual(Template("value=${number + 1}").render({"number": 1}), "value=2")
                            self.assertEqual(
                                ConstantTemplate.resolve_string("value=${number + 1}", {"number": 1}), "value=2"
                            )
                    finally:
                        backend.close()

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

    def test_production_compatibility_preset_reaches_both_paas_versions_and_engine(self):
        imports = "datetime,datetime.datetime,datetime.date,re,hashlib,random,time,os.path,config.mock.mock_json:json"
        for version in (2, 3):
            with self.subTest(version=version):
                scope = load_mako_settings(
                    {
                        "BKAPP_SOPS_MAKO_IMPORT_MODULES": imports,
                        "BKAPP_SOPS_MAKO_WHITELIST_MODE": "warn",
                        "BKAPP_MAKO_RENDER_BACKEND": "subprocess",
                        "BKAPP_MAKO_RENDER_NO_NETWORK": "0",
                        "BKAPP_MAKO_RENDER_FALLBACK_INPROCESS": "1",
                    },
                    env_version=version,
                )
                settings = scope["BambooSettings"]
                self.assertEqual(settings.MAKO_TEMPLATE_NAME_WHITELIST_MODE, "warn")
                self.assertEqual(settings.MAKO_TEMPLATE_NAME_EXTRA_WHITELIST, frozenset({"_system", "_loop"}))
                self.assertEqual(len(settings.MAKO_SANDBOX_IMPORT_MODULES), 9)
                for path in ("datetime.datetime", "datetime.date", "os.path"):
                    self.assertEqual(settings.MAKO_SANDBOX_IMPORT_MODULES[path], path)
                self.assertEqual(settings.MAKO_SANDBOX_IMPORT_MODULES["config.mock.mock_json"], "json")
                for name, value in vars(settings).items():
                    self.assertEqual(scope[name], value, name)
                with mock.patch.multiple(BambooSettings, create=True, **vars(settings)):
                    backend = render_backend._build_default_backend()
                    try:
                        self.assertIsInstance(backend, render_backend.SubprocessPoolRenderBackend)
                        self.assertTrue(backend.fallback_inprocess)
                        self.assertFalse(backend._harden_opts["no_network"])
                        self.assertTrue(backend._harden_opts["enabled"])
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

    def test_whitelist_mode_is_normalized_and_validated_in_both_paas_versions(self):
        for version in (2, 3):
            for raw, expected in [(" off ", "off"), ("WARN", "warn"), (" Enforce ", "enforce")]:
                with self.subTest(version=version, raw=raw):
                    scope = load_mako_settings({"BKAPP_SOPS_MAKO_WHITELIST_MODE": raw}, env_version=version)
                    self.assertEqual(scope["MAKO_TEMPLATE_NAME_WHITELIST_MODE"], expected)
                    self.assertEqual(scope["BambooSettings"].MAKO_TEMPLATE_NAME_WHITELIST_MODE, expected)
            for raw in ("enfroce", "", "   ", "disabled"):
                with self.subTest(version=version, raw=raw), self.assertRaisesRegex(
                    ValueError, "BKAPP_SOPS_MAKO_WHITELIST_MODE"
                ):
                    load_mako_settings({"BKAPP_SOPS_MAKO_WHITELIST_MODE": raw}, env_version=version)

    def test_file_and_network_modules_are_rejected_before_import(self):
        blocked = {"io", "_io", "http", "urllib", "ftplib", "smtplib", "xmlrpc", "webbrowser", "antigravity"}
        original_import = importlib.import_module

        def guarded_import(name, *args, **kwargs):
            self.assertNotIn(name.split(".", 1)[0], blocked, "rejected modules must not be imported first")
            return original_import(name, *args, **kwargs)

        for legacy in (False, True):
            with self.subTest(legacy=legacy), mock.patch.dict(sandbox.__dict__):
                if legacy:
                    del sandbox.resolve_import_object
                    del sandbox.filter_import_modules
                modules = COMPAT_IMPORTS + "," + ",".join(sorted(blocked)) + ",io.open:reader,urllib.request:client"
                with mock.patch.object(importlib, "import_module", side_effect=guarded_import):
                    scope = load_mako_settings({"BKAPP_SOPS_MAKO_IMPORT_MODULES": modules})
                self.assertEqual(len(scope["MAKO_SANDBOX_IMPORT_MODULES"]), 7)
                self.assertEqual(scope["MAKO_SANDBOX_IMPORT_MODULES"]["os.path"], "os.path")
                self.assertEqual(scope["MAKO_SANDBOX_IMPORT_MODULES"]["config.mock.mock_json"], "json")

    def test_legacy_resolver_only_skips_existing_class_paths(self):
        with mock.patch.dict(sandbox.__dict__):
            del sandbox.resolve_import_object
            scope = load_mako_settings({"BKAPP_SOPS_MAKO_IMPORT_MODULES": "datetime,datetime.datetime"})
            self.assertEqual(scope["MAKO_SANDBOX_IMPORT_MODULES"], {"datetime": "datetime"})
            for missing in ("missing_mako_test_package.utils", "datetime.missing_mako_class"):
                with self.subTest(missing=missing), self.assertRaises(ImportError):
                    load_mako_settings({"BKAPP_SOPS_MAKO_IMPORT_MODULES": missing})

    def test_format_and_compatibility_imports_in_both_engines(self):
        from pipeline.core.data import expression, sandbox_builder

        # Exercise the real worker while keeping Linux namespace privileges out
        # of expression-policy tests. Restore any backend owned by other tests.
        backend = render_backend.SubprocessPoolRenderBackend(
            pool_size=1, no_network=False, os_harden=False, fallback_inprocess=False
        )
        self.addCleanup(backend.close)
        backend_patch = mock.patch.object(render_backend, "_BACKEND", backend)
        backend_patch.start()
        self.addCleanup(backend_patch.stop)
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

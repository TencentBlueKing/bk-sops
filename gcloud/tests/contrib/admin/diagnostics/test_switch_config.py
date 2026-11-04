# -*- coding: utf-8 -*-
"""Configuration compatibility tests; no Django setup or external services required."""
import ast
import itertools
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock

from gcloud.diagnostics_config import resolve_switches


def load_switch_settings(environ):
    """Execute the real env/settings assignments without unrelated application startup."""
    root = Path(__file__).resolve().parents[5]

    def section(path, start, end):
        tree = ast.parse(path.read_text())
        indices = {
            target.id: index
            for index, node in enumerate(tree.body)
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        tree.body = tree.body[indices[start] : indices[end] + 1]
        return compile(tree, str(path), "exec")

    with mock.patch.dict(os.environ, environ, clear=True):
        env = {"os": os, "resolve_switches": resolve_switches}
        exec(section(root / "env.py", "_DIAG_TRUE", "DIAGNOSTICS_RECOVERY_PROJECT_IDS"), env)
        settings = {"env": SimpleNamespace(**env), "BambooSettings": SimpleNamespace()}
        exec(
            section(
                root / "config/default.py", "PIPELINE_DIAGNOSTICS_SCAN_ENABLED", "DIAGNOSTICS_RECOVERY_PROJECT_IDS"
            ),
            settings,
        )
    return settings


class SettingsWiringTest(TestCase):
    def test_default_env_and_settings_retain_legacy_behavior(self):
        settings = load_switch_settings({})
        self.assertIsNone(settings["DIAGNOSTICS_DETECTION_ENABLED"])
        self.assertTrue(settings["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"])
        self.assertFalse(settings["PIPELINE_DIAGNOSTICS_RECOVERY_ENABLED"])
        self.assertIsNone(settings["DIAGNOSTICS_RECOVERY_POLICY"])

    def test_unified_controls_reach_django_and_bamboo_settings(self):
        for mode, expected in (("off", (False, False)), ("observe", (True, False)), ("enforce", (True, True))):
            settings = load_switch_settings(
                {
                    "BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1",
                    "BKAPP_PIPELINE_FENCE_MODE": mode,
                    "BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "auto",
                }
            )
            engine = settings["BambooSettings"]
            self.assertEqual((engine.FENCE_EMIT_ENABLED, engine.FENCE_ENFORCE), expected)
            self.assertEqual((settings["PIPELINE_FENCE_EMIT_ENABLED"], settings["PIPELINE_FENCE_ENFORCE"]), expected)
            self.assertTrue(settings["PIPELINE_DIAGNOSTICS_WINDOW_SCAN_ENABLED"])
            self.assertTrue(settings["PIPELINE_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED"])
            self.assertTrue(settings["PIPELINE_DIAGNOSTICS_CALLBACK_SCAN_ENABLED"])
            self.assertTrue(settings["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"])
            self.assertTrue(settings["PIPELINE_DIAGNOSTICS_RECOVERY_ENABLED"])
            self.assertEqual(settings["PIPELINE_DIAGNOSTICS_RECOVERY_MODE"], "apply")
            self.assertFalse(engine.SYNC_ADVANCE_CHECKPOINT_ENABLED)
            for name in ("APPLY", "EVENT", "ALERT", "SYNC_ADVANCE"):
                self.assertFalse(settings["PIPELINE_DIAGNOSTICS_{}_ENABLED".format(name)])
            self.assertEqual(settings["DIAGNOSTICS_RECOVERY_PROJECT_IDS"], [])
            self.assertEqual(settings["PIPELINE_DIAGNOSTICS_AUTO_REPLAY_TYPES"], [])

    def test_unrelated_explicit_controls_and_scope_are_preserved(self):
        settings = load_switch_settings(
            {
                "BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "0",
                "BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "off",
                "BKAPP_DIAGNOSTICS_APPLY_ENABLED": "1",
                "BKAPP_DIAGNOSTICS_EVENT_ENABLED": "1",
                "BKAPP_DIAGNOSTICS_ALERT_ENABLED": "1",
                "BKAPP_DIAGNOSTICS_SYNC_ADVANCE_ENABLED": "1",
                "BKAPP_PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED": "1",
                "BKAPP_DIAGNOSTICS_RECOVERY_PROJECT_IDS": "12,34",
                "BKAPP_DIAGNOSTICS_AUTO_REPLAY_TYPES": "sync_advance_stalled",
            }
        )
        self.assertFalse(settings["DIAGNOSTICS_DETECTION_ENABLED"])
        self.assertFalse(settings["PIPELINE_DIAGNOSTICS_RECOVERY_ENABLED"])
        self.assertEqual(settings["DIAGNOSTICS_RECOVERY_POLICY"], "off")
        self.assertTrue(settings["BambooSettings"].SYNC_ADVANCE_CHECKPOINT_ENABLED)
        for name in ("APPLY", "EVENT", "ALERT", "SYNC_ADVANCE"):
            self.assertTrue(settings["PIPELINE_DIAGNOSTICS_{}_ENABLED".format(name)])
        self.assertEqual(settings["DIAGNOSTICS_RECOVERY_PROJECT_IDS"], ["12", "34"])
        self.assertEqual(settings["PIPELINE_DIAGNOSTICS_AUTO_REPLAY_TYPES"], ["sync_advance_stalled"])


class SwitchConfigTest(TestCase):
    def test_unset_preserves_legacy_defaults_including_supplement(self):
        result = resolve_switches({})
        self.assertIsNone(result["DIAGNOSTICS_DETECTION_ENABLED"])
        self.assertTrue(result["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"])
        for name in ("SCAN", "WINDOW_SCAN", "SIGNATURE_SCAN", "CALLBACK_SCAN", "RECOVERY"):
            self.assertFalse(result["DIAGNOSTICS_{}_ENABLED".format(name)])
        self.assertFalse(result["PIPELINE_FENCE_EMIT_ENABLED"])
        self.assertFalse(result["PIPELINE_FENCE_ENFORCE"])
        self.assertIsNone(result["DIAGNOSTICS_RECOVERY_POLICY"])
        self.assertEqual(result["DIAGNOSTICS_RECOVERY_MODE"], "preview")

    def test_every_legacy_scan_combination_is_preserved(self):
        names = [
            "DIAGNOSTICS_{}_ENABLED".format(name) for name in ("SCAN", "WINDOW_SCAN", "SIGNATURE_SCAN", "CALLBACK_SCAN")
        ]
        for values in itertools.product(("0", "1"), repeat=4):
            with self.subTest(values=values):
                result = resolve_switches(dict(zip(["BKAPP_" + name for name in names], values)))
                self.assertEqual([result[name] for name in names], [value == "1" for value in values])
                self.assertTrue(result["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"])

    def test_all_legacy_fence_combinations_including_enforce_without_emit(self):
        for emit, enforce in itertools.product(("0", "1"), repeat=2):
            result = resolve_switches(
                {"BKAPP_PIPELINE_FENCE_EMIT_ENABLED": emit, "BKAPP_PIPELINE_FENCE_ENFORCE": enforce}
            )
            self.assertEqual(result["PIPELINE_FENCE_EMIT_ENABLED"], emit == "1")
            self.assertEqual(result["PIPELINE_FENCE_ENFORCE"], enforce == "1")

    def test_legacy_recovery_disabled_and_preview_are_not_reinterpreted(self):
        for enabled, mode in itertools.product((None, "0", "1"), (None, "preview", "apply")):
            env = {}
            if enabled is not None:
                env["BKAPP_DIAGNOSTICS_RECOVERY_ENABLED"] = enabled
            if mode is not None:
                env["BKAPP_DIAGNOSTICS_RECOVERY_MODE"] = mode
            with self.subTest(env=env):
                result = resolve_switches(env)
                self.assertEqual(result["DIAGNOSTICS_RECOVERY_ENABLED"], enabled == "1")
                self.assertEqual(result["DIAGNOSTICS_RECOVERY_MODE"], mode or "preview")
                self.assertIsNone(result["DIAGNOSTICS_RECOVERY_POLICY"])

    def test_legacy_boolean_parsing_is_unchanged(self):
        for value in ("1", "TRUE", "yes", "on", "0", "false", "", " true ", "typo"):
            result = resolve_switches({"BKAPP_DIAGNOSTICS_SCAN_ENABLED": value})
            self.assertEqual(result["DIAGNOSTICS_SCAN_ENABLED"], value.lower() in ("1", "true", "yes", "on"))

    def test_detection_enables_all_modern_scanners_but_not_legacy_sampling(self):
        result = resolve_switches({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1"})
        self.assertFalse(result["DIAGNOSTICS_SCAN_ENABLED"])
        for name in ("WINDOW_SCAN", "SIGNATURE_SCAN", "CALLBACK_SCAN", "SUPPLEMENT_SCAN"):
            self.assertTrue(result["DIAGNOSTICS_{}_ENABLED".format(name)])

    def test_detection_off_disables_supplement_as_well(self):
        result = resolve_switches({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "0"})
        for name in ("SCAN", "WINDOW_SCAN", "SIGNATURE_SCAN", "CALLBACK_SCAN", "SUPPLEMENT_SCAN"):
            self.assertFalse(result["DIAGNOSTICS_{}_ENABLED".format(name)])

    def test_scanner_selection_can_isolate_callback(self):
        result = resolve_switches(
            {"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1", "BKAPP_DIAGNOSTICS_SCANNERS": " callback "}
        )
        self.assertTrue(result["DIAGNOSTICS_CALLBACK_SCAN_ENABLED"])
        for name in ("SCAN", "WINDOW_SCAN", "SIGNATURE_SCAN", "SUPPLEMENT_SCAN"):
            self.assertFalse(result["DIAGNOSTICS_{}_ENABLED".format(name)])

    def test_empty_scanner_list_explicitly_disables_all_scanners(self):
        result = resolve_switches({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1", "BKAPP_DIAGNOSTICS_SCANNERS": ""})
        self.assertEqual(result["DIAGNOSTICS_SCANNERS"], ())
        self.assertFalse(result["DIAGNOSTICS_SUPPLEMENT_SCAN_ENABLED"])

    def test_scanner_list_requires_explicit_master(self):
        with self.assertRaisesRegex(ValueError, "BKAPP_DIAGNOSTICS_DETECTION_ENABLED"):
            resolve_switches({"BKAPP_DIAGNOSTICS_SCANNERS": "callback"})

    def test_fence_modes_map_to_both_engine_flags(self):
        for mode, expected in (("off", (False, False)), ("observe", (True, False)), ("enforce", (True, True))):
            with self.subTest(mode=mode):
                result = resolve_switches({"BKAPP_PIPELINE_FENCE_MODE": mode})
                self.assertEqual((result["PIPELINE_FENCE_EMIT_ENABLED"], result["PIPELINE_FENCE_ENFORCE"]), expected)

    def test_recovery_policy_maps_to_existing_runtime_contract(self):
        for policy, enabled, mode in (("off", False, "preview"), ("preview", True, "preview"), ("auto", True, "apply")):
            with self.subTest(policy=policy):
                result = resolve_switches({"BKAPP_DIAGNOSTICS_RECOVERY_POLICY": policy})
                self.assertEqual(result["DIAGNOSTICS_RECOVERY_ENABLED"], enabled)
                self.assertEqual(result["DIAGNOSTICS_RECOVERY_MODE"], mode)
                self.assertEqual(result["DIAGNOSTICS_RECOVERY_POLICY"], policy)

    def test_matching_legacy_settings_are_accepted(self):
        env = {
            "BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1",
            "BKAPP_DIAGNOSTICS_SCAN_ENABLED": "0",
            "BKAPP_DIAGNOSTICS_WINDOW_SCAN_ENABLED": "1",
            "BKAPP_PIPELINE_FENCE_MODE": "observe",
            "BKAPP_PIPELINE_FENCE_EMIT_ENABLED": "1",
            "BKAPP_PIPELINE_FENCE_ENFORCE": "0",
            "BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "auto",
            "BKAPP_DIAGNOSTICS_RECOVERY_ENABLED": "1",
            "BKAPP_DIAGNOSTICS_RECOVERY_MODE": "apply",
        }
        self.assertEqual(resolve_switches(env)["DIAGNOSTICS_RECOVERY_MODE"], "apply")

    def test_conflicts_report_the_offending_old_setting(self):
        pairs = (
            ({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "0"}, "BKAPP_DIAGNOSTICS_SIGNATURE_SCAN_ENABLED", "1"),
            ({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1"}, "BKAPP_DIAGNOSTICS_WINDOW_SCAN_ENABLED", "0"),
            ({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1"}, "BKAPP_DIAGNOSTICS_SCAN_ENABLED", "1"),
            ({"BKAPP_PIPELINE_FENCE_MODE": "enforce"}, "BKAPP_PIPELINE_FENCE_EMIT_ENABLED", "0"),
            ({"BKAPP_PIPELINE_FENCE_MODE": "observe"}, "BKAPP_PIPELINE_FENCE_ENFORCE", "1"),
            ({"BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "preview"}, "BKAPP_DIAGNOSTICS_RECOVERY_ENABLED", "0"),
            ({"BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "preview"}, "BKAPP_DIAGNOSTICS_RECOVERY_MODE", "apply"),
            ({"BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "auto"}, "BKAPP_DIAGNOSTICS_RECOVERY_MODE", "preview"),
        )
        for new, key, value in pairs:
            with self.subTest(key=key, new=new):
                with self.assertRaisesRegex(ValueError, key):
                    resolve_switches(dict(new, **{key: value}))

    def test_invalid_new_values_fail_instead_of_silently_enabling_or_disabling(self):
        for key, values in (
            ("BKAPP_DIAGNOSTICS_DETECTION_ENABLED", ("", "maybe", "2")),
            ("BKAPP_PIPELINE_FENCE_MODE", ("", "true", "enforced")),
            ("BKAPP_DIAGNOSTICS_RECOVERY_POLICY", ("", "apply", "automatic")),
        ):
            for value in values:
                with self.subTest(key=key, value=value):
                    with self.assertRaisesRegex(ValueError, key):
                        resolve_switches({key: value})
        with self.assertRaisesRegex(ValueError, "BKAPP_DIAGNOSTICS_SCANNERS"):
            resolve_switches({"BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1", "BKAPP_DIAGNOSTICS_SCANNERS": "calback"})

    def test_new_modes_do_not_enable_unrelated_features(self):
        result = resolve_switches(
            {
                "BKAPP_DIAGNOSTICS_DETECTION_ENABLED": "1",
                "BKAPP_PIPELINE_FENCE_MODE": "enforce",
                "BKAPP_DIAGNOSTICS_RECOVERY_POLICY": "auto",
            }
        )
        for name in ("APPLY", "EVENT", "ALERT", "SYNC_ADVANCE"):
            self.assertNotIn("DIAGNOSTICS_{}_ENABLED".format(name), result)
        self.assertNotIn("PIPELINE_SYNC_ADVANCE_CHECKPOINT_ENABLED", result)

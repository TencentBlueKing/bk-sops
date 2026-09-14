# -*- coding: utf-8 -*-
"""SystemObject persistence and real subprocess transport, without Django settings.

Run with: python -m unittest gcloud.tests.security.test_system_object_portable -v
Workers deliberately disable Linux-only hardening for portable POSIX tests.
"""
import base64
import datetime
import pickle
import subprocess
import sys
from pathlib import Path
from unittest import TestCase, mock

from bamboo_engine.config import Settings as BambooSettings
from bamboo_engine.context import Context
from bamboo_engine.eri import ContextValue, ContextValueType
from bamboo_engine.template import Template, render_backend
from bamboo_engine.utils.object import Representable
from pipeline.eri.imp.serializer import SerializerMixin

from engine_pickle_obj.context import SystemObject

# Frozen BEFORE the fix, from actual engine_pickle_obj.context.SystemObject at
# bk-sops 954419a23afa396fbb9d20200059913a30ad81a2 with Python 3.6.15/engine 2.6.7:
#
# class SystemObject(Representable):
#     def __init__(self, attrs: dict):
#         self.__dict__ = attrs
#
# base64.b64encode(pickle.dumps(SystemObject(sample_attrs()), protocol)).decode()
# Protocol 3 is Python 3.6's default, used by SerializerMixin._serialize.
# Do not regenerate these with the new class: that would lose migration coverage.
OLD_PICKLES = {
    2: (
        "gAJjZW5naW5lX3BpY2tsZV9vYmouY29udGV4dApTeXN0ZW1PYmplY3QKcQApgXEBfXECKFgIAAAAZXhlY3V0b3JxA1gF"
        "AAAAYWxpY2VxBFgHAAAAdGFza19pZHEFSypYCAAAAHNjaGVkdWxlcQZ9cQcoWAQAAABkYXRlcQhjZGF0ZXRpbWUKZGF0"
        "ZQpxCWNfY29kZWNzCmVuY29kZQpxClgFAAAAB8OqCQpxC1gGAAAAbGF0aW4xcQyGcQ1ScQ6FcQ9ScRBYBQAAAGhvc3Rz"
        "cRFdcRIoWAYAAABob3N0LWFxE31xFFgCAAAAaXBxFVgJAAAAMTI3LjAuMC4xcRZzZXV1Yi4="
    ),
    3: (
        "gANjZW5naW5lX3BpY2tsZV9vYmouY29udGV4dApTeXN0ZW1PYmplY3QKcQApgXEBfXECKFgIAAAAZXhlY3V0b3JxA1gF"
        "AAAAYWxpY2VxBFgHAAAAdGFza19pZHEFSypYCAAAAHNjaGVkdWxlcQZ9cQcoWAQAAABkYXRlcQhjZGF0ZXRpbWUKZGF0"
        "ZQpxCUMEB+oJCnEKhXELUnEMWAUAAABob3N0c3ENXXEOKFgGAAAAaG9zdC1hcQ99cRBYAgAAAGlwcRFYCQAAADEyNy4w"
        "LjAuMXESc2V1dWIu"
    ),
    4: (
        "gASVswAAAAAAAACMGWVuZ2luZV9waWNrbGVfb2JqLmNvbnRleHSUjAxTeXN0ZW1PYmplY3SUk5QpgZR9lCiMCGV4ZWN1"
        "dG9ylIwFYWxpY2WUjAd0YXNrX2lklEsqjAhzY2hlZHVsZZR9lCiMBGRhdGWUjAhkYXRldGltZZSMBGRhdGWUk5RDBAfq"
        "CQqUhZRSlIwFaG9zdHOUXZQojAZob3N0LWGUfZSMAmlwlIwJMTI3LjAuMC4xlHNldXViLg=="
    ),
}
OLD_REPR = (
    "<SystemObject: {'executor': 'alice', 'task_id': 42, "
    "'schedule': {'date': datetime.date(2026, 9, 10), 'hosts': ['host-a', {'ip': '127.0.0.1'}]}}>"
)


def sample_attrs():
    return {
        "executor": "alice",
        "task_id": 42,
        "schedule": {"date": datetime.date(2026, 9, 10), "hosts": ["host-a", {"ip": "127.0.0.1"}]},
    }


class SystemObjectCompatibilityTestCase(TestCase):
    def test_dictionary_is_shared_mutable_and_replaceable(self):
        attrs = sample_attrs()
        obj = SystemObject(attrs)
        self.assertIs(vars(obj), attrs)
        attrs["executor"] = "bob"
        self.assertEqual(obj.executor, "bob")
        obj.task_id = 43
        obj.schedule["hosts"].append("host-b")
        self.assertEqual(attrs["task_id"], 43)
        self.assertEqual(attrs["schedule"]["hosts"], ["host-a", {"ip": "127.0.0.1"}, "host-b"])
        del obj.executor
        self.assertNotIn("executor", attrs)
        replacement = {"executor": "carol", "not-an-identifier": 1, 2: "two"}
        obj.__dict__ = replacement
        self.assertIs(vars(obj), replacement)
        self.assertEqual(obj.executor, "carol")
        self.assertEqual(vars(obj)[2], "two")

    def test_dictionary_subclass_is_preserved_but_not_made_portable(self):
        class AttributeDict(dict):
            pass

        attrs = AttributeDict(executor="alice")
        obj = SystemObject(attrs)
        self.assertIs(vars(obj), attrs)
        self.assertEqual(obj.executor, "alice")
        with self.assertRaises(render_backend.UnsupportedContext):
            render_backend._portable_context({"_system": obj})
        for invalid in (None, [], [("executor", "alice")]):
            with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                SystemObject(invalid)

    def test_old_persisted_pickles_load_with_original_attributes_and_display(self):
        serializer = SerializerMixin()
        for protocol, encoded in OLD_PICKLES.items():
            with self.subTest(protocol=protocol):
                obj = serializer._deserialize(encoded, "pickle")
                self.assertIs(type(obj), SystemObject)
                self.assertEqual(vars(obj), sample_attrs())
                self.assertIs(type(obj.schedule["date"]), datetime.date)
                self.assertEqual(str(obj), OLD_REPR)
                self.assertEqual(repr(obj), OLD_REPR)

    def test_new_objects_keep_persistence_identity_and_display(self):
        serializer = SerializerMixin()
        obj = SystemObject(sample_attrs())
        self.assertEqual(str(obj), OLD_REPR)
        self.assertEqual(repr(obj), OLD_REPR)
        encoded, kind = serializer._serialize(obj)
        self.assertEqual(kind, "pickle")
        restored = serializer._deserialize(encoded, kind)
        self.assertIs(type(restored), SystemObject)
        self.assertEqual(type(restored).__module__, "engine_pickle_obj.context")
        self.assertEqual(type(restored).__name__, "SystemObject")
        self.assertEqual(vars(restored), sample_attrs())
        self.assertEqual(repr(restored), OLD_REPR)

    def test_engine_normalizes_system_object_without_losing_data_or_display(self):
        obj = SystemObject(sample_attrs())
        portable = render_backend._portable_context({"_system": obj})["_system"]
        self.assertIs(type(portable), render_backend.PortableRenderObject)
        self.assertEqual(vars(portable), sample_attrs())
        self.assertEqual(str(portable), OLD_REPR)
        self.assertEqual(repr(portable), OLD_REPR)

    def test_pickling_does_not_make_current_or_restored_objects_untransportable(self):
        obj = SystemObject(sample_attrs())
        for protocol in (2, 3, 4):
            restored = pickle.loads(pickle.dumps(obj, protocol=protocol))
            for value in (obj, restored):
                with self.subTest(protocol=protocol, restored=value is restored):
                    portable = render_backend._portable_context({"_system": value})["_system"]
                    self.assertEqual(vars(portable), sample_attrs())
                    self.assertEqual(repr(portable), OLD_REPR)

    def test_inherited_properties_and_other_representable_subclasses_remain_rejected(self):
        class PropertySystemObject(SystemObject):
            @property
            def computed(self):
                raise AssertionError("transport must not evaluate a property")

        class InheritedPropertySystemObject(PropertySystemObject):
            pass

        class OtherRepresentable(Representable):
            def __init__(self, attrs):
                self.__dict__ = attrs

        for kind in (PropertySystemObject, InheritedPropertySystemObject, OtherRepresentable):
            with self.subTest(kind=kind.__name__), self.assertRaises(render_backend.UnsupportedContext):
                render_backend._portable_context({"_system": kind(sample_attrs())})


class SystemObjectSubprocessTestCase(TestCase):
    def setUp(self):
        self.backend = render_backend.SubprocessPoolRenderBackend(
            pool_size=1, timeout=10, fallback_inprocess=False, no_network=False, os_harden=False
        )
        self.addCleanup(self.backend.close)
        spec = render_backend.SandboxSpec("engine", BambooSettings.MAKO_SANDBOX_SHIELD_WORDS, {})
        self.provider = render_backend.SandboxProvider(spec.build, spec)

    def test_newly_persisted_root_context_renders_in_real_worker(self):
        serializer = SerializerMixin()
        root_context = {"${_system}": SystemObject(sample_attrs())}
        encoded, kind = serializer._serialize(root_context)
        self.assertEqual(kind, "pickle")
        restored = serializer._deserialize(encoded, kind)
        for values in (root_context, restored):
            with self.subTest(restored=values is restored):
                self.assertEqual(
                    self.backend.render(
                        "by=${_system.executor};task=${_system.task_id}",
                        {"_system": values["${_system}"]},
                        self.provider,
                    ),
                    "by=alice;task=42",
                )

    def test_old_pickles_render_in_real_worker_that_cannot_import_application_class(self):
        root = Path(__file__).resolve().parents[3]
        worker_paths = [
            path for path in sys.path if root != Path(path).resolve() and root not in Path(path).resolve().parents
        ]
        # Negative control: the same fresh-interpreter import paths cannot load
        # the original persisted app object. No production class hooks or mocks.
        probe = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                "-c",
                "import sys,base64,pickle; sys.path={!r}; pickle.loads(base64.b64decode({!r}))".format(
                    worker_paths, OLD_PICKLES[3]
                ),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        self.assertNotEqual(probe.returncode, 0)
        self.assertIn(b"No module named 'engine_pickle_obj'", probe.stderr)
        template = (
            "by=${_system.executor};date=${_system.schedule['date']};"
            "ip=${_system.schedule['hosts'][1]['ip']};object=${_system};repr=${[_system]}"
        )
        # List display exercises __repr__ without enabling the shielded repr builtin.
        expected = "by=alice;date=2026-09-10;ip=127.0.0.1;object=" + OLD_REPR + ";repr=[" + OLD_REPR + "]"
        with mock.patch.object(sys, "path", worker_paths):
            for protocol, encoded in OLD_PICKLES.items():
                with self.subTest(protocol=protocol):
                    obj = pickle.loads(base64.b64decode(encoded))
                    self.assertEqual(self.backend.render(template, {"_system": obj}, self.provider), expected)

    def test_portable_datetime_forms_render_with_their_values_intact(self):
        offset = datetime.timezone(datetime.timedelta(hours=8))
        cases = [
            (datetime.date(2026, 9, 10), "2026-09-10"),
            (datetime.datetime(2026, 9, 10, 12, 34, 56), "2026-09-10 12:34:56"),
            (datetime.datetime(2026, 9, 10, 12, 34, tzinfo=datetime.timezone.utc), "2026-09-10 12:34:00+00:00"),
            (datetime.datetime(2026, 9, 10, 12, 34, tzinfo=offset), "2026-09-10 12:34:00+08:00"),
            (datetime.time(12, 34, 56), "12:34:56"),
            (datetime.time(12, 34, tzinfo=datetime.timezone.utc), "12:34:00+00:00"),
            (datetime.time(12, 34, tzinfo=offset), "12:34:00+08:00"),
            (datetime.timedelta(days=1, seconds=2), "1 day, 0:00:02"),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                obj = SystemObject({"dates": [{"value": value}]})
                portable = render_backend._portable_context({"_system": obj})["_system"].dates[0]["value"]
                self.assertIs(type(portable), type(value))
                self.assertEqual(portable, value)
                self.assertEqual(
                    self.backend.render("value=${_system.dates[0]['value']}", {"_system": obj}, self.provider),
                    "value=" + expected,
                )

    def test_root_context_hydration_and_template_render_preserve_system_usage(self):
        obj = SerializerMixin()._deserialize(OLD_PICKLES[3], "pickle")
        context = Context(
            runtime=None,  # Plain/splice values require no runtime or database calls.
            values=[
                ContextValue("${_system}", ContextValueType.PLAIN, obj),
                ContextValue("${summary}", ContextValueType.SPLICE, "by=${_system.executor};task=${_system.task_id}"),
            ],
            additional_data={},
        )
        # Inject the real backend while preserving any backend owned by other tests.
        with mock.patch.object(render_backend, "_BACKEND", self.backend), mock.patch.object(
            BambooSettings, "MAKO_TEMPLATE_NAME_EXTRA_WHITELIST", frozenset({"_system", "_loop"})
        ):
            hydrated = context.hydrate()
            self.assertIs(hydrated["${_system}"], obj)
            self.assertEqual(hydrated["${summary}"], "by=alice;task=42")
            data = context.hydrate(deformat=True)
            self.assertIs(Template("${_system}").render(data), obj)
            self.assertEqual(
                Template({"executor": "${_system.executor}", "hosts": ["${_system.schedule['hosts'][0]}"]}).render(
                    data
                ),
                {"executor": "alice", "hosts": ["host-a"]},
            )

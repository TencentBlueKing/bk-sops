# -*- coding: utf-8 -*-

import re
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.test import SimpleTestCase, override_settings

from gcloud.plugin_gateway.services.native_forms import build_component_forms, build_third_party_forms
from pipeline_plugins.components.collections.sites.open.job.execute_task.v2_0 import JobExecuteTaskComponent


@override_settings(BK_SOPS_HOST="https://bksops.example.com/")
class BuildComponentFormsTestCase(SimpleTestCase):
    def test_builds_input_and_output_component_js_descriptors(self):
        class Component:
            code = "job_execute_task"
            form = "/static/components/job.js"
            form_is_embedded = False
            base = "/static/components/base.js"
            output_form = "window.outputForm = true"
            embedded_output_form = True

        self.assertEqual(
            build_component_forms(Component),
            {
                "input": {
                    "type": "component_js",
                    "key": "job_execute_task",
                    "data": "https://bksops.example.com/static/components/job.js",
                    "is_embedded": False,
                    "base": "https://bksops.example.com/static/components/base.js",
                },
                "output": {
                    "type": "component_js",
                    "key": "job_execute_task",
                    "data": "window.outputForm = true",
                    "is_embedded": True,
                    "base": None,
                },
            },
        )

    def test_returns_null_descriptors_when_component_has_no_forms(self):
        class Component:
            code = "bk_http_request"

        self.assertEqual(build_component_forms(Component), {"input": None, "output": None})

    def test_output_key_matches_real_component_output_script_registration(self):
        static_path = urlsplit(JobExecuteTaskComponent.output_form).path
        static_prefix = urlsplit(settings.STATIC_URL).path
        self.assertTrue(static_path.startswith(static_prefix))

        output_script = find(static_path[len(static_prefix) :])
        self.assertIsNotNone(output_script)
        script = Path(output_script).read_text(encoding="utf-8")
        forms = build_component_forms(JobExecuteTaskComponent)
        registration = re.search(r"\$\.atoms\.{}\s*=".format(re.escape(forms["output"]["key"])), script)
        registered_match = re.search(r"\$\.atoms\.([A-Za-z0-9_]+)\s*=", script)

        self.assertIsNotNone(registration)
        self.assertIsNotNone(registered_match)
        registered_key = registered_match.group(1)
        self.assertEqual(registered_key, JobExecuteTaskComponent.code)
        self.assertEqual(forms["output"]["key"], registered_key)


@override_settings(BK_SOPS_HOST="https://bksops.example.com/")
class BuildThirdPartyFormsTestCase(SimpleTestCase):
    def test_builds_renderform_descriptor(self):
        detail = {
            "forms": {
                "renderform": "window.$.atoms.demo = [{tag_code: 'input', attrs: {name: 'x'}}]",
                "is_embedded": True,
            }
        }

        self.assertEqual(
            build_third_party_forms("demo", detail),
            {
                "input": {
                    "type": "renderform",
                    "key": "demo",
                    "data": detail["forms"]["renderform"],
                    "is_embedded": True,
                    "base": None,
                },
                "output": None,
            },
        )

    def test_builds_jsonschema_descriptor(self):
        schema = {"type": "object", "properties": {"x": {"type": "string"}}}

        forms = build_third_party_forms("demo", {"forms": {"jsonschema": schema}})

        self.assertEqual(forms["input"]["type"], "jsonschema")
        self.assertEqual(forms["input"]["data"], schema)
        self.assertTrue(forms["input"]["is_embedded"])

    def test_returns_null_input_when_provider_has_no_native_form(self):
        self.assertEqual(
            build_third_party_forms("demo", {"forms": {}}),
            {"input": None, "output": None},
        )

    def test_does_not_treat_renderform_schema_as_native_renderform(self):
        self.assertEqual(
            build_third_party_forms(
                "demo",
                {"forms": {"renderform": {"type": "object", "properties": {"x": {"type": "string"}}}}},
            ),
            {"input": None, "output": None},
        )

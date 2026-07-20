# -*- coding: utf-8 -*-

from unittest.mock import patch

from django.test import TestCase

from gcloud.plugin_gateway.constants import (
    PLUGIN_SOURCE_BUILTIN,
    PLUGIN_SOURCE_THIRD_PARTY,
    UNIFORM_API_WRAPPER_VERSION,
    decode_plugin_id,
    encode_plugin_id,
)
from gcloud.plugin_gateway.services.builtin_catalog import BuiltinCatalogService
from pipeline_plugins.components.collections.http.v1_0 import HttpComponent


class TestPluginIdCodec(TestCase):
    def test_encode_builtin(self):
        self.assertEqual(encode_plugin_id(PLUGIN_SOURCE_BUILTIN, "job_execute_task"), "builtin__job_execute_task")

    def test_decode_builtin(self):
        self.assertEqual(decode_plugin_id("builtin__job_execute_task"), (PLUGIN_SOURCE_BUILTIN, "job_execute_task"))

    def test_decode_legacy_third_party_is_bare_code(self):
        self.assertEqual(decode_plugin_id("bk_plugin_demo"), (PLUGIN_SOURCE_THIRD_PARTY, "bk_plugin_demo"))


class FakeService:
    def inputs_format(self):
        return []

    def outputs_format(self):
        return []


class FakeComponent:
    code = "job_execute_task"
    name = "执行作业"
    group_name = "JOB"
    version = "legacy"
    bound_service = FakeService


class TestBuiltinCatalog(TestCase):
    @patch("gcloud.plugin_gateway.services.builtin_catalog.ComponentLibrary")
    def test_list_builtin_plugins(self, mock_lib):
        mock_lib.component_list.return_value = [FakeComponent]
        mock_lib.get_component_class.return_value = FakeComponent

        plugins = BuiltinCatalogService.list_plugins()

        self.assertEqual(plugins[0]["plugin_source"], PLUGIN_SOURCE_BUILTIN)
        self.assertEqual(plugins[0]["id"], "builtin__job_execute_task")
        self.assertEqual(plugins[0]["plugin_code"], "job_execute_task")
        self.assertEqual(plugins[0]["category"], "JOB")
        self.assertEqual(plugins[0]["wrapper_version"], UNIFORM_API_WRAPPER_VERSION)
        self.assertIn("legacy", plugins[0]["versions"])

    @patch("gcloud.plugin_gateway.services.builtin_catalog.ComponentLibrary")
    def test_http_detail_exposes_runtime_timeout_input(self, mock_lib):
        mock_lib.get_component_class.return_value = HttpComponent

        detail = BuiltinCatalogService.get_plugin_detail("bk_http_request", "v1.0")

        input_keys = [item["key"] for item in detail["inputs"]]
        self.assertIn("bk_http_timeout", input_keys)
        self.assertNotIn("bk_http_request_timeout", input_keys)

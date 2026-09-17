# -*- coding: utf-8 -*-
"""Regression coverage for the multi-tenant PaaS V3 light-application adapter."""

import importlib
import os
from unittest import TestCase
from unittest.mock import patch

from gcloud.core.api_adapter import app_maker
from gcloud.core.api_adapter.app_maker import v3


class AppMakerAdapterTestCase(TestCase):
    def test_missing_paas_version_does_not_fall_back_to_esb(self):
        for value in (None, "", "3"):
            with self.subTest(major_version=value), patch.dict(os.environ):
                if value is None:
                    os.environ.pop("BKPAAS_MAJOR_VERSION", None)
                else:
                    os.environ["BKPAAS_MAJOR_VERSION"] = value
                adapter = importlib.reload(app_maker)
                for name in (
                    "create_maker_app",
                    "edit_maker_app",
                    "del_maker_app",
                    "modify_app_logo",
                    "get_app_logo_url",
                ):
                    self.assertIs(getattr(adapter, name), getattr(v3, name))

    def test_light_application_operations_preserve_tenant_and_paas_v3_request(self):
        cases = [
            ("create_maker_app", ("operator", "app", "https://app.example.com"), "post"),
            ("edit_maker_app", ("operator", "light-app"), "patch"),
            ("del_maker_app", ("operator", "light-app"), "delete"),
            ("modify_app_logo", ("operator", "light-app", b"logo"), "patch"),
            ("get_app_logo_url", ("light-app",), "get"),
        ]
        for name, args, method in cases:
            with self.subTest(operation=name), patch.object(v3, "_request_paasv3_light_app_api") as request:
                request.return_value = {"result": True, "data": {"light_app_code": "light-app", "logo": "logo-url"}}
                result = getattr(app_maker, name)(*args, tenant_id="tenant-a")
                request.assert_called_once()
                self.assertEqual(request.call_args.kwargs["url"], v3.LIGHT_APP_API)
                self.assertEqual(request.call_args.kwargs["method"], method)
                self.assertEqual(request.call_args.kwargs["tenant_id"], "tenant-a")
                if name == "create_maker_app":
                    self.assertEqual(request.call_args.kwargs["data"]["app_tenant_id"], "tenant-a")
                    self.assertEqual(result["data"]["bk_light_app_code"], "light-app")
                elif name == "get_app_logo_url":
                    self.assertEqual(result, "logo-url")

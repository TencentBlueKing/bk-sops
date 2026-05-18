# -*- coding: utf-8 -*-
import unittest

from django.conf import settings
from django.test import override_settings
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

if not settings.configured:
    settings.configure(
        AUTO_TEST_ENABLE=False,
        AUTO_TEST_SECRET_KEY="",
        AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS=600,
    )

from gcloud.auto_test.apis.permission import (
    AUTO_TEST_SCOPE_COMMON_TEMPLATE,
    AUTO_TEST_SCOPE_TEMPLATE,
    EnablePermission,
    TestTokenPermission,
    generate_token,
    is_auto_test_enabled,
)


class AutoTestPermissionTestCase(unittest.TestCase):
    def test_auto_test_enable_only_accepts_explicit_true_values(self):
        false_values = [None, False, "", "0", "false", "False", "off", "no", "random"]
        for value in false_values:
            with override_settings(AUTO_TEST_ENABLE=value):
                self.assertFalse(is_auto_test_enabled())

        for value in [True, "1", "true", "True", "yes", "on"]:
            with override_settings(AUTO_TEST_ENABLE=value):
                self.assertTrue(is_auto_test_enabled())

    def test_enable_permission_requires_secret_when_enabled(self):
        with override_settings(AUTO_TEST_ENABLE=True, AUTO_TEST_SECRET_KEY=""):
            with self.assertRaises(PermissionDenied):
                EnablePermission().has_permission(request=None, view=None)

    def test_token_signed_by_request_key_is_rejected(self):
        with override_settings(AUTO_TEST_ENABLE=True, AUTO_TEST_SECRET_KEY="server-secret"):
            forged_token = generate_token(
                expire=60, scope=AUTO_TEST_SCOPE_TEMPLATE, project_id=1, secret="attacker-key"
            )
            request = _Request(
                headers={"Auto-Test-Key": "attacker-key", "Auto-Test-Token": forged_token},
                data={"project_id": 1},
            )
            view = _View(auto_test_scope=AUTO_TEST_SCOPE_TEMPLATE, auto_test_require_project_id=True)

            with self.assertRaises(AuthenticationFailed):
                TestTokenPermission().has_permission(request=request, view=view)

    def test_token_scope_and_project_id_must_match_view_and_request(self):
        with override_settings(AUTO_TEST_ENABLE=True, AUTO_TEST_SECRET_KEY="server-secret"):
            token = generate_token(expire=60, scope=AUTO_TEST_SCOPE_TEMPLATE, project_id=1)

            invalid_scope_request = _Request(
                headers={"Auto-Test-Key": "server-secret", "Auto-Test-Token": token},
                data={"project_id": 1},
            )
            invalid_scope_view = _View(auto_test_scope=AUTO_TEST_SCOPE_COMMON_TEMPLATE)
            with self.assertRaises(PermissionDenied):
                TestTokenPermission().has_permission(request=invalid_scope_request, view=invalid_scope_view)

            invalid_project_request = _Request(
                headers={"Auto-Test-Key": "server-secret", "Auto-Test-Token": token},
                data={"project_id": 2},
            )
            valid_scope_view = _View(auto_test_scope=AUTO_TEST_SCOPE_TEMPLATE, auto_test_require_project_id=True)
            with self.assertRaises(PermissionDenied):
                TestTokenPermission().has_permission(request=invalid_project_request, view=valid_scope_view)

            valid_request = _Request(
                headers={"Auto-Test-Key": "server-secret", "Auto-Test-Token": token},
                data={"project_id": 1},
            )
            self.assertTrue(TestTokenPermission().has_permission(request=valid_request, view=valid_scope_view))


class _Request:
    def __init__(self, headers, data=None):
        self.headers = headers
        self.data = data or {}


class _View:
    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)

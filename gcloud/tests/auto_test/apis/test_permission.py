# -*- coding: utf-8 -*-
import importlib
import os
import sys
import types
import unittest
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.test import override_settings
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

if not settings.configured:
    settings.configure(
        AUTO_TEST_ENABLE=False,
        AUTO_TEST_SECRET_KEY="",
        AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS=600,
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )

from gcloud.auto_test.apis.permission import (
    AUTO_TEST_SCOPE_COMMON_TEMPLATE,
    AUTO_TEST_SCOPE_TEMPLATE,
    EnablePermission,
    TestTokenPermission,
    generate_token,
    is_auto_test_enabled,
)

_drf_yasg_utils = types.ModuleType("drf_yasg.utils")
_drf_yasg_utils.swagger_auto_schema = lambda *args, **kwargs: lambda func: func
_drf_yasg = types.ModuleType("drf_yasg")
_drf_yasg.utils = _drf_yasg_utils
_gcloud_core_viewsets = types.ModuleType("gcloud.core.apis.drf.viewsets")
_gcloud_core_viewsets.ApiMixin = object
with patch.dict(
    sys.modules,
    {
        "drf_yasg": _drf_yasg,
        "drf_yasg.utils": _drf_yasg_utils,
        "gcloud.core.apis.drf.viewsets": _gcloud_core_viewsets,
    },
):
    from gcloud.auto_test.apis.mixin import BatchDeleteMixin


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


class AutoTestBatchDeleteTestCase(unittest.TestCase):
    def test_batch_delete_uses_soft_delete_when_model_has_is_deleted_field(self):
        queryset = _QuerySet(field_names={"is_deleted"})
        view = _BatchDeleteView(queryset=queryset)

        response = view.batch_delete(_Request(headers={}, data={"ids_list": [1, 2]}))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(queryset.filter_calls, [{"id__in": [1, 2]}])
        self.assertEqual(queryset.update_calls, [{"is_deleted": True}])
        self.assertEqual(queryset.delete_call_count, 0)

    def test_batch_delete_hard_deletes_only_when_model_has_no_is_deleted_field(self):
        queryset = _QuerySet(field_names=set())
        view = _BatchDeleteView(queryset=queryset)

        response = view.batch_delete(_Request(headers={}, data={"ids_list": [1, 2]}))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(queryset.update_calls, [])
        self.assertEqual(queryset.delete_call_count, 1)

    def test_batch_delete_does_not_fallback_to_hard_delete_when_soft_delete_fails(self):
        queryset = _QuerySet(field_names={"is_deleted"}, update_exception=RuntimeError("db error"))
        view = _BatchDeleteView(queryset=queryset)

        with self.assertRaises(RuntimeError):
            view.batch_delete(_Request(headers={}, data={"ids_list": [1, 2]}))

        self.assertEqual(queryset.update_calls, [{"is_deleted": True}])
        self.assertEqual(queryset.delete_call_count, 0)


class AutoTestEnvTestCase(unittest.TestCase):
    def test_invalid_token_max_expire_seconds_falls_back_to_default(self):
        dummy_env_v2 = types.ModuleType("env_v2")
        dummy_env_v2.json = __import__("json")

        with patch.dict(sys.modules, {"env_v2": dummy_env_v2}):
            with patch.dict(os.environ, {"BKAPP_AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS": "disabled"}):
                sys.modules.pop("env", None)

                env = importlib.import_module("env")

        self.assertEqual(env.AUTO_TEST_TOKEN_MAX_EXPIRE_SECONDS, 600)
        sys.modules.pop("env", None)


class _Request:
    def __init__(self, headers, data=None):
        self.headers = headers
        self.data = data or {}


class _View:
    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)


class _BatchDeleteView(BatchDeleteMixin):
    def __init__(self, queryset):
        self.queryset = queryset


class _QuerySet:
    def __init__(self, field_names, update_exception=None):
        self.model = _Model(field_names)
        self.update_exception = update_exception
        self.filter_calls = []
        self.update_calls = []
        self.delete_call_count = 0

    def filter(self, **kwargs):
        self.filter_calls.append(kwargs)
        return self

    def update(self, **kwargs):
        self.update_calls.append(kwargs)
        if self.update_exception:
            raise self.update_exception

    def delete(self):
        self.delete_call_count += 1


class _Model:
    def __init__(self, field_names):
        self._meta = _Meta(field_names)


class _Meta:
    def __init__(self, field_names):
        self.field_names = field_names

    def get_field(self, name):
        if name not in self.field_names:
            raise FieldDoesNotExist(name)
        return name

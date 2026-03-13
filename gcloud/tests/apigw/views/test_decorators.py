# -*- coding: utf-8 -*-
import sys
from types import ModuleType
from unittest import TestCase
from unittest.mock import MagicMock

import django.conf

if not django.conf.settings.configured:
    django.conf.settings.configure(
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )

_conf_mod = ModuleType("gcloud.conf")
_settings = MagicMock()
_settings.APIGW_AI_PLATFORM_HEADER = "HTTP_X_BKAPI_AI_PLATFORM"
_settings.APIGW_AI_SKILL_HEADER = "HTTP_X_BKAPI_AI_SKILL"
_settings.APIGW_ALLOWED_AI_PLATFORMS = ("openclaw",)
_settings.APIGW_MANAGER_APP_CODE_KEY = "app_code"
_conf_mod.settings = _settings
sys.modules["gcloud.conf"] = _conf_mod

for _mod in [
    "iam",
    "iam.exceptions",
    "gcloud.err_code",
    "gcloud.core.models",
    "gcloud.apigw.constants",
    "gcloud.apigw.exceptions",
    "gcloud.apigw.utils",
    "gcloud.apigw.whitelist",
]:
    sys.modules.setdefault(_mod, MagicMock())

from gcloud.apigw.decorators import (  # noqa: E402
    get_ai_platform_from_request,
    get_request_task_create_method,
    is_ai_platform_request,
    mark_ai_platform,
)
from gcloud.constants import TaskCreateMethod  # noqa: E402


class _FakeRequest:
    def __init__(self, meta=None, **attrs):
        self.META = meta or {}
        for key, value in attrs.items():
            setattr(self, key, value)


class GetAiPlatformFromRequestTest(TestCase):
    def test_returns_platform_when_header_present(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "openclaw"})
        self.assertEqual(get_ai_platform_from_request(request), "openclaw")

    def test_returns_empty_string_when_header_absent(self):
        request = _FakeRequest()
        self.assertEqual(get_ai_platform_from_request(request), "")

    def test_returns_empty_string_when_header_is_whitespace(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "   "})
        self.assertEqual(get_ai_platform_from_request(request), "")

    def test_strips_whitespace(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "  openclaw  "})
        self.assertEqual(get_ai_platform_from_request(request), "openclaw")

    def test_returns_empty_string_when_platform_is_not_allowed(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "competitor_platform"})
        self.assertEqual(get_ai_platform_from_request(request), "")


class IsAiPlatformRequestTest(TestCase):
    def test_returns_true_when_platform_is_allowed(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "openclaw"})
        self.assertTrue(is_ai_platform_request(request))

    def test_returns_false_when_platform_is_not_allowed(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "competitor_platform"})
        self.assertFalse(is_ai_platform_request(request))


class GetRequestTaskCreateMethodTest(TestCase):
    def test_returns_ai_platform_create_method(self):
        request = _FakeRequest(ai_platform="openclaw")
        self.assertEqual(get_request_task_create_method(request), TaskCreateMethod.OPENCLAW.value)

    def test_mcp_takes_priority_over_ai_platform(self):
        request = _FakeRequest(ai_platform="openclaw", is_mcp_request=True)
        self.assertEqual(get_request_task_create_method(request), TaskCreateMethod.MCP.value)

    def test_returns_api_when_no_valid_source(self):
        request = _FakeRequest(ai_platform="")
        self.assertEqual(get_request_task_create_method(request), TaskCreateMethod.API.value)


class MarkAiPlatformDecoratorTest(TestCase):
    def test_injects_ai_platform_and_skill(self):
        request = _FakeRequest(
            {
                "HTTP_X_BKAPI_AI_PLATFORM": "openclaw",
                "HTTP_X_BKAPI_AI_SKILL": "sops-task-execution",
            }
        )

        @mark_ai_platform
        def dummy_view(request):
            return {"result": True}

        dummy_view(request)
        self.assertEqual(request.ai_platform, "openclaw")
        self.assertEqual(request.ai_skill, "sops-task-execution")

    def test_empty_when_no_headers(self):
        request = _FakeRequest()

        @mark_ai_platform
        def dummy_view(request):
            return {"result": True}

        dummy_view(request)
        self.assertEqual(request.ai_platform, "")
        self.assertEqual(request.ai_skill, "")

    def test_ignores_skill_when_platform_is_not_allowed(self):
        request = _FakeRequest(
            {
                "HTTP_X_BKAPI_AI_PLATFORM": "competitor_platform",
                "HTTP_X_BKAPI_AI_SKILL": "sops-task-execution",
            }
        )

        @mark_ai_platform
        def dummy_view(request):
            return {"result": True}

        dummy_view(request)
        self.assertEqual(request.ai_platform, "")
        self.assertEqual(request.ai_skill, "")

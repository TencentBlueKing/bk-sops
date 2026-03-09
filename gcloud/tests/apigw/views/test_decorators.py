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

from gcloud.apigw.decorators import is_ai_platform_request, mark_ai_platform  # noqa: E402


class _FakeRequest:
    def __init__(self, meta=None):
        self.META = meta or {}


class IsAiPlatformRequestTest(TestCase):
    def test_returns_platform_when_header_present(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "openclaw"})
        self.assertEqual(is_ai_platform_request(request), "openclaw")

    def test_returns_empty_string_when_header_absent(self):
        request = _FakeRequest()
        self.assertEqual(is_ai_platform_request(request), "")

    def test_returns_empty_string_when_header_is_whitespace(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "   "})
        self.assertEqual(is_ai_platform_request(request), "")

    def test_strips_whitespace(self):
        request = _FakeRequest({"HTTP_X_BKAPI_AI_PLATFORM": "  openclaw  "})
        self.assertEqual(is_ai_platform_request(request), "openclaw")


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

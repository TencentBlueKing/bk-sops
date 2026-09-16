from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from gcloud.core.context_processors import _ai_sops_agent_plugin_url, _cmdb_create_business_url


class CmdbCreateBusinessUrlTest(SimpleTestCase):
    @override_settings(BK_CC_HOST=None)
    def test_missing_cmdb_host_does_not_break_page_rendering(self):
        self.assertEqual(_cmdb_create_business_url(), "")

    @override_settings(BK_CC_HOST="https://cmdb.example.test/")
    def test_builds_current_cmdb_business_create_route(self):
        self.assertEqual(
            _cmdb_create_business_url(),
            "https://cmdb.example.test/#/resource/business?create=true",
        )


class AiSopsAgentPluginUrlTest(SimpleTestCase):
    @patch("gcloud.core.context_processors.env.AI_SOPS_AGENT_URL", "")
    def test_missing_agent_host_keeps_ai_disabled(self):
        self.assertEqual(_ai_sops_agent_plugin_url(), "")

    @patch("gcloud.core.context_processors.env.AI_SOPS_AGENT_URL", "https://agent.example.test/prod/")
    def test_builds_plugin_api_url_without_duplicate_slash(self):
        self.assertEqual(
            _ai_sops_agent_plugin_url(),
            "https://agent.example.test/prod/bk_plugin/plugin_api/",
        )

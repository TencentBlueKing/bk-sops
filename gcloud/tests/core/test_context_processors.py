from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings

from gcloud.core import context_processors


@override_settings(
    BK_IAM_SAAS_HOST="https://iam.example.test",
    BK_API_URL_TMPL="https://{api_name}.example.test",
    CUSTOM_HOME_RENDER_CONTEXT={},
)
class AiContextTestCase(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.request.user = SimpleNamespace(username="tester", tenant_id="tenant", is_superuser=False)
        self.request.session = {}
        for name, return_value in (
            ("is_user_functor", False),
            ("is_user_auditor", False),
            ("get_default_project_for_user", None),
            ("get_user_timezone", "Asia/Shanghai"),
            ("get_cur_pos_from_url", ""),
            ("get_default_asymmetric_key_config", SimpleNamespace(public_key_string="test-public-key")),
        ):
            self.enterContext(patch.object(context_processors, name, return_value=return_value))
        self.enterContext(
            patch.object(
                context_processors.EnvironmentVariables.objects, "get_var", side_effect=lambda key, default: default
            )
        )

    def test_missing_agent_disables_all_agent_entry_points_even_when_notifications_are_enabled(self):
        for host in ("", None, " \t "):
            with self.subTest(host=host), patch.multiple(
                context_processors.env, AI_SOPS_AGENT_URL=host, ENABLE_AI_NOTIFICATION=1
            ):
                context = context_processors.mysetting(self.request)

                self.assertEqual(context["AI_SOPS_AGENT_URL"], "")
                self.assertEqual(context["ENABLE_AI_NOTIFICATION"], 0)

    def test_configured_agent_preserves_stage_and_normalizes_trailing_slashes(self):
        for host in (
            "https://agent.example.test/prod",
            "https://agent.example.test/prod/",
            " https://agent.example.test/prod/ ",
        ):
            with self.subTest(host=host), patch.multiple(
                context_processors.env, AI_SOPS_AGENT_URL=host, ENABLE_AI_NOTIFICATION=1
            ):
                context = context_processors.mysetting(self.request)

                self.assertEqual(context["AI_SOPS_AGENT_URL"], "https://agent.example.test/prod/bk_plugin/plugin_api/")
                self.assertEqual(context["ENABLE_AI_NOTIFICATION"], 1)

    @patch.multiple(
        context_processors.env, AI_SOPS_AGENT_URL="https://agent.example.test/prod", ENABLE_AI_NOTIFICATION=0
    )
    def test_notification_switch_remains_independent_when_agent_is_configured(self):
        context = context_processors.mysetting(self.request)

        self.assertTrue(context["AI_SOPS_AGENT_URL"])
        self.assertEqual(context["ENABLE_AI_NOTIFICATION"], 0)

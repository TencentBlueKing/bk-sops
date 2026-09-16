# -*- coding: utf-8 -*-
from unittest.mock import patch

from django.test import SimpleTestCase

from api.ai_sops_agent import AgentRequestType, BKSopsAgentClient


class AgentEndpointTestCase(SimpleTestCase):
    @patch("api.ai_sops_agent.requests.request")
    @patch("api.ai_sops_agent.env.AI_SOPS_AGENT_URL", "https://agent.example.com/prod")
    @patch("api.ai_sops_agent.env.BKAPP_APIGW_ENVIRONMENT", "stag")
    def test_user_endpoint_uses_configured_stage_without_adding_another(self, request):
        client = BKSopsAgentClient("", AgentRequestType.USER, "tester")

        client._make_request("POST", data={"input": "test"}, timeout=10)

        self.assertEqual(
            request.call_args.kwargs["url"],
            "https://agent.example.com/prod/bk_plugin/openapi/agent/chat_completion/",
        )
        self.assertEqual(request.call_args.kwargs["headers"]["X-BKAIDEV-USER"], "tester")

    @patch("api.ai_sops_agent.requests.request")
    @patch("api.ai_sops_agent.env.AI_SOPS_AGENT_URL", "https://agent.example.com/prod")
    def test_explicit_agent_endpoint_is_preserved(self, request):
        client = BKSopsAgentClient("https://custom.example.com/test", AgentRequestType.USER, "tester")

        client._make_request("POST", data={"input": "test"}, timeout=10)

        self.assertEqual(
            request.call_args.kwargs["url"],
            "https://custom.example.com/test/bk_plugin/openapi/agent/chat_completion/",
        )

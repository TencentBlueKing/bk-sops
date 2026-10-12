# -*- coding: utf-8 -*-
import io
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml
from bkai_init import BkaiInit
from django.template import Context, Engine

from gcloud.contrib.sync_agent.management.commands import sync_agent

ROOT = Path(__file__).resolve().parents[4]


class SyncAgentSwitchTest(unittest.TestCase):
    @patch.object(sync_agent, "BkaiInit")
    def test_disabled_or_unknown_values_never_initialize_remote_client(self, initializer):
        for value in (None, "", "0", "false", "False", " FALSE ", "no", "off", "unexpected"):
            with self.subTest(value=value), patch.dict(os.environ, {}, clear=True):
                if value is not None:
                    os.environ["BKAI_SYNC_ENABLED"] = value
                stdout = io.StringIO()
                sync_agent.Command(stdout=stdout).handle()
                initializer.assert_not_called()
                self.assertIn("已跳过", stdout.getvalue())

    @patch.object(sync_agent, "BkaiInit")
    def test_explicit_true_values_sync_once(self, initializer):
        settings = SimpleNamespace(
            BK_API_URL_TMPL="https://{api_name}.example.com",
            BK_APIGW_STAGE_NAME="prod",
            APP_CODE="example-app",
            SECRET_KEY="test-only",
            BASE_DIR=str(ROOT),
        )
        for value in ("1", "true", "True", " TRUE ", "yes", "on"):
            with self.subTest(value=value), patch.dict(os.environ, {"BKAI_SYNC_ENABLED": value}, clear=True):
                initializer.reset_mock()
                with patch.object(sync_agent, "settings", settings):
                    sync_agent.Command(stdout=io.StringIO()).handle()
                initializer.return_value.sync.assert_called_once_with(
                    str(ROOT / "ai-agent/bkai.yaml"), publish=True, publish_config_only=False
                )


class AgentPackageSafetyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = yaml.safe_load((ROOT / "ai-agent/agents/ai-sops.yaml").read_text())
        definition = (ROOT / "gcloud/apigw/management/commands/data/api-definition.yml").read_text()
        cls.gateway = yaml.safe_load(Engine().from_string(definition).render(Context({})))

    def test_package_validation_does_not_include_knowledgebase_imports(self):
        report = BkaiInit().validate(ROOT / "ai-agent/bkai.yaml")
        self.assertTrue(report.events)
        self.assertNotIn("KnowledgeBase", {event.kind for event in report.events})
        # Omitting this field preserves existing bindings rather than sending an empty list.
        self.assertNotIn("knowledgebases", self.agent["spec"])

    def test_agent_selects_only_registered_read_only_tools(self):
        servers = {server["name"]: server for server in self.gateway["stages"][0]["mcp_servers"]}
        for binding in self.agent["spec"]["mcps"]:
            with self.subTest(mcp=binding["code"]):
                self.assertIs(binding["is_selected_all"], False)
                names = [tool["tool_name"] for tool in binding["selected_tools"]]
                # An empty selection may fall back to loading all tools in the runtime.
                self.assertTrue(names)
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(all(name.startswith("get_") or name == "preview_task_tree" for name in names))
                server = servers[binding["code"].removeprefix("bk-sops-prod-")]
                self.assertLessEqual(set(names), set(server["resource_names"]))

    def test_gateway_retains_write_tools_for_other_clients(self):
        servers = {server["name"]: set(server["resource_names"]) for server in self.gateway["stages"][0]["mcp_servers"]}
        self.assertLessEqual(
            {"create_task", "start_task", "operate_task", "operate_node", "node_callback"}, servers["task"]
        )
        self.assertLessEqual(
            {
                "create_periodic_task",
                "modify_constants_for_periodic_task",
                "modify_cron_for_periodic_task",
                "set_periodic_task_enabled",
            },
            servers["periodic"],
        )

    def test_gateway_keeps_existing_backend_timeout(self):
        self.assertEqual(self.gateway["stages"][0]["backends"][0]["config"]["timeout"], 120)

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from apigw_manager.apigw.management.commands.fetch_esb_public_key import Command as FetchEsbPublicKeyCommand
from apigw_manager.core.exceptions import ApiResponseError
from bkapi_client_core.exceptions import HTTPResponseError
from django.core.management.base import CommandError
from requests import Response

from gcloud.apigw.management.commands import sync_saas_apigw


class SyncSaasApigwTest(unittest.TestCase):
    def setUp(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.command = sync_saas_apigw.Command(stdout=self.stdout, stderr=self.stderr)
        self.paas = patch.object(sync_saas_apigw.env, "IS_PAAS_V3", True)
        self.paas.start()
        self.addCleanup(self.paas.stop)
        self.output = redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    @patch.object(sync_saas_apigw, "call_command")
    def test_success_runs_resource_docs_release_and_permissions(self, call_command):
        self.command.handle()
        self.assertEqual(
            [call.args[0] for call in call_command.call_args_list],
            [
                "sync_apigw_config",
                "sync_apigw_stage",
                "sync_apigw_resources",
                "sync_resource_docs_by_archive",
                "create_version_and_release_apigw",
                "grant_apigw_permissions",
                "fetch_apigw_public_key",
                "fetch_esb_public_key",
            ],
        )
        self.assertEqual(self.stderr.getvalue(), "")

    @patch.object(sync_saas_apigw, "call_command")
    def test_non_paas_v3_does_not_sync(self, call_command):
        with patch.object(sync_saas_apigw.env, "IS_PAAS_V3", False):
            self.command.handle()
        call_command.assert_not_called()

    def test_resource_failure_preserves_error_and_stops_release(self):
        for error in (SystemExit(1), CommandError("duplicate operationId"), RuntimeError("sync failed")):
            with self.subTest(error=type(error).__name__):
                self.stderr.seek(0)
                self.stderr.truncate()
                with patch.object(sync_saas_apigw, "call_command", side_effect=[None, None, error]) as call_command:
                    with self.assertRaises(type(error)) as raised:
                        self.command.handle()
                self.assertIs(raised.exception, error)
                self.assertEqual(call_command.call_count, 3)
                self.assertIn("apigw_log_resource_migration.md", self.stderr.getvalue())
                self.assertIn("后续文档同步和版本发布未执行", self.stderr.getvalue())

    @patch.object(sync_saas_apigw, "call_command", side_effect=[None, None, SystemExit(0)])
    def test_successful_exit_does_not_print_failure(self, call_command):
        with self.assertRaises(SystemExit) as raised:
            self.command.handle()
        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(self.stderr.getvalue(), "")

    @staticmethod
    def raise_public_key_error(status):
        response = Response()
        response.status_code = status
        try:
            raise HTTPResponseError("public key request failed", response=response)
        except HTTPResponseError:
            # Match apigw-manager's wrapping without serializing authorization headers.
            raise ApiResponseError("public key request failed")

    def call_esb_command(self, status):
        # Exercise the installed dependency's real SystemExit wrapper; never call HTTP or save a key.
        command = FetchEsbPublicKeyCommand(stderr=io.StringIO())
        manager = Mock()
        manager.public_key.side_effect = lambda: self.raise_public_key_error(status)
        with patch.object(command, "get_configuration"), patch.object(command, "manager_class", return_value=manager):
            command.handle(gateway_name="bk-sops")

    def test_missing_esb_key_system_exit_does_not_fail_sync(self):
        def call(name, *args, **kwargs):
            if name == "fetch_esb_public_key":
                self.call_esb_command(404)

        with patch.object(sync_saas_apigw, "call_command", side_effect=call):
            self.command.handle()
        self.assertIn("HTTP 404", self.stdout.getvalue())
        self.assertIn("继续发布", self.stdout.getvalue())

    def test_missing_esb_key_api_error_does_not_fail_sync(self):
        def call(name, *args, **kwargs):
            if name == "fetch_esb_public_key":
                self.raise_public_key_error(404)

        with patch.object(sync_saas_apigw, "call_command", side_effect=call):
            self.command.handle()
        self.assertIn("HTTP 404", self.stdout.getvalue())

    def test_esb_auth_and_server_errors_still_fail_sync(self):
        for status in (401, 403, 500):
            with self.subTest(status=status):
                self.stdout.seek(0)
                self.stdout.truncate()

                def call(name, *args, **kwargs):
                    if name == "fetch_esb_public_key":
                        self.call_esb_command(status)

                with patch.object(sync_saas_apigw, "call_command", side_effect=call):
                    with self.assertRaises(SystemExit) as raised:
                        self.command.handle()
                self.assertEqual(raised.exception.code, 1)
                self.assertEqual(self.stdout.getvalue(), "")

    def test_unknown_esb_failures_are_not_treated_as_missing_gateway(self):
        for error in (SystemExit(1), RuntimeError("status_code: 404"), CommandError("request timed out")):
            with self.subTest(error=type(error).__name__):
                with patch.object(sync_saas_apigw, "call_command", side_effect=[None] * 7 + [error]):
                    with self.assertRaises(type(error)) as raised:
                        self.command.handle()
                self.assertIs(raised.exception, error)

    def test_required_gateway_key_404_still_fails_sync(self):
        def call(name, *args, **kwargs):
            if name == "fetch_apigw_public_key":
                self.call_esb_command(404)

        with patch.object(sync_saas_apigw, "call_command", side_effect=call) as call_command:
            with self.assertRaises(SystemExit):
                self.command.handle()
        self.assertEqual(call_command.call_args.args[0], "fetch_apigw_public_key")
        self.assertEqual(self.stdout.getvalue(), "")


class PreReleaseTest(unittest.TestCase):
    commands = [
        "migrate",
        "createcachetable",
        "update_component_models",
        "update_variable_models",
        "sync_saas_apigw",
        "register_bksops_notice",
        "sync_webhook_events",
    ]

    def run_pre_release(self, fail_command=""):
        # Replace python so no real migration, gateway or notification can run.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            python = root / "python"
            python.write_text(
                "#!/bin/bash\n"
                'printf "%s\\n" "$2" >> "$TEST_COMMAND_LOG"\n'
                'if [ "$2" = "$TEST_FAIL_COMMAND" ]; then exit 23; fi\n'
            )
            python.chmod(0o755)
            log = root / "commands.log"
            result = subprocess.run(
                ["/bin/bash", str(Path(__file__).resolve().parents[3] / "bin/pre_release")],
                cwd=directory,
                env={
                    "PATH": directory + os.pathsep + os.defpath,
                    "TEST_COMMAND_LOG": str(log),
                    "TEST_FAIL_COMMAND": fail_command,
                },
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode, log.read_text().splitlines()

    def test_success_runs_all_initialization_steps(self):
        code, commands = self.run_pre_release()
        self.assertEqual(code, 0)
        self.assertEqual(commands, self.commands)

    def test_failure_stops_at_failed_step_and_preserves_exit_code(self):
        for index, command in enumerate(self.commands):
            with self.subTest(command=command):
                code, commands = self.run_pre_release(command)
                self.assertEqual(code, 23)
                self.assertEqual(commands, self.commands[: index + 1])

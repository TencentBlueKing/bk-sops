# -*- coding: utf-8 -*-

from django.test import TestCase

from gcloud.plugin_gateway.services.builtin_form_schema import build_builtin_form_schema


class TestBuiltinFormSchema(TestCase):
    def test_job_script_content_uses_code_editor(self):
        schema = build_builtin_form_schema(
            "job_fast_execute_script",
            [
                {
                    "key": "job_content",
                    "name": "脚本内容",
                    "type": "string",
                    "required": True,
                    "schema": {"type": "string", "description": "待执行的脚本内容"},
                }
            ],
        )

        field = schema["properties"]["job_content"]
        self.assertEqual(field["ui:component"]["name"], "codeEditor")
        self.assertEqual(field["ui:component"]["props"]["language"], "shell")
        self.assertEqual(field["ui:component"]["props"]["height"], "400px")
        self.assertEqual(schema["required"], ["job_content"])

    def test_http_multiline_fields_use_textarea(self):
        schema = build_builtin_form_schema(
            "bk_http_request",
            [
                {
                    "key": "bk_http_request_body",
                    "name": "HTTP 请求 body",
                    "type": "string",
                    "schema": {"type": "string", "description": "HTTP 请求 body"},
                },
                {
                    "key": "bk_http_success_exp",
                    "name": "HTTP 请求成功条件",
                    "type": "string",
                    "schema": {"type": "string", "description": "成功条件"},
                },
            ],
        )

        self.assertEqual(schema["properties"]["bk_http_request_body"]["ui:component"]["name"], "textarea")
        self.assertEqual(schema["properties"]["bk_http_success_exp"]["ui:component"]["name"], "textarea")

    def test_nested_nodeman_auth_key_uses_password(self):
        schema = build_builtin_form_schema(
            "nodeman_create_task",
            [
                {
                    "key": "nodeman_hosts",
                    "name": "主机",
                    "type": "array",
                    "schema": {
                        "type": "array",
                        "description": "主机",
                        "items": {
                            "type": "object",
                            "description": "主机信息",
                            "properties": {
                                "auth_key": {
                                    "type": "string",
                                    "description": "认证密钥",
                                }
                            },
                        },
                    },
                }
            ],
        )

        field = schema["properties"]["nodeman_hosts"]["items"]["properties"]["auth_key"]
        self.assertEqual(field["ui:component"]["name"], "password")

    def test_component_without_overrides_keeps_flat_input_contract(self):
        self.assertIsNone(build_builtin_form_schema("job_execute_task", []))

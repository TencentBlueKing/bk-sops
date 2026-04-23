from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase

from gcloud.plugin_gateway.constants import PLUGIN_SOURCE_THIRD_PARTY
from gcloud.plugin_gateway.services.catalog import PluginGatewayCatalogService


class PluginGatewayCatalogServiceTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/apigw/plugin-gateway/plugins/")

    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_plugin_list_contains_category_and_versions(self, mock_client_cls):
        mock_client = Mock()
        mock_client.get_meta.return_value = {
            "result": True,
            "data": {
                "description": "remote plugin",
                "versions": ["1.0.0", "1.1.0"],
                "framework_version": "2.0.0",
                "runtime_version": "3.11",
            },
        }
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {"plugins": [{"code": "bk_plugin_demo", "name": "Demo Plugin"}]},
        }
        mock_client_cls.return_value = mock_client

        meta = PluginGatewayCatalogService.get_plugin_list(request=self.request)

        self.assertEqual(len(meta["apis"]), 1)
        plugin = meta["apis"][0]
        self.assertEqual(plugin["id"], "bk_plugin_demo")
        self.assertEqual(plugin["plugin_source"], PLUGIN_SOURCE_THIRD_PARTY)
        self.assertEqual(plugin["category"], PLUGIN_SOURCE_THIRD_PARTY)
        self.assertEqual(plugin["default_version"], "1.1.0")
        self.assertEqual(plugin["latest_version"], "1.1.0")
        self.assertEqual(plugin["versions"], ["1.0.0", "1.1.0"])
        self.assertIn("/apigw/plugin-gateway/plugins/bk_plugin_demo/", plugin["meta_url_template"])

    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_plugin_detail_converts_json_schema_inputs_and_outputs(self, mock_client_cls):
        mock_client = Mock()
        mock_client.get_meta.return_value = {
            "result": True,
            "data": {
                "description": "remote plugin",
                "versions": ["1.0.0", "1.1.0"],
                "framework_version": "2.0.0",
                "runtime_version": "3.11",
            },
        }
        mock_client.get_detail.return_value = {
            "result": True,
            "data": {
                "version": "1.1.0",
                "inputs": {
                    "properties": {
                        "biz_id": {
                            "title": "业务ID",
                            "type": "integer",
                            "description": "业务 ID",
                            "default": 2,
                        }
                    },
                    "required": ["biz_id"],
                },
                "outputs": {
                    "properties": {
                        "job_instance_id": {
                            "title": "作业实例 ID",
                            "type": "integer",
                            "description": "JOB instance id",
                        }
                    }
                },
                "context_inputs": {"properties": {}},
            },
        }
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {"plugins": [{"code": "bk_plugin_demo", "name": "Demo Plugin"}]},
        }
        mock_client_cls.return_value = mock_client

        detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="bk_plugin_demo",
            version="1.1.0",
        )

        self.assertEqual(detail["plugin_version"], "1.1.0")
        self.assertEqual(detail["plugin_source"], PLUGIN_SOURCE_THIRD_PARTY)
        self.assertEqual(
            detail["inputs"],
            [
                {
                    "key": "biz_id",
                    "name": "业务ID",
                    "type": "integer",
                    "description": "业务 ID",
                    "required": True,
                    "default": 2,
                }
            ],
        )
        self.assertEqual(
            detail["outputs"],
            [
                {
                    "key": "job_instance_id",
                    "name": "作业实例 ID",
                    "type": "integer",
                    "description": "JOB instance id",
                }
            ],
        )
        self.assertIn("/apigw/plugin-gateway/runs/", detail["url"])
        self.assertIn("/apigw/plugin-gateway/runs/status/", detail["polling"]["url"])

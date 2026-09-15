from threading import Barrier
from unittest.mock import call, patch

from django.test import RequestFactory, TestCase, override_settings

from gcloud.core.models import Project
from gcloud.plugin_gateway.constants import (
    PLUGIN_SOURCE_BUILTIN,
    PLUGIN_SOURCE_THIRD_PARTY,
    UNIFORM_API_WRAPPER_VERSION,
)
from gcloud.plugin_gateway.exceptions import PluginGatewaySourceUnavailableError, PluginGatewayVersionNotFoundError
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.catalog import PluginGatewayCatalogService
from plugin_service.conf import PLUGIN_DISTRIBUTOR_NAME
from plugin_service.plugin_client import PluginServiceApiClient


class PluginGatewayCatalogServiceTestCase(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/apigw/plugin-gateway/plugins/")
        self._clear_catalog_caches()

    def tearDown(self):
        self._clear_catalog_caches()

    def _clear_catalog_caches(self):
        for func_name in [
            "_list_plugins",
            "_list_third_party_plugins",
            "_get_plugin_meta",
            "_get_plugin_detail_schema",
        ]:
            descriptor = PluginGatewayCatalogService.__dict__.get(func_name)
            for func in [getattr(PluginGatewayCatalogService, func_name, None), getattr(descriptor, "__func__", None)]:
                cache = getattr(func, "cache", None)
                if cache is not None:
                    cache.clear()
                cache_clear = getattr(func, "cache_clear", None)
                if cache_clear is not None:
                    cache_clear()
        clear_plugin_reference_cache = getattr(
            PluginGatewayCatalogService,
            "clear_plugin_reference_cache",
            None,
        )
        if clear_plugin_reference_cache is not None:
            clear_plugin_reference_cache()

    @patch("plugin_service.plugin_client.env.USE_PLUGIN_SERVICE", "1")
    @patch.object(PluginServiceApiClient, "get_paas_plugin_info")
    def test_plugin_list_preserves_tag_info(self, mock_get_paas_plugin_info):
        mock_get_paas_plugin_info.return_value = {
            "count": 1,
            "results": [
                {
                    "code": "bk_plugin_demo",
                    "name": "Demo Plugin",
                    "logo_url": "https://example.com/logo.png",
                    "creator": "admin",
                    "tag_info": {"code_name": "DEVOPS", "name": "研发工具"},
                }
            ],
        }

        result = PluginServiceApiClient.get_plugin_list(
            limit=200,
            offset=0,
            distributor_code_name=PLUGIN_DISTRIBUTOR_NAME,
        )

        self.assertEqual(
            result["data"]["plugins"][0]["tag_info"],
            {"code_name": "DEVOPS", "name": "研发工具"},
        )

    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient.get_plugin_tags_list")
    def test_get_categories_returns_all_and_real_plugin_groups(self, mock_get_tags, mock_builtin_list):
        mock_builtin_list.return_value = [{"category": "JOB"}, {"category": "CC"}]
        mock_get_tags.return_value = {
            "result": True,
            "data": [
                {"code_name": "DEVOPS", "name": "研发工具"},
                {"code_name": "CC", "name": "配置平台"},
            ],
        }

        categories = PluginGatewayCatalogService.get_categories()

        self.assertEqual(categories[0], {"id": "all", "name": "全部"})
        self.assertEqual(
            categories[1:],
            [
                {"id": "CC", "name": "CC"},
                {"id": "DEVOPS", "name": "研发工具"},
                {"id": "JOB", "name": "JOB"},
            ],
        )

    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient.get_plugin_tags_list")
    def test_get_categories_filters_builtin_plugin_source(self, mock_get_tags, mock_builtin_list):
        mock_builtin_list.return_value = [{"category": "JOB"}, {"category": "CC"}]

        categories = PluginGatewayCatalogService.get_categories(plugin_source=PLUGIN_SOURCE_BUILTIN)

        self.assertEqual(
            categories,
            [
                {"id": "all", "name": "全部"},
                {"id": "CC", "name": "CC"},
                {"id": "JOB", "name": "JOB"},
            ],
        )
        mock_get_tags.assert_not_called()

    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient.get_plugin_tags_list")
    def test_get_categories_filters_third_party_plugin_source(self, mock_get_tags, mock_builtin_list):
        mock_get_tags.return_value = {
            "result": True,
            "data": [{"code_name": "DEVOPS", "name": "研发工具"}],
        }

        categories = PluginGatewayCatalogService.get_categories(plugin_source=PLUGIN_SOURCE_THIRD_PARTY)

        self.assertEqual(
            categories,
            [
                {"id": "all", "name": "全部"},
                {"id": "DEVOPS", "name": "研发工具"},
            ],
        )
        mock_builtin_list.assert_not_called()

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._list_plugins")
    def test_get_plugin_list_filters_category_and_keyword(self, mock_list_plugins):
        request = RequestFactory().get(
            "/apigw/plugin-gateway/plugins/",
            {"category": "JOB", "key": "execute"},
        )
        mock_list_plugins.return_value = [
            {"id": "builtin__job_execute", "name": "Execute Job", "category": "JOB"},
            {"id": "builtin__job_push_file", "name": "Push File", "category": "JOB"},
            {"id": "bk_plugin_execute", "name": "Execute Plugin", "category": "DEVOPS"},
        ]

        meta = PluginGatewayCatalogService.get_plugin_list(request=request)

        self.assertEqual(meta["total"], 1)
        self.assertEqual([item["id"] for item in meta["apis"]], ["builtin__job_execute"])

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._list_plugins")
    def test_get_plugin_list_filters_plugin_source(self, mock_list_plugins):
        request = RequestFactory().get(
            "/apigw/plugin-gateway/plugins/",
            {"plugin_source": PLUGIN_SOURCE_BUILTIN},
        )
        mock_list_plugins.return_value = [
            {
                "id": "builtin__job_execute",
                "name": "Execute Job",
                "plugin_source": PLUGIN_SOURCE_BUILTIN,
                "category": "JOB",
            },
            {
                "id": "bk_plugin_execute",
                "name": "Execute Plugin",
                "plugin_source": PLUGIN_SOURCE_THIRD_PARTY,
                "category": "DEVOPS",
            },
        ]

        meta = PluginGatewayCatalogService.get_plugin_list(request=request)

        self.assertEqual(meta["total"], 1)
        self.assertEqual([item["id"] for item in meta["apis"]], ["builtin__job_execute"])

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._list_third_party_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    def test_get_plugin_list_loads_only_builtin_source(self, mock_builtin_list, mock_third_party_list):
        request = RequestFactory().get(
            "/apigw/plugin-gateway/plugins/",
            {"plugin_source": PLUGIN_SOURCE_BUILTIN},
        )
        mock_builtin_list.return_value = []

        PluginGatewayCatalogService.get_plugin_list(request=request)

        mock_builtin_list.assert_called_once_with()
        mock_third_party_list.assert_not_called()

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._list_third_party_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    def test_get_plugin_list_loads_only_third_party_source(self, mock_builtin_list, mock_third_party_list):
        request = RequestFactory().get(
            "/apigw/plugin-gateway/plugins/",
            {"plugin_source": PLUGIN_SOURCE_THIRD_PARTY},
        )
        mock_third_party_list.return_value = []

        PluginGatewayCatalogService.get_plugin_list(request=request)

        mock_builtin_list.assert_not_called()
        mock_third_party_list.assert_called_once_with()

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._list_third_party_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    def test_get_plugin_list_without_source_loads_all_sources(self, mock_builtin_list, mock_third_party_list):
        mock_builtin_list.return_value = []
        mock_third_party_list.return_value = []

        PluginGatewayCatalogService.get_plugin_list(request=self.request)

        mock_builtin_list.assert_called_once_with()
        mock_third_party_list.assert_called_once_with()

    @override_settings(
        BK_API_URL_TMPL="https://{api_name}.apigw.example.com",
        BK_APIGW_NAME="bk-sops",
        BK_APIGW_STAGE_NAME="stage",
    )
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._list_plugins")
    def test_get_plugin_list_uses_public_apigw_url(self, mock_list_plugins):
        mock_list_plugins.return_value = [
            {
                "id": "builtin__job_execute_task",
                "name": "执行作业",
                "plugin_source": PLUGIN_SOURCE_BUILTIN,
                "plugin_code": "job_execute_task",
                "wrapper_version": "",
                "default_version": "legacy",
                "latest_version": "legacy",
                "versions": ["legacy"],
                "category": "JOB",
                "description": "",
            }
        ]

        meta = PluginGatewayCatalogService.get_plugin_list(request=self.request)

        self.assertEqual(
            meta["apis"][0]["meta_url_template"],
            "https://bk-sops.apigw.example.com/stage/plugin-gateway/plugins/"
            "builtin__job_execute_task/?version={version}",
        )

    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_plugin_list_contains_builtin_and_third_party_plugins(
        self, mock_client_cls, mock_get_plugin_meta, mock_builtin_list
    ):
        mock_builtin_list.return_value = [
            {
                "id": "builtin__job_execute_task",
                "name": "执行作业",
                "plugin_source": PLUGIN_SOURCE_BUILTIN,
                "plugin_code": "job_execute_task",
                "wrapper_version": "",
                "default_version": "legacy",
                "latest_version": "legacy",
                "versions": ["legacy"],
                "category": "JOB",
                "description": "",
            }
        ]
        mock_get_plugin_meta.return_value = {
            "description": "remote plugin",
            "versions": ["1.1.0", "1.0.0"],
            "framework_version": "2.0.0",
            "runtime_version": "3.11",
            "group": "PLUGIN_META_GROUP",
        }
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {
                "count": 1,
                "plugins": [
                    {
                        "code": "bk_plugin_demo",
                        "name": "Demo Plugin",
                        "tag_info": {"code_name": "DEVOPS", "name": "研发工具"},
                    }
                ],
            },
        }

        meta = PluginGatewayCatalogService.get_plugin_list(request=self.request)

        self.assertEqual(len(meta["apis"]), 2)
        plugins = {plugin["id"]: plugin for plugin in meta["apis"]}
        third_party_plugin = plugins["bk_plugin_demo"]
        builtin_plugin = plugins["builtin__job_execute_task"]
        self.assertEqual(third_party_plugin["plugin_source"], PLUGIN_SOURCE_THIRD_PARTY)
        self.assertEqual(third_party_plugin["category"], "DEVOPS")
        self.assertEqual(third_party_plugin["category_name"], "研发工具")
        self.assertEqual(third_party_plugin["default_version"], "1.1.0")
        self.assertEqual(third_party_plugin["latest_version"], "1.1.0")
        self.assertEqual(third_party_plugin["versions"], ["1.1.0", "1.0.0"])
        self.assertEqual(third_party_plugin["wrapper_version"], UNIFORM_API_WRAPPER_VERSION)
        self.assertIn("/apigw/plugin-gateway/plugins/bk_plugin_demo/", third_party_plugin["meta_url_template"])
        self.assertEqual(builtin_plugin["plugin_source"], PLUGIN_SOURCE_BUILTIN)
        self.assertEqual(builtin_plugin["category"], "JOB")
        self.assertIn(
            "/apigw/plugin-gateway/plugins/builtin__job_execute_task/",
            builtin_plugin["meta_url_template"],
        )

    @override_settings(
        BK_API_URL_TMPL="https://{api_name}.apigw.example.com",
        BK_APIGW_NAME="bk-sops",
        BK_APIGW_STAGE_NAME="stage",
    )
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.get_plugin_detail")
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    def test_get_builtin_plugin_detail_preserves_form_schema(self, mock_builtin_list, mock_builtin_detail):
        mock_builtin_list.return_value = [
            {
                "id": "builtin__job_fast_execute_script",
                "name": "快速执行脚本",
                "plugin_source": PLUGIN_SOURCE_BUILTIN,
                "plugin_code": "job_fast_execute_script",
                "wrapper_version": UNIFORM_API_WRAPPER_VERSION,
                "default_version": "v2.0",
                "latest_version": "v2.0",
                "versions": ["v2.0"],
                "category": "JOB",
                "description": "",
            }
        ]
        mock_builtin_detail.return_value = {
            "inputs": [],
            "outputs": [],
            "form_schema": {
                "type": "object",
                "properties": {"job_content": {"type": "string", "ui:component": {"name": "codeEditor"}}},
            },
        }

        detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="builtin__job_fast_execute_script",
            version="v2.0",
        )

        self.assertEqual(detail["form_schema"]["properties"]["job_content"]["ui:component"]["name"], "codeEditor")

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayContextService.resolve_form_context")
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.get_plugin_detail")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService.get_plugin_reference")
    def test_get_plugin_detail_adds_form_context_only_for_source_request(
        self, mock_get_plugin_reference, mock_builtin_detail, mock_resolve_form_context
    ):
        project = Project.objects.create(name="biz9991", creator="admin", bk_biz_id=9991, from_cmdb=True)
        source_config = PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            default_project_id=project.id,
            is_enabled=True,
        )
        mock_get_plugin_reference.return_value = {
            "id": "builtin__job_fast_execute_script",
            "name": "快速执行脚本",
            "plugin_source": PLUGIN_SOURCE_BUILTIN,
            "plugin_code": "job_fast_execute_script",
            "wrapper_version": UNIFORM_API_WRAPPER_VERSION,
            "default_version": "v2.0",
            "latest_version": "v2.0",
            "versions": ["v2.0"],
        }
        mock_builtin_detail.return_value = {"inputs": [], "outputs": [], "forms": {"input": None, "output": None}}
        mock_resolve_form_context.return_value = {"project": {"id": project.id}}

        old_detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="builtin__job_fast_execute_script",
            version="v2.0",
        )
        detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="builtin__job_fast_execute_script",
            version="v2.0",
            source_config=source_config,
            scope_type="biz",
            scope_value="9991",
            operator="jwt-operator",
        )

        self.assertNotIn("form_context", old_detail)
        self.assertEqual(detail["form_context"], {"project": {"id": project.id}})
        mock_resolve_form_context.assert_called_once_with(
            source_config=source_config,
            scope_type="biz",
            scope_value="9991",
            plugin_source=PLUGIN_SOURCE_BUILTIN,
            plugin_code="job_fast_execute_script",
        )

    @override_settings(
        BK_API_URL_TMPL="https://{api_name}.apigw.example.com",
        BK_APIGW_NAME="bk-sops",
        BK_APIGW_STAGE_NAME="stage",
    )
    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_detail_schema")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_plugin_detail_converts_json_schema_inputs_and_outputs(
        self, mock_client_cls, mock_get_plugin_meta, mock_get_plugin_detail_schema, mock_builtin_list
    ):
        mock_builtin_list.return_value = []
        mock_get_plugin_meta.return_value = {
            "description": "remote plugin",
            "versions": ["1.1.0", "1.0.0"],
            "framework_version": "2.0.0",
            "runtime_version": "3.11",
        }
        mock_get_plugin_detail_schema.return_value = {
            "version": "1.1.0",
            "inputs": {
                "properties": {
                    "biz_id": {
                        "title": "业务ID",
                        "type": "integer",
                        "description": "业务 ID",
                        "default": 2,
                        "ui:component": {
                            "name": "select",
                            "props": {
                                "datasource": [
                                    {"label": "业务 2", "value": 2},
                                ]
                            },
                        },
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
            "forms": {
                "renderform": {
                    "type": "object",
                    "properties": {
                        "biz_id": {
                            "ui:reactions": [
                                {
                                    "lifetime": "init",
                                    "then": {"actions": ["{{ $loadDataSource }}"]},
                                }
                            ]
                        }
                    },
                }
            },
        }
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {"count": 1, "plugins": [{"code": "bk_plugin_demo", "name": "Demo Plugin"}]},
        }

        detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="bk_plugin_demo",
            version="1.1.0",
        )

        self.assertEqual(detail["plugin_version"], "1.1.0")
        self.assertEqual(detail["version"], UNIFORM_API_WRAPPER_VERSION)
        self.assertEqual(detail["wrapper_version"], UNIFORM_API_WRAPPER_VERSION)
        self.assertEqual(detail["plugin_source"], PLUGIN_SOURCE_THIRD_PARTY)
        self.assertEqual(detail["polling"]["success_tag"]["key"], "data.status")
        self.assertEqual(detail["polling"]["fail_tag"]["key"], "data.status")
        self.assertEqual(detail["polling"]["running_tag"]["key"], "data.status")
        self.assertEqual(detail["polling"]["running_tag"]["value"], "RUNNING")
        self.assertEqual(
            detail["inputs"],
            [
                {
                    "key": "biz_id",
                    "name": "业务ID",
                    "type": "int",
                    "desc": "业务 ID",
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
                    "type": "int",
                    "desc": "JOB instance id",
                    "description": "JOB instance id",
                }
            ],
        )
        self.assertEqual(detail["desc"], "remote plugin")
        self.assertEqual(detail["forms"], {"input": None, "output": None})
        self.assertEqual(detail["form_schema"]["properties"]["biz_id"]["ui:component"]["name"], "select")
        self.assertEqual(
            detail["form_schema"]["properties"]["biz_id"]["ui:reactions"],
            [
                {
                    "lifetime": "init",
                    "then": {"actions": ["{{ $loadDataSource }}"]},
                }
            ],
        )
        self.assertEqual(
            detail["url"],
            "https://bk-sops.apigw.example.com/stage/plugin-gateway/runs/",
        )
        self.assertEqual(
            detail["polling"]["url"],
            "https://bk-sops.apigw.example.com/stage/plugin-gateway/runs/status/",
        )

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_detail_schema")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService.get_plugin_reference")
    def test_get_plugin_detail_exposes_renderform_with_selected_version(
        self, mock_get_plugin_reference, mock_get_plugin_detail_schema
    ):
        mock_get_plugin_reference.return_value = {
            "id": "danny-test-plugi",
            "name": "Danny Test Plugin",
            "plugin_source": PLUGIN_SOURCE_THIRD_PARTY,
            "plugin_code": "danny-test-plugi",
            "wrapper_version": UNIFORM_API_WRAPPER_VERSION,
            "default_version": "1.2.3",
            "latest_version": "1.2.3",
            "versions": ["1.2.3"],
            "description": "remote plugin",
        }
        mock_get_plugin_detail_schema.return_value = {
            "inputs": {"properties": {}},
            "outputs": {"properties": {}},
            "forms": {"renderform": "window.$.atoms.dannyTest = []"},
        }

        detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="danny-test-plugi",
            version="1.2.3",
        )

        self.assertEqual(detail["plugin_version"], "1.2.3")
        self.assertEqual(detail["forms"]["input"]["type"], "renderform")
        self.assertEqual(detail["forms"]["input"]["key"], "danny-test-plugi")
        self.assertIn("form_schema", detail)
        mock_get_plugin_detail_schema.assert_called_once_with("danny-test-plugi", "1.2.3")

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_detail_schema")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService.get_plugin_reference")
    def test_get_plugin_detail_rejects_unavailable_version_before_loading_detail(
        self, mock_get_plugin_reference, mock_get_plugin_detail_schema
    ):
        mock_get_plugin_reference.return_value = {
            "id": "danny-test-plugi",
            "plugin_source": PLUGIN_SOURCE_THIRD_PARTY,
            "plugin_code": "danny-test-plugi",
            "default_version": "1.2.3",
            "versions": ["1.2.3"],
        }

        with self.assertRaises(PluginGatewayVersionNotFoundError):
            PluginGatewayCatalogService.get_plugin_detail(
                request=self.request,
                plugin_id="danny-test-plugi",
                version="9.9.9",
            )

        mock_get_plugin_detail_schema.assert_not_called()

    def test_build_third_party_plugin_reference_uses_first_framework_version_as_latest(self):
        plugin = {"code": "bk_plugin_demo", "name": "Demo Plugin"}
        meta = {"description": "remote plugin", "versions": ["1.2.0", "1.0.0"]}

        reference = PluginGatewayCatalogService._build_third_party_plugin_reference(plugin, meta)

        self.assertEqual(reference["default_version"], "1.2.0")
        self.assertEqual(reference["latest_version"], "1.2.0")
        self.assertEqual(reference["versions"], ["1.2.0", "1.0.0"])

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_list_third_party_plugins_loads_meta_concurrently(self, mock_client_cls, mock_get_plugin_meta):
        meta_barrier = Barrier(2)

        def load_meta(_plugin_code):
            meta_barrier.wait(timeout=5)
            return {"description": "remote plugin", "versions": ["1.0.0"]}

        mock_get_plugin_meta.side_effect = load_meta
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {
                "count": 2,
                "plugins": [
                    {"code": "bk_plugin_demo_1", "name": "Demo Plugin 1"},
                    {"code": "bk_plugin_demo_2", "name": "Demo Plugin 2"},
                ],
            },
        }

        plugins = PluginGatewayCatalogService._list_third_party_plugins()

        self.assertEqual([plugin["id"] for plugin in plugins], ["bk_plugin_demo_1", "bk_plugin_demo_2"])

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_third_party_plugin_entries")
    def test_list_third_party_plugins_skips_plugin_when_loading_meta_raises(
        self, mock_get_plugin_entries, mock_get_plugin_meta
    ):
        mock_get_plugin_entries.return_value = [
            {"code": "broken_plugin", "name": "Broken Plugin"},
            {"code": "healthy_plugin", "name": "Healthy Plugin"},
        ]

        def load_meta(plugin_code):
            if plugin_code == "broken_plugin":
                raise ValueError("invalid metadata response")
            return {"description": "remote plugin", "versions": ["1.0.0"]}

        mock_get_plugin_meta.side_effect = load_meta

        with self.assertLogs("root", level="ERROR") as captured_logs:
            plugins = PluginGatewayCatalogService._list_third_party_plugins()

        self.assertEqual([plugin["id"] for plugin in plugins], ["healthy_plugin"])
        self.assertIn("broken_plugin", "\n".join(captured_logs.output))

    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_third_party_plugin_entries_loads_all_pages(self, mock_client_cls):
        first_page = [
            {"code": "plugin_{:03d}".format(index), "name": "Plugin {:03d}".format(index)} for index in range(200)
        ]
        second_page = [
            {"code": "plugin_{:03d}".format(index), "name": "Plugin {:03d}".format(index)} for index in range(200, 400)
        ]
        third_page = [{"code": "plugin_400", "name": "Plugin 400"}]
        mock_client_cls.get_plugin_list.side_effect = [
            {"result": True, "data": {"count": 401, "plugins": first_page}},
            {"result": True, "data": {"count": 401, "plugins": second_page}},
            {"result": True, "data": {"count": 401, "plugins": third_page}},
        ]

        plugins = PluginGatewayCatalogService._get_third_party_plugin_entries()

        self.assertEqual(len(plugins), 401)
        self.assertEqual(plugins[-1]["code"], "plugin_400")
        self.assertEqual(
            mock_client_cls.get_plugin_list.call_args_list,
            [
                call(limit=200, offset=0, distributor_code_name=PLUGIN_DISTRIBUTOR_NAME),
                call(limit=200, offset=200, distributor_code_name=PLUGIN_DISTRIBUTOR_NAME),
                call(limit=200, offset=400, distributor_code_name=PLUGIN_DISTRIBUTOR_NAME),
            ],
        )

    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_third_party_plugin_entries_rejects_incomplete_page(self, mock_client_cls):
        first_page = [
            {"code": "plugin_{:03d}".format(index), "name": "Plugin {:03d}".format(index)} for index in range(200)
        ]
        mock_client_cls.get_plugin_list.side_effect = [
            {"result": True, "data": {"count": 401, "plugins": first_page}},
            {"result": True, "data": {"count": 401, "plugins": []}},
        ]

        with self.assertRaises(PluginGatewaySourceUnavailableError):
            PluginGatewayCatalogService._get_third_party_plugin_entries()

    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_third_party_plugin_entries_rejects_boolean_count(self, mock_client_cls):
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {"count": True, "plugins": [{"code": "plugin_demo", "name": "Plugin Demo"}]},
        }

        with self.assertRaises(PluginGatewaySourceUnavailableError):
            PluginGatewayCatalogService._get_third_party_plugin_entries()

    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_detail_schema")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_get_third_party_detail_only_loads_selected_meta(
        self, mock_client_cls, mock_get_plugin_meta, mock_get_plugin_detail_schema, mock_builtin_list
    ):
        mock_builtin_list.return_value = []
        mock_get_plugin_meta.return_value = {
            "description": "remote plugin",
            "versions": ["1.0.0"],
        }
        mock_get_plugin_detail_schema.return_value = {"inputs": {}, "outputs": {}}
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {
                "count": 2,
                "plugins": [
                    {"code": "bk_plugin_demo_1", "name": "Demo Plugin 1"},
                    {"code": "bk_plugin_demo_2", "name": "Demo Plugin 2"},
                ],
            },
        }

        detail = PluginGatewayCatalogService.get_plugin_detail(
            request=self.request,
            plugin_id="bk_plugin_demo_1",
            version="1.0.0",
        )

        self.assertEqual(detail["id"], "bk_plugin_demo_1")
        mock_get_plugin_meta.assert_called_once_with("bk_plugin_demo_1")
        mock_client_cls.get_plugin_list.assert_called_once_with(
            search_term="bk_plugin_demo_1",
            limit=200,
            offset=0,
            distributor_code_name=PLUGIN_DISTRIBUTOR_NAME,
        )

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient.get_plugin_list")
    def test_get_plugin_reference_caches_exact_third_party_reference(self, mock_get_plugin_list, mock_get_plugin_meta):
        mock_get_plugin_list.return_value = {
            "result": True,
            "data": {
                "count": 1,
                "plugins": [
                    {
                        "code": "bk_plugin_demo",
                        "name": "Demo Plugin",
                        "logo_url": "https://example.com/logo.png",
                        "creator": "admin",
                        "tag_info": {"code_name": "DEVOPS", "name": "DevOps"},
                    }
                ],
            },
        }
        mock_get_plugin_meta.return_value = {
            "description": "remote plugin",
            "versions": ["2.1.0", "1.4.0"],
        }

        first = PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")
        second = PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")

        self.assertEqual(first["versions"], ["2.1.0", "1.4.0"])
        self.assertEqual(second, first)
        self.assertEqual(mock_get_plugin_list.call_count, 1)

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient.get_plugin_list")
    def test_plugin_reference_cache_can_be_cleared_deterministically(self, mock_get_plugin_list, mock_get_plugin_meta):
        mock_get_plugin_list.return_value = {
            "result": True,
            "data": {
                "count": 1,
                "plugins": [
                    {
                        "code": "bk_plugin_demo",
                        "name": "Demo Plugin",
                        "logo_url": "https://example.com/logo.png",
                        "creator": "admin",
                        "tag_info": {"code_name": "DEVOPS", "name": "DevOps"},
                    }
                ],
            },
        }
        mock_get_plugin_meta.return_value = {"description": "remote plugin", "versions": ["2.1.0"]}

        PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")
        PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")
        clear_plugin_reference_cache = getattr(
            PluginGatewayCatalogService,
            "clear_plugin_reference_cache",
            None,
        )
        if clear_plugin_reference_cache is not None:
            clear_plugin_reference_cache()
        PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")

        self.assertEqual(mock_get_plugin_list.call_count, 2)

    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient.get_plugin_list")
    def test_blacklist_is_evaluated_after_plugin_reference_cache_hit(self, mock_get_plugin_list, mock_get_plugin_meta):
        mock_get_plugin_list.return_value = {
            "result": True,
            "data": {
                "count": 1,
                "plugins": [
                    {
                        "code": "bk_plugin_demo",
                        "name": "Demo Plugin",
                        "logo_url": "https://example.com/logo.png",
                        "creator": "admin",
                        "tag_info": {"code_name": "DEVOPS", "name": "DevOps"},
                    }
                ],
            },
        }
        mock_get_plugin_meta.return_value = {"description": "remote plugin", "versions": ["2.1.0"]}

        first = PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")
        cached = PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")
        PluginGatewaySourceConfig.objects.create(
            source_key="bkflow-cache-test",
            display_name="BKFlow Cache Test",
            do_not_open_list=["bk_plugin_demo"],
        )
        blocked = PluginGatewayCatalogService.get_plugin_reference("bk_plugin_demo")

        self.assertEqual(cached, first)
        self.assertIsNone(blocked)
        self.assertEqual(mock_get_plugin_list.call_count, 1)

    @patch("gcloud.plugin_gateway.services.catalog.BuiltinCatalogService.list_plugins")
    @patch("gcloud.plugin_gateway.services.catalog.PluginGatewayCatalogService._get_plugin_meta")
    @patch("gcloud.plugin_gateway.services.catalog.PluginServiceApiClient")
    def test_do_not_open_list_filters_list_and_detail(self, mock_client_cls, mock_get_plugin_meta, mock_builtin_list):
        PluginGatewaySourceConfig.objects.create(
            source_key="bkflow",
            display_name="BKFlow",
            do_not_open_list=["builtin__job_execute_task", "bk_plugin_demo"],
        )
        mock_builtin_list.return_value = [
            {
                "id": "builtin__job_execute_task",
                "name": "执行作业",
                "plugin_source": PLUGIN_SOURCE_BUILTIN,
                "plugin_code": "job_execute_task",
                "wrapper_version": "",
                "default_version": "legacy",
                "latest_version": "legacy",
                "versions": ["legacy"],
                "category": "JOB",
                "description": "",
            }
        ]
        mock_get_plugin_meta.return_value = {"description": "remote plugin", "versions": ["1.0.0"]}
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {"count": 1, "plugins": [{"code": "bk_plugin_demo", "name": "Demo Plugin"}]},
        }

        meta = PluginGatewayCatalogService.get_plugin_list(request=self.request)

        self.assertEqual(meta["apis"], [])
        self.assertIsNone(
            PluginGatewayCatalogService.get_plugin_detail(
                request=self.request,
                plugin_id="builtin__job_execute_task",
                version="legacy",
            )
        )
        self.assertIsNone(
            PluginGatewayCatalogService.get_plugin_detail(
                request=self.request,
                plugin_id="bk_plugin_demo",
                version="1.0.0",
            )
        )

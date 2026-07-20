from threading import Barrier
from unittest.mock import call, patch

from django.test import RequestFactory, TestCase, override_settings

from gcloud.plugin_gateway.constants import (
    PLUGIN_SOURCE_BUILTIN,
    PLUGIN_SOURCE_THIRD_PARTY,
    UNIFORM_API_WRAPPER_VERSION,
)
from gcloud.plugin_gateway.exceptions import PluginGatewaySourceUnavailableError
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
from gcloud.plugin_gateway.services.catalog import PluginGatewayCatalogService
from plugin_service.conf import PLUGIN_DISTRIBUTOR_NAME


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
            "versions": ["1.0.0", "1.1.0"],
            "framework_version": "2.0.0",
            "runtime_version": "3.11",
            "group": "DEVOPS",
        }
        mock_client_cls.get_plugin_list.return_value = {
            "result": True,
            "data": {"count": 1, "plugins": [{"code": "bk_plugin_demo", "name": "Demo Plugin"}]},
        }

        meta = PluginGatewayCatalogService.get_plugin_list(request=self.request)

        self.assertEqual(len(meta["apis"]), 2)
        plugins = {plugin["id"]: plugin for plugin in meta["apis"]}
        third_party_plugin = plugins["bk_plugin_demo"]
        builtin_plugin = plugins["builtin__job_execute_task"]
        self.assertEqual(third_party_plugin["plugin_source"], PLUGIN_SOURCE_THIRD_PARTY)
        self.assertEqual(third_party_plugin["category"], "DEVOPS")
        self.assertEqual(third_party_plugin["default_version"], "1.1.0")
        self.assertEqual(third_party_plugin["latest_version"], "1.1.0")
        self.assertEqual(third_party_plugin["versions"], ["1.0.0", "1.1.0"])
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
            "versions": ["1.0.0", "1.1.0"],
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
        self.assertEqual(
            detail["url"],
            "https://bk-sops.apigw.example.com/stage/plugin-gateway/runs/",
        )
        self.assertEqual(
            detail["polling"]["url"],
            "https://bk-sops.apigw.example.com/stage/plugin-gateway/runs/status/",
        )

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

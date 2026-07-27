from django.test import RequestFactory, SimpleTestCase, TestCase, modify_settings, override_settings

from gcloud.plugin_gateway.cors import allow_plugin_form_cors

ALLOWED_ORIGIN = "https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com"
GLOBAL_ORIGIN = "https://global-cors.example.com"
REGISTERED_PATHS = (
    "/pipeline/cc_get_business_list/",
    "/pipeline/job_get_public_script_name_list/",
    "/pipeline/job_get_script_name_list/2/",
    "/pipeline/get_job_account_list/2/",
    "/pipeline/jobv3_get_instance_list/2/1/0/",
    "/plugin_service/data_api/demo/options/nested/",
)


class PluginFormCorsSignalTestCase(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.allowed_origin = ALLOWED_ORIGIN

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_allows_registered_route_for_exact_origin(self):
        request = self.factory.get(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self.assertTrue(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_allows_all_registered_routes(self):
        for path in REGISTERED_PATHS:
            with self.subTest(path=path):
                request = self.factory.get(path, HTTP_ORIGIN=self.allowed_origin)
                self.assertTrue(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_allows_registered_route_with_script_name_prefix(self):
        request = self.factory.get(
            "/pipeline/job_get_script_name_list/2/",
            SCRIPT_NAME="/o/bk_sops",
            HTTP_ORIGIN=self.allowed_origin,
        )

        self.assertEqual(request.path, "/o/bk_sops/pipeline/job_get_script_name_list/2/")
        self.assertEqual(request.path_info, "/pipeline/job_get_script_name_list/2/")
        self.assertTrue(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_rejects_pipeline_routes_outside_real_urlconf_shape(self):
        invalid_paths = (
            ("script empty parameter", "/pipeline/job_get_script_name_list/"),
            ("account empty parameter", "/pipeline/get_job_account_list/"),
            ("job instance empty parameters", "/pipeline/jobv3_get_instance_list/"),
            ("script nonnumeric parameter", "/pipeline/job_get_script_name_list/demo/"),
            ("account nonnumeric parameter", "/pipeline/get_job_account_list/demo/"),
            ("job instance nonnumeric parameter", "/pipeline/jobv3_get_instance_list/2/type/0/"),
            ("script extra segment", "/pipeline/job_get_script_name_list/2/extra/"),
            ("account extra segment", "/pipeline/get_job_account_list/2/extra/"),
            ("job instance extra segment", "/pipeline/jobv3_get_instance_list/2/1/0/extra/"),
        )

        for case, path in invalid_paths:
            with self.subTest(case=case, path=path):
                request = self.factory.get(path, HTTP_ORIGIN=self.allowed_origin)
                self.assertFalse(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_rejects_percent_encoded_slash_after_request_decoding(self):
        encoded_and_decoded_paths = (
            (
                "/pipeline/job_get_script_name_list/2%2F3/",
                "/pipeline/job_get_script_name_list/2/3/",
            ),
            (
                "/pipeline/get_job_account_list/2%2F3/",
                "/pipeline/get_job_account_list/2/3/",
            ),
            (
                "/pipeline/jobv3_get_instance_list/2/1%2F0/0/",
                "/pipeline/jobv3_get_instance_list/2/1/0/0/",
            ),
        )

        for encoded_path, decoded_path in encoded_and_decoded_paths:
            with self.subTest(encoded_path=encoded_path):
                request = self.factory.get(encoded_path, HTTP_ORIGIN=self.allowed_origin)
                self.assertEqual(request.path_info, decoded_path)
                self.assertFalse(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_data_api_matches_real_urlconf_nonempty_segments(self):
        for path, expected in (
            ("/plugin_service/data_api/demo/options/nested/", True),
            ("/plugin_service/data_api//options/", False),
            ("/plugin_service/data_api/demo/", False),
        ):
            with self.subTest(path=path):
                request = self.factory.get(path, HTTP_ORIGIN=self.allowed_origin)
                self.assertEqual(allow_plugin_form_cors(None, request), expected)

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_rejects_unregistered_pipeline_route(self):
        request = self.factory.get(
            "/pipeline/admin/private/",
            HTTP_ORIGIN=self.allowed_origin,
        )

        self.assertFalse(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_rejects_suffix_or_scheme_mismatch(self):
        for origin in (
            "http://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com",
            "https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com.evil.example",
        ):
            with self.subTest(origin=origin):
                request = self.factory.get(
                    "/pipeline/cc_get_business_list/",
                    HTTP_ORIGIN=origin,
                )
                self.assertFalse(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=False,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_rejects_registered_route_when_dedicated_switch_is_disabled(self):
        request = self.factory.get(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=self.allowed_origin,
        )

        self.assertFalse(allow_plugin_form_cors(None, request))

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_actual_request_method_matrix_matches_registered_views(self):
        cases = (
            ("/pipeline/cc_get_business_list/", "GET", True),
            ("/pipeline/cc_get_business_list/", "POST", False),
            ("/plugin_service/data_api/demo/options/", "GET", True),
            ("/plugin_service/data_api/demo/options/", "POST", True),
            ("/plugin_service/data_api/demo/options/", "PUT", True),
            ("/plugin_service/data_api/demo/options/", "PATCH", True),
            ("/plugin_service/data_api/demo/options/", "DELETE", True),
            ("/plugin_service/data_api/demo/options/", "HEAD", False),
        )

        for path, method, expected in cases:
            with self.subTest(path=path, method=method):
                request = self.factory.generic(method, path, HTTP_ORIGIN=self.allowed_origin)
                self.assertEqual(allow_plugin_form_cors(None, request), expected)

    @override_settings(
        PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
        PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    )
    def test_preflight_request_method_matrix_matches_registered_views(self):
        cases = (
            ("/pipeline/cc_get_business_list/", "GET", True),
            ("/pipeline/cc_get_business_list/", "POST", False),
            ("/plugin_service/data_api/demo/options/", "GET", True),
            ("/plugin_service/data_api/demo/options/", "POST", True),
            ("/plugin_service/data_api/demo/options/", "PUT", True),
            ("/plugin_service/data_api/demo/options/", "PATCH", True),
            ("/plugin_service/data_api/demo/options/", "DELETE", True),
            ("/plugin_service/data_api/demo/options/", "HEAD", False),
        )

        for path, requested_method, expected in cases:
            with self.subTest(path=path, requested_method=requested_method):
                request = self.factory.options(
                    path,
                    HTTP_ORIGIN=self.allowed_origin,
                    HTTP_ACCESS_CONTROL_REQUEST_METHOD=requested_method,
                )
                self.assertEqual(allow_plugin_form_cors(None, request), expected)


@modify_settings(
    MIDDLEWARE={
        "prepend": (
            "gcloud.plugin_gateway.cors.PluginFormCorsResponseMiddleware",
            "corsheaders.middleware.CorsMiddleware",
        )
    }
)
@override_settings(
    PLUGIN_GATEWAY_FORM_CORS_ALLOW=True,
    PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN},
    CORS_ALLOW_CREDENTIALS=True,
)
class PluginFormCorsMiddlewareTestCase(TestCase):
    def _assert_credentialed_cors(self, response):
        self.assertIn("Access-Control-Allow-Origin", response)
        self.assertIn("Access-Control-Allow-Credentials", response)
        self.assertIn("Vary", response)
        self.assertEqual(response["Access-Control-Allow-Origin"], ALLOWED_ORIGIN)
        self.assertEqual(response["Access-Control-Allow-Credentials"], "true")
        self.assertIn("Origin", response["Vary"])

    def test_options_response_has_credentialed_cors_headers(self):
        response = self.client.options(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        self._assert_credentialed_cors(response)
        self.assertEqual(response["Access-Control-Allow-Methods"], "GET")

    def test_data_api_options_response_has_exact_registered_methods(self):
        response = self.client.options(
            "/plugin_service/data_api/demo/options/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="PATCH",
        )

        self._assert_credentialed_cors(response)
        self.assertEqual(
            response["Access-Control-Allow-Methods"],
            "GET, POST, PUT, PATCH, DELETE",
        )

    def test_get_response_has_credentialed_cors_headers(self):
        response = self.client.get(
            "/plugin_service/data_api/blocked/demo/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self._assert_credentialed_cors(response)

    def test_unregistered_route_has_no_cors_allow_origin_header(self):
        response = self.client.options(
            "/pipeline/admin/private/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
        )

        self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_unsupported_actual_method_has_no_credentialed_cors_headers(self):
        response = self.client.post(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
        )

        self.assertNotIn("Access-Control-Allow-Origin", response)
        self.assertNotIn("Access-Control-Allow-Methods", response)
        self.assertFalse(
            "Access-Control-Allow-Origin" in response and response.get("Access-Control-Allow-Credentials") == "true"
        )

    @override_settings(
        CORS_ORIGIN_WHITELIST=(GLOBAL_ORIGIN,),
        CORS_ALLOW_METHODS=("GET", "POST", "OPTIONS"),
    )
    def test_global_cors_preflight_methods_are_unchanged(self):
        response = self.client.options(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=GLOBAL_ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        self.assertEqual(response["Access-Control-Allow-Origin"], GLOBAL_ORIGIN)
        self.assertEqual(response["Access-Control-Allow-Methods"], "GET, POST, OPTIONS")

    def test_unsupported_preflight_method_has_no_credentialed_cors_headers(self):
        response = self.client.options(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=ALLOWED_ORIGIN,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )

        self.assertNotIn("Access-Control-Allow-Origin", response)
        self.assertFalse(
            "Access-Control-Allow-Origin" in response and response.get("Access-Control-Allow-Credentials") == "true"
        )

import base64
import copy
import json
import os
import unittest
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, override_settings

if not settings.configured:
    settings.configure(
        APP_CODE="bk_sops",
        APP_NAME="标准运维",
        BASE_DIR=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")),
        BK_APP_CODE="bk_sops",
        BK_APP_SECRET="secret",
        SECRET_KEY="secret",
        BK_IAM_SYSTEM_ID="bk_sops",
        BK_IAM_SYSTEM_NAME="标准运维",
        BK_IAM_RESOURCE_API_HOST="https://sops.example.test",
        BK_IAM_V4_API_URL="https://iam.example.test/stage",
        BKIAM_APIGW_NAME="bkiam",
        BK_API_URL_TMPL="https://{api_name}.example.test",
        IAM_V4_BATCH_AUTH_CHUNK_SIZE=2,
        IAM_V4_CALLBACK_TOKEN_CACHE_SECONDS=300,
        IAM_V4_REQUEST_TIMEOUT=10,
        IAM_V4_TENANT_HEADER="X-Bk-Tenant-Id",
        DEFAULT_CHARSET="utf-8",
        CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
        USE_I18N=False,
    )

from bk_resource.exceptions import APIRequestError
from requests import HTTPError

from gcloud.core.api_adapter.user_role import is_user_functor
from gcloud.iam_auth import api as iam_api
from gcloud.iam_auth.api_v4.resources import DirectAuthResource
from gcloud.iam_auth.api_v4.serializers import DirectAuthRequestSerializer
from gcloud.iam_auth.apply_service import ApplyService, checks_from_permission_payload, checks_from_simple_payload
from gcloud.iam_auth.apps import validate_settings
from gcloud.iam_auth.client import (
    IAMV4Client,
    _api_request,
    validate_action_decisions,
    validate_authorized_resources,
    validate_resource_decisions,
)
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES, ACTIONS, RESOURCES
from gcloud.iam_auth.exceptions import IAMPermissionDenied, IAMResourceNotFound, IAMV4ProtocolError, IAMV4Unavailable
from gcloud.iam_auth.management.commands.register_iam_v4_roles import validate_registration_response
from gcloud.iam_auth.middleware import IAMPermissionDeniedMiddleware
from gcloud.iam_auth.model_validation import load_models, validate_models
from gcloud.iam_auth.models import Resource
from gcloud.iam_auth.payloads import resource_to_v4_apply, resource_to_v4_auth
from gcloud.iam_auth.request_resources import load_resource_for_request
from gcloud.iam_auth.resource_api_v4 import auth as callback_auth
from gcloud.iam_auth.resource_api_v4.dispatcher import resource_callback
from gcloud.iam_auth.resource_api_v4.providers import PROVIDERS
from gcloud.iam_auth.resource_api_v4.providers.base import list_instance_cache_key
from gcloud.iam_auth.resource_api_v4.serializers import CallbackRequestSerializer
from gcloud.iam_auth.scope_resolver import ScopeResolver
from gcloud.iam_auth.service import PermissionService
from gcloud.iam_auth.topology import parse_iam_path, project_path
from gcloud.iam_auth.types import AuthorizedScope, PermissionCheck


def resource(resource_type="flow", resource_id="1", project_id="2"):
    return Resource(
        "bk_sops",
        resource_type,
        resource_id,
        {"name": "resource", "_bk_iam_path_": project_path(project_id)},
    )


def creator_resource(resource_type="flow", resource_id="1", username="alice"):
    return Resource(
        "bk_sops",
        resource_type,
        resource_id,
        {"name": "resource", "iam_resource_owner": username, "_bk_iam_path_": project_path("2")},
    )


class MetadataAndModelTest(unittest.TestCase):
    def test_code_model_is_exactly_7_by_42(self):
        self.assertEqual(len(RESOURCES), 7)
        self.assertEqual(len(ACTIONS), 42)
        self.assertEqual(len(ACTION_RESOURCE_TYPES), 42)

    def test_json_model_and_nine_roles_match_code(self):
        with override_settings(BK_IAM_RESOURCE_API_HOST="https://sops.example.test"):
            counts = validate_models(*load_models())
        self.assertEqual(counts, {"systems": 1, "resources": 7, "actions": 42, "roles": 9})

    def test_platform_auditor_has_no_admin_view_or_write_action(self):
        with override_settings(BK_IAM_RESOURCE_API_HOST="https://sops.example.test"):
            _, roles = load_models()
        auditor = next(role for role in roles if role["id"] == "platform_auditor")
        action_ids = {item["id"] for item in auditor["actions"]}
        self.assertNotIn("admin_view", action_ids)
        self.assertFalse(action_ids & {"admin_edit", "project_edit", "flow_edit", "task_operate"})

    def test_role_validation_rejects_any_v11_binding_drift(self):
        with override_settings(BK_IAM_RESOURCE_API_HOST="https://sops.example.test"):
            model, roles = load_models()
        mutated = copy.deepcopy(roles)
        next(role for role in mutated if role["id"] == "biz_viewer")["actions"].append(
            {"id": "project_edit", "resource_type_id": "project"}
        )
        with self.assertRaises(IAMV4ProtocolError):
            validate_models(model, mutated)


class SettingsValidationTest(unittest.TestCase):
    @override_settings(RUN_MODE="PRODUCT", BK_IAM_V4_API_URL="", BK_API_URL_TMPL="")
    def test_product_startup_requires_resolvable_v4_endpoint(self):
        with self.assertRaises(ImproperlyConfigured):
            validate_settings()

    @override_settings(IAM_V4_BATCH_AUTH_CHUNK_SIZE=21)
    def test_batch_auth_chunk_size_must_not_exceed_gateway_limit(self):
        with self.assertRaisesRegex(ImproperlyConfigured, "between 1 and 20"):
            validate_settings()

    def test_client_rejects_invalid_explicit_batch_auth_chunk_size(self):
        with self.assertRaisesRegex(IAMV4ProtocolError, "between 1 and 20"):
            IAMV4Client(chunk_size=21)


class SerializerAndPayloadTest(unittest.TestCase):
    def test_strict_request_rejects_unknown_field(self):
        serializer = DirectAuthRequestSerializer(
            data={
                "tenant_id": "t1",
                "system_id": "bk_sops",
                "subject": {"type": "user", "id": "alice"},
                "action_id": "flow_view",
                "unexpected": "value",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("unexpected", serializer.errors)

    def test_callback_list_requires_valid_page(self):
        serializer = CallbackRequestSerializer(data={"type": "project", "method": "list_instance"})
        self.assertFalse(serializer.is_valid())
        serializer = CallbackRequestSerializer(
            data={
                "type": "project",
                "method": "list_instance",
                "page": {"page": 1, "page_size": 1001},
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_callback_fetch_rejects_more_than_1000_ids(self):
        serializer = CallbackRequestSerializer(
            data={
                "type": "flow",
                "method": "fetch_instance_info",
                "filter": {"ids": [str(index) for index in range(1001)]},
                "requires": ["secret"],
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_callback_fetch_accepts_extensible_requires(self):
        serializer = CallbackRequestSerializer(
            data={
                "type": "flow",
                "method": "fetch_instance_info",
                "filter": {"ids": ["1"]},
                "requires": ["id", "future_attribute"],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_auth_and_apply_payloads_have_distinct_topology_fields(self):
        item = resource()
        self.assertEqual(resource_to_v4_auth(item), {"id": "1"})
        self.assertEqual(resource_to_v4_apply(item)["ancestors"], [{"type": "project", "id": "2"}])
        self.assertNotIn("attributes", resource_to_v4_auth(item))

    def test_invalid_path_is_rejected(self):
        with self.assertRaises(IAMV4ProtocolError):
            parse_iam_path("project,2")


class StrictResponseTest(unittest.TestCase):
    def test_action_results_are_merged_by_id_not_order(self):
        result = validate_action_decisions(
            [{"action_id": "flow_edit", "allowed": False}, {"action_id": "flow_view", "allowed": True}],
            ["flow_view", "flow_edit"],
        )
        self.assertEqual(list(result), ["flow_view", "flow_edit"])
        self.assertEqual(result, {"flow_view": True, "flow_edit": False})

    def test_action_results_reject_missing_duplicate_and_unknown_ids(self):
        invalid_rows = (
            [{"action_id": "flow_view", "allowed": True}],
            [
                {"action_id": "flow_view", "allowed": True},
                {"action_id": "flow_view", "allowed": False},
            ],
            [
                {"action_id": "flow_view", "allowed": True},
                {"action_id": "unknown", "allowed": False},
            ],
        )
        for rows in invalid_rows:
            with self.subTest(rows=rows), self.assertRaises(IAMV4ProtocolError):
                validate_action_decisions(rows, ["flow_view", "flow_edit"])

    def test_resource_results_require_string_unique_complete_ids(self):
        items = [resource(resource_id="1"), resource(resource_id="2")]
        result = validate_resource_decisions(
            [{"resource_id": "2", "allowed": False}, {"resource_id": "1", "allowed": True}], items
        )
        self.assertEqual(result, {"1": True, "2": False})
        with self.assertRaises(IAMV4ProtocolError):
            validate_resource_decisions([{"resource_id": 1, "allowed": True}], [items[0]])

    def test_authorized_scope_distinguishes_empty_and_wildcard(self):
        self.assertEqual(validate_authorized_resources([]), [])
        self.assertEqual(validate_authorized_resources([{"type": "flow", "ids": ["*"]}])[0]["ids"], ["*"])
        self.assertEqual(
            validate_authorized_resources([{"type": "flow", "ids": ["1", "*", "1"]}]),
            [{"type": "flow", "ids": ["*"]}],
        )
        self.assertEqual(
            validate_authorized_resources([{"type": "flow", "ids": ["1", "2", "1"]}]),
            [{"type": "flow", "ids": ["1", "2"]}],
        )
        with self.assertRaises(IAMV4ProtocolError):
            validate_authorized_resources([{"type": "unknown", "ids": []}])

    def test_project_ancestor_scope_is_only_valid_for_project_tree(self):
        self.assertEqual(
            validate_authorized_resources([{"type": "project", "ids": ["2"]}], "task"),
            [{"type": "project", "ids": ["2"]}],
        )
        with self.assertRaises(IAMV4ProtocolError):
            validate_authorized_resources([{"type": "project", "ids": ["2"]}], "common_flow")


class ClientAndResourceTest(unittest.TestCase):
    @mock.patch("gcloud.iam_auth.client._api_request")
    def test_client_chunks_and_preserves_requested_action_order(self, api_request):
        api_request.side_effect = lambda unused, payload: [
            {"action_id": action_id, "allowed": action_id.endswith("view")}
            for action_id in reversed(payload["action_ids"])
        ]
        result = IAMV4Client(chunk_size=2).direct_auth_by_actions(
            "t1",
            SimpleNamespace(type="user", id="alice"),
            ["flow_view", "flow_edit", "flow_delete"],
            resource(),
        )
        self.assertEqual(list(result), ["flow_view", "flow_edit", "flow_delete"])
        self.assertEqual(api_request.call_count, 2)

    def test_resource_header_contains_tenant_and_never_body_tenant(self):
        api = DirectAuthResource()
        data = {"tenant_id": "t1", "system_id": "bk_sops"}
        headers = api.build_header(data)
        self.assertEqual(headers["X-Bk-Tenant-Id"], "t1")
        self.assertIn("bk_app_secret", json.loads(headers["x-bkapi-authorization"]))
        request_kwargs = api.before_request({"json": dict(data)})
        self.assertNotIn("tenant_id", request_kwargs["json"])

    def test_resource_rejects_non_json_http_error_and_missing_data(self):
        cases = (
            SimpleNamespace(
                headers={"X-Request-Id": "req-json"},
                status_code=502,
                json=mock.Mock(side_effect=ValueError("not json")),
                raise_for_status=mock.Mock(),
            ),
            SimpleNamespace(
                headers={"X-Request-Id": "req-http"},
                status_code=403,
                json=mock.Mock(return_value={"error": {"code": "DENIED", "message": "denied"}}),
                raise_for_status=mock.Mock(side_effect=HTTPError("403")),
            ),
            SimpleNamespace(
                headers={"X-Request-Id": "req-data"},
                status_code=200,
                json=mock.Mock(return_value={"result": True}),
                raise_for_status=mock.Mock(),
            ),
        )
        for response in cases:
            with self.subTest(request_id=response.headers["X-Request-Id"]):
                with self.assertRaises(APIRequestError) as context:
                    DirectAuthResource().parse_response(response)
                self.assertEqual(context.exception.data["request_id"], response.headers["X-Request-Id"])

    @mock.patch("gcloud.iam_auth.client.DirectAuthResource")
    def test_timeout_or_transport_error_maps_to_unavailable(self, resource_cls):
        resource_cls.return_value.request.side_effect = TimeoutError("timeout")
        with self.assertRaises(IAMV4Unavailable):
            IAMV4Client().direct_auth("t1", SimpleNamespace(type="user", id="alice"), "project_create")

    def test_gateway_error_is_logged_without_request_payload(self):
        resource = SimpleNamespace(
            name="apply URL",
            method="POST",
            action="/api/v1/open/application/permission-apply-urls/",
            request=mock.Mock(
                side_effect=APIRequestError(
                    module_name="bk_iam_v4",
                    url="/api/v1/open/application/permission-apply-urls/",
                    status_code=403,
                    result={
                        "code": "DENIED",
                        "message": "tenant denied",
                        "request_id": "req-apply",
                    },
                )
            ),
        )
        payload = {"tenant_id": "tenant-a", "secret": "must-not-be-logged"}
        with self.assertLogs("gcloud.iam_auth.client", level="ERROR") as logs, self.assertRaises(
            IAMV4Unavailable
        ) as context:
            _api_request(resource, payload)
        self.assertEqual(context.exception.request_id, "req-apply")
        output = "\n".join(logs.output)
        self.assertIn("status_code=403", output)
        self.assertIn("error_code=DENIED", output)
        self.assertIn("request_id=req-apply", output)
        self.assertNotIn("must-not-be-logged", output)


class ServiceAndApplyTest(unittest.TestCase):
    @mock.patch("gcloud.core.api_adapter.user_role.ScopeResolver")
    def test_functor_entry_uses_project_scoped_function_task_action(self, resolver_cls):
        resolver_cls.return_value.authorized_scope.return_value = AuthorizedScope({"project": {"2"}})
        request = SimpleNamespace(user=SimpleNamespace(username="alice", tenant_id="t1"))

        self.assertTrue(is_user_functor(request))
        resolver_cls.return_value.authorized_scope.assert_called_once_with("alice", "t1", "function_task_view")

    @mock.patch("gcloud.iam_auth.api.ScopeResolver")
    @mock.patch("gcloud.iam_auth.api.PermissionService")
    def test_common_flow_view_scope_allows_management_page(self, service_cls, resolver_cls):
        service_cls.return_value.is_allowed.return_value = False
        resolver_cls.return_value.authorized_scope.return_value = AuthorizedScope({"common_flow": {"1"}})

        is_allowed = iam_api._has_common_flow_management_permission("alice", "t1")

        self.assertTrue(is_allowed)
        resolver_cls.return_value.authorized_scope.assert_called_once_with("alice", "t1", "common_flow_view")

    @mock.patch("gcloud.iam_auth.api.ScopeResolver")
    @mock.patch("gcloud.iam_auth.api.PermissionService")
    def test_empty_common_flow_scopes_reject_management_page(self, service_cls, resolver_cls):
        service_cls.return_value.is_allowed.return_value = False
        resolver_cls.return_value.authorized_scope.return_value = AuthorizedScope.empty()

        is_allowed = iam_api._has_common_flow_management_permission("alice", "t1")

        self.assertFalse(is_allowed)
        self.assertEqual(resolver_cls.return_value.authorized_scope.call_count, 3)

    @mock.patch("gcloud.iam_auth.api.PermissionService")
    @mock.patch("gcloud.iam_auth.api.checks_from_simple_payload")
    def test_is_allow_checks_both_common_flow_and_project_permissions(self, parse_checks, service_cls):
        checks = [
            PermissionCheck("common_flow_create_task", resource("common_flow", "1")),
            PermissionCheck("project_common_create_task", resource("project", "2")),
        ]
        parse_checks.return_value = checks
        service_cls.return_value.is_allowed.side_effect = [True, False]
        request = RequestFactory().post(
            "/iam/api/is_allow/",
            data=json.dumps({"action": "common_flow_create_task", "resources": []}),
            content_type="application/json",
        )
        request.user = SimpleNamespace(username="alice", tenant_id="t1")

        response = iam_api.is_allow(request)
        response_data = json.loads(response.content)

        self.assertTrue(response_data["result"])
        self.assertFalse(response_data["data"]["is_allow"])
        self.assertEqual(service_cls.return_value.is_allowed.call_count, 2)

    @mock.patch("gcloud.iam_auth.apply_service._resource_from_id")
    def test_simple_payload_expands_common_flow_task_to_two_permission_checks(self, load_resource):
        load_resource.side_effect = lambda resource_type, resource_id, tenant_id: resource(
            resource_type, str(resource_id)
        )

        checks = checks_from_simple_payload(
            "common_flow_create_task",
            [
                {"type": "project", "id": 2},
                {"type": "common_flow", "id": 1},
            ],
            "t1",
        )

        self.assertEqual(
            [(check.action_id, check.resource.type, check.resource.id) for check in checks],
            [
                ("common_flow_create_task", "common_flow", "1"),
                ("project_common_create_task", "project", "2"),
            ],
        )

    @mock.patch("gcloud.iam_auth.apply_service._resource_from_id")
    def test_simple_payload_expands_common_flow_periodic_task_to_two_permission_checks(self, load_resource):
        load_resource.side_effect = lambda resource_type, resource_id, tenant_id: resource(
            resource_type, str(resource_id)
        )

        checks = checks_from_simple_payload(
            "common_flow_create_periodic_task",
            [
                {"type": "common_flow", "id": 1},
                {"type": "project", "id": 2},
            ],
            "t1",
        )

        self.assertEqual(
            [(check.action_id, check.resource.type, check.resource.id) for check in checks],
            [
                ("common_flow_create_periodic_task", "common_flow", "1"),
                ("project_common_create_periodic", "project", "2"),
            ],
        )

    def test_simple_payload_rejects_incomplete_common_flow_task_resources(self):
        with self.assertRaisesRegex(IAMV4ProtocolError, "one resource of each type"):
            checks_from_simple_payload(
                "common_flow_create_task",
                [{"type": "common_flow", "id": 1}],
                "t1",
            )

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_require_all_covers_all_four_dual_permission_outcomes(self, unused):
        for common_action, project_action in (
            ("common_flow_create_task", "project_common_create_task"),
            ("common_flow_create_periodic_task", "project_common_create_periodic"),
        ):
            checks = [
                PermissionCheck(common_action, resource("common_flow")),
                PermissionCheck(project_action, resource("project")),
            ]
            for outcomes, expected_missing in (
                ([True, True], []),
                ([False, True], [checks[0]]),
                ([True, False], [checks[1]]),
                ([False, False], checks),
            ):
                client = mock.Mock()
                client.direct_auth.side_effect = outcomes
                with self.subTest(actions=(common_action, project_action), outcomes=outcomes):
                    if not expected_missing:
                        PermissionService(client).require_all("alice", "t1", checks)
                    else:
                        with self.assertRaises(IAMPermissionDenied) as context:
                            PermissionService(client).require_all("alice", "t1", checks)
                        self.assertEqual(list(context.exception.missing_permissions), expected_missing)

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_require_all_aggregates_both_missing_permissions(self, unused):
        client = mock.Mock()
        client.direct_auth.return_value = False
        checks = [
            PermissionCheck("common_flow_create_task", resource("common_flow")),
            PermissionCheck("project_common_create_task", resource("project")),
        ]
        with self.assertRaises(IAMPermissionDenied) as context:
            PermissionService(client).require_all("alice", "t1", checks)
        self.assertEqual(context.exception.missing_permissions, tuple(checks))

    @mock.patch(
        "gcloud.iam_auth.service.validate_local_resources",
        side_effect=IAMResourceNotFound("flow", "1"),
    )
    def test_cross_tenant_or_missing_resource_stops_before_iam(self, unused):
        client = mock.Mock()
        with self.assertRaises(Exception):
            PermissionService(client).is_allowed("alice", "t1", PermissionCheck("flow_view", resource()))
        client.direct_auth.assert_not_called()

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_creator_permission_skips_remote_direct_auth(self, unused):
        client = mock.Mock()

        self.assertTrue(
            PermissionService(client).is_allowed("alice", "t1", PermissionCheck("flow_edit", creator_resource()))
        )

        client.direct_auth.assert_not_called()

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_creator_permission_only_applies_to_v3_configured_action(self, unused):
        client = mock.Mock()
        client.direct_auth.return_value = False

        self.assertFalse(
            PermissionService(client).is_allowed(
                "alice",
                "t1",
                PermissionCheck("common_flow_create_task", creator_resource("common_flow")),
            )
        )

        client.direct_auth.assert_called_once()

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_batch_permission_merges_creator_and_remote_results(self, unused):
        creator_flow = creator_resource("flow", "1")
        other_flow = creator_resource("flow", "2", username="bob")
        client = mock.Mock()
        client.direct_auth_by_resources.return_value = {"2": False}

        decisions = PermissionService(client).allowed_resources("alice", "t1", "flow_view", [creator_flow, other_flow])

        self.assertEqual(decisions, {"1": True, "2": False})
        client.direct_auth_by_resources.assert_called_once_with("t1", mock.ANY, "flow_view", [other_flow])

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_action_permission_only_sends_non_creator_actions_to_gateway(self, unused):
        common_flow = creator_resource("common_flow")
        client = mock.Mock()
        client.direct_auth_by_actions.return_value = {"common_flow_create_task": False}

        decisions = PermissionService(client).allowed_actions(
            "alice",
            "t1",
            ["common_flow_view", "common_flow_edit", "common_flow_create_task"],
            common_flow,
        )

        self.assertEqual(
            decisions,
            {
                "common_flow_view": True,
                "common_flow_edit": True,
                "common_flow_create_task": False,
            },
        )
        client.direct_auth_by_actions.assert_called_once_with("t1", mock.ANY, ["common_flow_create_task"], common_flow)

    @mock.patch("gcloud.iam_auth.service.validate_local_resources")
    def test_resource_action_matrix_validates_local_resources_once(self, validate_resources):
        resources = [resource("flow", "1"), resource("flow", "2")]
        client = mock.Mock()
        client.direct_auth_by_resources.side_effect = [
            {"1": True, "2": False},
            {"1": False, "2": True},
        ]

        decisions = PermissionService(client).allowed_resource_actions(
            "alice", "t1", ["flow_view", "flow_edit"], resources
        )

        self.assertEqual(
            decisions,
            {
                "1": {"flow_view": True, "flow_edit": False},
                "2": {"flow_view": False, "flow_edit": True},
            },
        )
        validate_resources.assert_called_once_with(resources, "t1")

    @mock.patch("gcloud.iam_auth.apply_service.validate_local_resource")
    def test_apply_service_deduplicates_and_uses_server_resource_path(self, unused):
        check = PermissionCheck("flow_view", resource())
        permissions = ApplyService().build_permissions([check, check], "t1")
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0]["resources"][0]["ancestors"], [{"type": "project", "id": "2"}])

    @mock.patch("gcloud.iam_auth.apply_service._resource_from_id")
    def test_apply_payload_ignores_submitted_ancestor_and_reloads_resource(self, load_resource):
        load_resource.return_value = resource("flow", "1", project_id="2")
        checks = checks_from_permission_payload(
            {
                "actions": [
                    {
                        "id": "flow_view",
                        "related_resource_types": [
                            {
                                "type": "flow",
                                "instances": [
                                    [
                                        {"type": "project", "id": "forged-project"},
                                        {"type": "flow", "id": "1"},
                                    ]
                                ],
                            }
                        ],
                    }
                ]
            },
            "t1",
        )
        self.assertEqual(checks[0].resource.attribute["_bk_iam_path_"], "/project,2/")
        load_resource.assert_called_once_with("flow", "1", "t1")

    def test_apply_payload_allows_iam_to_select_project_scope(self):
        checks = checks_from_permission_payload(
            {"actions": [{"id": "project_view", "related_resource_types": []}]},
            "t1",
        )

        self.assertEqual(checks, [PermissionCheck("project_view")])
        self.assertEqual(
            ApplyService().build_permissions(checks, "t1"),
            [{"action_id": "project_view"}],
        )

    @mock.patch("gcloud.iam_auth.scope_resolver.creator_local_queryset")
    @mock.patch("gcloud.iam_auth.scope_resolver.local_resource_queryset")
    def test_project_scope_is_built_lazily_without_materializing_descendant_ids(self, local_queryset, creator_queryset):
        project_queryset = mock.MagicMock(name="project_queryset")
        task_queryset = mock.MagicMock(name="task_queryset")
        local_queryset.side_effect = lambda resource_type, tenant_id: {
            "project": project_queryset,
            "task": task_queryset,
        }[resource_type]
        creator_queryset.return_value = mock.MagicMock(name="creator_queryset")
        client = mock.Mock()
        client.list_authorized_resources.return_value = [{"type": "project", "ids": ["2"]}]

        scope = ScopeResolver(client).authorized_scope("alice", "t1", "task_view")

        self.assertIsNotNone(scope.queryset("project"))
        self.assertIsNotNone(scope.queryset("task"))
        project_queryset.values_list.assert_not_called()
        task_queryset.values_list.assert_not_called()
        creator_queryset.assert_called_once_with("task", "alice", "t1")

    @mock.patch("gcloud.iam_auth.scope_resolver.creator_local_queryset")
    def test_scope_does_not_add_creator_resources_for_unconfigured_action(self, creator_queryset):
        client = mock.Mock()
        client.list_authorized_resources.return_value = []

        scope = ScopeResolver(client).authorized_scope("alice", "t1", "common_flow_create_task")

        self.assertTrue(scope.is_empty)
        creator_queryset.assert_not_called()

    @mock.patch("gcloud.iam_auth.request_resources._load_resources")
    def test_trust_resource_loader_rejects_route_project_mismatch(self, load_resources):
        load_resources.return_value = [resource("task", project_id="2")]
        request = SimpleNamespace(
            user=SimpleNamespace(tenant_id="t1"),
            project=SimpleNamespace(id=3),
            is_trust=True,
        )
        with self.assertRaises(IAMResourceNotFound):
            load_resource_for_request(request, "task", "1")


class CallbackSecurityTest(unittest.TestCase):
    def request(self, token="token", tenant="t1"):
        encoded = base64.b64encode("bk_iam:{}".format(token).encode()).decode()
        meta = {"HTTP_AUTHORIZATION": "Basic {}".format(encoded)}
        if tenant is not None:
            meta["HTTP_X_BK_TENANT_ID"] = tenant
        return SimpleNamespace(META=meta)

    def test_callback_has_exactly_seven_providers(self):
        self.assertEqual(set(PROVIDERS), {item["id"] for item in RESOURCES})

    def test_list_cache_key_covers_full_tenant_query_context(self):
        base = list_instance_cache_key("t1", "flow", {"type": "project", "id": "2"}, "x", 1, 20)
        variants = (
            list_instance_cache_key("t2", "flow", {"type": "project", "id": "2"}, "x", 1, 20),
            list_instance_cache_key("t1", "task", {"type": "project", "id": "2"}, "x", 1, 20),
            list_instance_cache_key("t1", "flow", {"type": "project", "id": "3"}, "x", 1, 20),
            list_instance_cache_key("t1", "flow", {"type": "project", "id": "2"}, "y", 1, 20),
            list_instance_cache_key("t1", "flow", {"type": "project", "id": "2"}, "x", 2, 20),
            list_instance_cache_key("t1", "flow", {"type": "project", "id": "2"}, "x", 1, 50),
        )
        self.assertNotIn(base, variants)

    @mock.patch("gcloud.iam_auth.resource_api_v4.auth.IAMV4Client")
    @mock.patch.object(callback_auth.cache, "set")
    @mock.patch.object(callback_auth.cache, "get", return_value=None)
    def test_callback_token_cache_key_contains_system_and_tenant(self, cache_get, cache_set, client_cls):
        client_cls.return_value.retrieve_callback_token.return_value = "token"
        self.assertEqual(callback_auth.get_cached_callback_token("t1"), "token")
        key = cache_get.call_args.args[0]
        self.assertIn("bk_sops", key)
        self.assertIn("t1", key)
        self.assertEqual(cache_set.call_args.args[0], key)

    @mock.patch("gcloud.iam_auth.resource_api_v4.auth.get_cached_callback_token")
    def test_callback_rotates_token_once_and_rejects_wrong_token(self, get_token):
        get_token.side_effect = ["old", "new"]
        with self.assertRaises(callback_auth.CallbackUnauthorized):
            callback_auth.authenticate_callback(self.request("wrong"))
        self.assertEqual(get_token.call_count, 2)
        self.assertTrue(get_token.call_args.kwargs["force_refresh"])

    @override_settings(IAM_V4_MODEL_REGISTRATION_TENANT_ID="system")
    def test_callback_rejects_request_without_tenant_header(self):
        with self.assertRaises(callback_auth.CallbackTenantMissing):
            callback_auth.authenticate_callback(self.request(tenant=None))

    @mock.patch("gcloud.iam_auth.resource_api_v4.auth.get_cached_callback_token")
    def test_callback_endpoint_returns_400_before_token_lookup_when_tenant_is_missing(self, get_token):
        request = self.request(tenant=None)
        request.method = "POST"
        request.body = b"{}"
        request.META["HTTP_X_REQUEST_ID"] = "req-tenant"

        response = resource_callback(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["X-Request-Id"], "req-tenant")
        self.assertEqual(json.loads(response.content)["error"]["code"], "TENANT_REQUIRED")
        get_token.assert_not_called()

    def test_callback_rejects_non_post_and_preserves_request_id(self):
        request = SimpleNamespace(method="GET", META={"HTTP_X_REQUEST_ID": "req-method"})
        response = resource_callback(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["X-Request-Id"], "req-method")
        self.assertEqual(json.loads(response.content)["error"]["code"], "METHOD_NOT_ALLOWED")

    @mock.patch("gcloud.iam_auth.resource_api_v4.dispatcher.authenticate_callback")
    def test_callback_rejects_invalid_json_without_calling_provider(self, authenticate):
        authenticate.return_value = "t1"
        request = SimpleNamespace(method="POST", META={"HTTP_X_REQUEST_ID": "req-body"}, body=b"{")
        with self.assertLogs("root", level="WARNING") as logs:
            response = resource_callback(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["X-Request-Id"], "req-body")
        self.assertEqual(json.loads(response.content)["error"]["code"], "INVALID_REQUEST")
        self.assertIn("error_type=JSONDecodeError request_id=req-body", logs.output[0])

    @mock.patch("gcloud.iam_auth.resource_api_v4.dispatcher.authenticate_callback", return_value="t1")
    def test_callback_logs_validation_error_without_resource_ids(self, unused):
        request = SimpleNamespace(
            method="POST",
            META={"HTTP_X_REQUEST_ID": "req-validation"},
            body=json.dumps(
                {
                    "type": "project",
                    "method": "fetch_instance_info",
                    "filter": {"ids": ["sensitive-resource-id"]},
                    "requires": ["display_name", "display_name"],
                }
            ).encode(),
        )
        with self.assertLogs("root", level="WARNING") as logs:
            response = resource_callback(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("type=project method=fetch_instance_info", logs.output[0])
        self.assertIn("request_id=req-validation", logs.output[0])
        self.assertNotIn("sensitive-resource-id", logs.output[0])


class MiddlewareAndRoleResponseTest(unittest.TestCase):
    def test_permission_denied_is_499_with_two_actions_and_request_id(self):
        checks = [
            PermissionCheck("common_flow_create_task", resource("common_flow")),
            PermissionCheck("project_common_create_task", resource("project")),
        ]
        request = SimpleNamespace(META={"HTTP_X_REQUEST_ID": "req-1"})
        response = IAMPermissionDeniedMiddleware(lambda unused: None).process_exception(
            request, IAMPermissionDenied(checks)
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 499)
        self.assertEqual(data["request_id"], "req-1")
        self.assertEqual(
            [item["id"] for item in data["permission"]["actions"]],
            ["common_flow_create_task", "project_common_create_task"],
        )

    def test_resource_not_found_and_iam_unavailable_are_fail_closed(self):
        middleware = IAMPermissionDeniedMiddleware(lambda unused: None)
        request = SimpleNamespace(META={"HTTP_X_REQUEST_ID": "req-fail"})
        not_found = middleware.process_exception(request, IAMResourceNotFound("task", "1"))
        unavailable = middleware.process_exception(request, IAMV4Unavailable(request_id="req-iam"))
        self.assertEqual(not_found.status_code, 404)
        self.assertEqual(json.loads(not_found.content)["code"], "RESOURCE_NOT_FOUND")
        self.assertEqual(unavailable.status_code, 503)
        self.assertEqual(json.loads(unavailable.content)["request_id"], "req-iam")

    def test_role_response_matches_documented_id_list(self):
        with self.assertRaises(IAMV4ProtocolError):
            validate_registration_response([{"id": "r1"}], ["r1"])
        with self.assertRaises(IAMV4ProtocolError):
            validate_registration_response(["r1"], ["r1", "r2"])
        validate_registration_response(["r2", "r1"], ["r1", "r2"])


if __name__ == "__main__":
    unittest.main()

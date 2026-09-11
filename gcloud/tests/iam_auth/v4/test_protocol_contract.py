import base64
import json
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase, override_settings

from gcloud.iam_auth.api_v4.resources import (
    BatchCreateActionResource,
    BatchCreateResourceTypeResource,
    BatchCreateRoleResource,
    CreateSystemResource,
    DirectAuthByActionsResource,
    DirectAuthByResourcesResource,
    DirectAuthResource,
    GenerateApplyURLResource,
    ListActionResource,
    ListAuthorizedResourceResource,
    ListResourceTypeResource,
    ListRoleResource,
    RetrieveCallbackTokenResource,
    RetrieveSystemResource,
    UpdateActionResource,
    UpdateResourceTypeResource,
    UpdateRoleResource,
    UpdateSystemResource,
)
from gcloud.iam_auth.apply_service import ApplyService
from gcloud.iam_auth.client import IAMV4Client
from gcloud.iam_auth.domains import build_iam_v4_api_url
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.models import Resource
from gcloud.iam_auth.resource_api_v4 import auth as callback_auth
from gcloud.iam_auth.resource_api_v4.dispatcher import resource_callback
from gcloud.iam_auth.resource_api_v4.providers import PROVIDERS
from gcloud.iam_auth.topology import project_path
from gcloud.iam_auth.types import PermissionCheck


def flow_resource(resource_id="1", project_id="2"):
    return Resource(
        "bk_sops",
        "flow",
        resource_id,
        {"name": "flow-{}".format(resource_id), "_bk_iam_path_": project_path(project_id)},
    )


class EndpointAndAuthenticationContractTest(SimpleTestCase):
    def test_all_v4_resources_use_the_expected_method_and_path(self):
        contracts = {
            DirectAuthResource: ("POST", "/api/v1/open/rbac/authorization/systems/{system_id}/auth/"),
            DirectAuthByActionsResource: (
                "POST",
                "/api/v1/open/rbac/authorization/systems/{system_id}/auth-by-actions/",
            ),
            DirectAuthByResourcesResource: (
                "POST",
                "/api/v1/open/rbac/authorization/systems/{system_id}/auth-by-resources/",
            ),
            ListAuthorizedResourceResource: (
                "POST",
                "/api/v1/open/rbac/authorization/systems/{system_id}/relation/authorized-resources/",
            ),
            GenerateApplyURLResource: ("POST", "/api/v1/open/application/permission-apply-urls/"),
            RetrieveCallbackTokenResource: (
                "GET",
                "/api/v1/open/rbac/model/systems/{system_id}/auth-token/",
            ),
            BatchCreateRoleResource: (
                "POST",
                "/api/v1/open/rbac/model/systems/{system_id}/roles/",
            ),
            ListRoleResource: ("GET", "/api/v1/open/rbac/model/systems/{system_id}/roles/"),
            UpdateRoleResource: (
                "PATCH",
                "/api/v1/open/rbac/model/systems/{system_id}/roles/{role_id}/",
            ),
            CreateSystemResource: ("POST", "/api/v1/open/rbac/model/systems/"),
            RetrieveSystemResource: ("GET", "/api/v1/open/rbac/model/systems/{system_id}/"),
            UpdateSystemResource: ("PATCH", "/api/v1/open/rbac/model/systems/{system_id}/"),
            BatchCreateResourceTypeResource: ("POST", "/api/v1/open/rbac/model/systems/{system_id}/resource-types/"),
            BatchCreateActionResource: ("POST", "/api/v1/open/rbac/model/systems/{system_id}/actions/"),
            ListResourceTypeResource: ("GET", "/api/v1/open/rbac/model/systems/{system_id}/resource-types/"),
            UpdateResourceTypeResource: (
                "PATCH",
                "/api/v1/open/rbac/model/systems/{system_id}/resource-types/{resource_type_id}/",
            ),
            ListActionResource: ("GET", "/api/v1/open/rbac/model/systems/{system_id}/actions/"),
            UpdateActionResource: ("PATCH", "/api/v1/open/rbac/model/systems/{system_id}/actions/{action_id}/"),
        }
        for resource_class, (method, path) in contracts.items():
            with self.subTest(resource=resource_class.__name__):
                self.assertEqual(resource_class.method, method)
                self.assertEqual(resource_class.action, path)

    @override_settings(BK_IAM_V4_API_URL="https://iam-v4.example.test/dev/")
    def test_explicit_v4_url_has_priority_and_trailing_slash_is_removed(self):
        self.assertEqual(build_iam_v4_api_url(), "https://iam-v4.example.test/dev")

    @override_settings(
        BK_IAM_V4_API_URL="",
        BK_API_URL_TMPL="https://api.example.test/{api_name}",
        BKIAM_APIGW_NAME="bkiam-v4",
        BK_APIGW_STAGE_NAME="stage",
    )
    def test_gateway_fallback_uses_configured_name_and_non_product_stage(self):
        self.assertEqual(build_iam_v4_api_url(), "https://api.example.test/bkiam-v4/stage")

    @override_settings(
        BK_IAM_V4_API_URL="",
        BK_API_URL_TMPL="https://api.example.test/{api_name}",
        BKIAM_APIGW_NAME="bkiam-v4",
        BK_APIGW_STAGE_NAME="prod",
    )
    def test_gateway_fallback_uses_product_stage(self):
        self.assertEqual(build_iam_v4_api_url(), "https://api.example.test/bkiam-v4/prod")

    @override_settings(
        BK_APP_CODE="sops-app",
        BK_APP_SECRET="sops-secret",
        IAM_V4_TENANT_HEADER="X-Bk-Tenant-Id",
    )
    def test_outbound_auth_header_uses_sops_identity_and_tenant(self):
        payload = {"tenant_id": "tenant-a", "system_id": "bk_sops", "action_id": "project_create"}
        resource = DirectAuthResource()
        headers = resource.build_header(payload)
        authorization = json.loads(headers["x-bkapi-authorization"])

        self.assertEqual(
            authorization,
            {
                "bk_app_code": "sops-app",
                "bk_app_secret": "sops-secret",
            },
        )
        self.assertEqual(headers["X-Bk-Tenant-Id"], "tenant-a")
        request_kwargs = resource.before_request({"json": dict(payload)})
        self.assertNotIn("tenant_id", request_kwargs["json"])


class ClientProtocolContractTest(SimpleTestCase):
    @mock.patch("gcloud.iam_auth.client._api_request")
    def test_direct_auth_sends_exact_subject_action_resource_and_tenant(self, api_request):
        api_request.return_value = {"allowed": True}
        allowed = IAMV4Client().direct_auth(
            "tenant-a",
            SimpleNamespace(type="user", id="alice"),
            "flow_view",
            flow_resource(),
        )
        self.assertTrue(allowed)
        resource, payload = api_request.call_args.args
        self.assertIsInstance(resource, DirectAuthResource)
        self.assertEqual(payload["tenant_id"], "tenant-a")
        self.assertEqual(payload["subject"], {"type": "user", "id": "alice"})
        self.assertEqual(payload["action_id"], "flow_view")
        self.assertEqual(payload["resource"], {"id": "1"})

    @mock.patch("gcloud.iam_auth.client._api_request")
    def test_auth_by_resources_chunks_and_merges_decisions_by_resource_id(self, api_request):
        api_request.side_effect = lambda unused, payload: [
            {"resource_id": item["id"], "allowed": item["id"] != "2"} for item in reversed(payload["resources"])
        ]
        resources = [flow_resource("1"), flow_resource("2"), flow_resource("3")]
        result = IAMV4Client(chunk_size=2).direct_auth_by_resources(
            "tenant-a", SimpleNamespace(type="user", id="alice"), "flow_view", resources
        )
        self.assertEqual(result, {"1": True, "2": False, "3": True})
        self.assertEqual(api_request.call_count, 2)

    @mock.patch("gcloud.iam_auth.client._api_request")
    def test_authorized_resources_and_callback_token_are_strictly_parsed(self, api_request):
        client = IAMV4Client()
        api_request.return_value = [{"type": "project", "ids": ["2"]}]
        scope = client.list_authorized_resources("tenant-a", SimpleNamespace(type="user", id="alice"), "flow_view")
        self.assertEqual(scope, [{"type": "project", "ids": ["2"]}])

        api_request.return_value = {"auth_token": "callback-token"}
        self.assertEqual(client.retrieve_callback_token("tenant-a"), "callback-token")
        api_request.return_value = {"auth_token": ""}
        with self.assertRaises(IAMV4ProtocolError):
            client.retrieve_callback_token("tenant-a")

    @mock.patch("gcloud.iam_auth.apply_service._api_request")
    def test_apply_url_uses_system_action_payload_and_rejects_missing_url(self, api_request):
        api_request.return_value = {"url": "https://iam.example.test/apply/1"}
        result = ApplyService().generate_url("tenant-a", [PermissionCheck("project_create")])
        self.assertEqual(result, "https://iam.example.test/apply/1")
        resource, payload = api_request.call_args.args
        self.assertIsInstance(resource, GenerateApplyURLResource)
        self.assertEqual(
            payload,
            {
                "tenant_id": "tenant-a",
                "system_id": "bk_sops",
                "permissions": [{"action_id": "project_create"}],
            },
        )

        api_request.return_value = {"unexpected": "value"}
        with self.assertRaises(IAMV4ProtocolError):
            ApplyService().generate_url("tenant-a", [PermissionCheck("project_create")])

    @mock.patch("gcloud.iam_auth.apply_service._api_request")
    def test_apply_url_can_defer_project_selection_to_iam(self, api_request):
        api_request.return_value = {"url": "https://iam.example.test/apply/2"}

        ApplyService().generate_url("tenant-a", [PermissionCheck("project_view")])

        self.assertEqual(
            api_request.call_args.args[1]["permissions"],
            [{"action_id": "project_view"}],
        )


class CallbackEndToEndUnitTest(SimpleTestCase):
    @staticmethod
    def callback_request(payload, request_id="request-1"):
        return SimpleNamespace(
            method="POST",
            META={"HTTP_X_REQUEST_ID": request_id},
            body=json.dumps(payload).encode(),
        )

    @staticmethod
    def basic_request(username="bk_iam", token="callback-token", tenant="tenant-a"):
        encoded = base64.b64encode("{}:{}".format(username, token).encode()).decode()
        return SimpleNamespace(
            META={
                "HTTP_AUTHORIZATION": "Basic {}".format(encoded),
                "HTTP_X_BK_TENANT_ID": tenant,
            }
        )

    @mock.patch("gcloud.iam_auth.resource_api_v4.auth.get_cached_callback_token", return_value="callback-token")
    def test_callback_basic_auth_accepts_only_bk_iam_and_matching_token(self, get_token):
        self.assertEqual(callback_auth.authenticate_callback(self.basic_request()), "tenant-a")
        get_token.assert_called_once_with("tenant-a")
        with self.assertRaises(callback_auth.CallbackUnauthorized):
            callback_auth.authenticate_callback(self.basic_request(username="other"))

    @mock.patch("gcloud.iam_auth.resource_api_v4.dispatcher.authenticate_callback", return_value="tenant-a")
    def test_list_instance_dispatches_tenant_filter_and_page_and_preserves_request_id(self, unused):
        provider = mock.Mock()
        provider.list_instance.return_value = {"count": 1, "results": [{"id": "1", "display_name": "P"}]}
        request = self.callback_request(
            {
                "type": "project",
                "method": "list_instance",
                "filter": {"keyword": "P"},
                "page": {"page": 2, "page_size": 20},
            },
            request_id="request-list",
        )
        with mock.patch.dict(PROVIDERS, {"project": provider}):
            response = resource_callback(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Request-Id"], "request-list")
        self.assertEqual(json.loads(response.content)["data"]["count"], 1)
        provider.list_instance.assert_called_once_with("tenant-a", parent=None, keyword="P", page=2, page_size=20)

    @mock.patch("gcloud.iam_auth.resource_api_v4.dispatcher.authenticate_callback", return_value="tenant-a")
    def test_fetch_instance_info_dispatches_ids_and_requires(self, unused):
        provider = mock.Mock()
        provider.fetch_instance_info.return_value = [
            {"id": "1", "display_name": "Flow", "_bk_iam_path_": "/project,2/"}
        ]
        request = self.callback_request(
            {
                "type": "flow",
                "method": "fetch_instance_info",
                "filter": {"ids": ["1"]},
                "requires": ["id", "display_name", "_bk_iam_path_"],
            }
        )
        with mock.patch.dict(PROVIDERS, {"flow": provider}):
            response = resource_callback(request)

        self.assertEqual(response.status_code, 200)
        provider.fetch_instance_info.assert_called_once_with(
            "tenant-a", ids=["1"], requires=["id", "display_name", "_bk_iam_path_"]
        )

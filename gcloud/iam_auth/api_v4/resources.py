import abc
import json

from bk_resource import BkApiResource
from bk_resource.exceptions import APIRequestError
from django.conf import settings
from requests.exceptions import HTTPError

from gcloud.iam_auth.api_v4.serializers import (
    BatchCreateActionRequestSerializer,
    BatchCreateResourceTypeRequestSerializer,
    BatchCreateRoleRequestSerializer,
    CreateSystemRequestSerializer,
    DirectAuthByActionsRequestSerializer,
    DirectAuthByResourcesRequestSerializer,
    DirectAuthRequestSerializer,
    GenerateApplyURLRequestSerializer,
    ListAuthorizedResourceRequestSerializer,
    ListModelObjectRequestSerializer,
    RetrieveCallbackTokenRequestSerializer,
    RetrieveSystemRequestSerializer,
    UpdateActionRequestSerializer,
    UpdateResourceTypeRequestSerializer,
    UpdateRoleRequestSerializer,
    UpdateSystemRequestSerializer,
)
from gcloud.iam_auth.domains import build_iam_v4_api_url


class IAMV4BaseResource(BkApiResource, abc.ABC):
    module_name = "bk_iam_v4"
    body_exclude_keys = ("tenant_id",)
    platform_authorization = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.TIMEOUT = settings.IAM_V4_REQUEST_TIMEOUT

    @property
    def base_url(self):
        return build_iam_v4_api_url()

    def build_url(self, validated_request_data):
        url = super().build_url(validated_request_data)
        for key in self.url_keys:
            validated_request_data.pop(key, None)
        return url

    def build_header(self, validated_request_data):
        tenant_id = validated_request_data.get("tenant_id")
        authorization = {
            "bk_app_code": settings.BK_APP_CODE,
            "bk_app_secret": settings.BK_APP_SECRET,
        }

        return {
            "Content-Type": "application/json",
            "x-bkapi-authorization": json.dumps(authorization),
            settings.IAM_V4_TENANT_HEADER: tenant_id,
        }

    def before_request(self, kwargs):
        kwargs = super().before_request(kwargs)
        for container_name in ("json", "params"):
            container = kwargs.get(container_name)
            if isinstance(container, dict):
                for key in self.body_exclude_keys:
                    container.pop(key, None)
        return kwargs

    def parse_response(self, response):
        request_id = response.headers.get("X-Request-Id", "") or response.headers.get("x-bkapi-request-id", "")
        if response.status_code == 204:
            response.raise_for_status()
            return None
        try:
            result_json = response.json()
        except Exception as error:
            raise APIRequestError(
                module_name=self.module_name,
                url=self.action,
                status_code=response.status_code,
                result={
                    "message": "IAM V4 returned a non-JSON response",
                    "request_id": request_id,
                    "status_code": response.status_code,
                },
            ) from error
        if not request_id and isinstance(result_json, dict):
            request_id = result_json.get("request_id", "")

        try:
            response.raise_for_status()
        except HTTPError as error:
            error_data = result_json.get("error", {}) if isinstance(result_json, dict) else {}
            raise APIRequestError(
                module_name=self.module_name,
                url=self.action,
                status_code=response.status_code,
                result={
                    "code": error_data.get("code") if isinstance(error_data, dict) else None,
                    "message": error_data.get("message", "IAM V4 request failed")
                    if isinstance(error_data, dict)
                    else "IAM V4 request failed",
                    "request_id": request_id,
                    "status_code": response.status_code,
                },
            ) from error

        if not isinstance(result_json, dict) or "data" not in result_json:
            raise APIRequestError(
                module_name=self.module_name,
                url=self.action,
                status_code=response.status_code,
                result={
                    "message": "IAM V4 response is missing data",
                    "request_id": request_id,
                    "status_code": response.status_code,
                },
            )
        return result_json["data"]


class DirectAuthResource(IAMV4BaseResource):
    name = "IAM V4 direct auth"
    action = "/api/v1/open/rbac/authorization/systems/{system_id}/auth/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = DirectAuthRequestSerializer


class DirectAuthByActionsResource(IAMV4BaseResource):
    name = "IAM V4 auth by actions"
    action = "/api/v1/open/rbac/authorization/systems/{system_id}/auth-by-actions/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = DirectAuthByActionsRequestSerializer


class DirectAuthByResourcesResource(IAMV4BaseResource):
    name = "IAM V4 auth by resources"
    action = "/api/v1/open/rbac/authorization/systems/{system_id}/auth-by-resources/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = DirectAuthByResourcesRequestSerializer


class ListAuthorizedResourceResource(IAMV4BaseResource):
    name = "IAM V4 authorized resources"
    action = "/api/v1/open/rbac/authorization/systems/{system_id}/relation/authorized-resources/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = ListAuthorizedResourceRequestSerializer


class GenerateApplyURLResource(IAMV4BaseResource):
    name = "IAM V4 permission apply URL"
    action = "/api/v1/open/application/permission-apply-urls/"
    method = "POST"
    RequestSerializer = GenerateApplyURLRequestSerializer


class RetrieveCallbackTokenResource(IAMV4BaseResource):
    name = "IAM V4 callback token"
    action = "/api/v1/open/rbac/model/systems/{system_id}/auth-token/"
    method = "GET"
    url_keys = ["system_id"]
    RequestSerializer = RetrieveCallbackTokenRequestSerializer


class CreateSystemResource(IAMV4BaseResource):
    name = "IAM V4 create system"
    action = "/api/v1/open/rbac/model/systems/"
    method = "POST"
    RequestSerializer = CreateSystemRequestSerializer


class RetrieveSystemResource(IAMV4BaseResource):
    name = "IAM V4 retrieve system"
    action = "/api/v1/open/rbac/model/systems/{system_id}/"
    method = "GET"
    url_keys = ["system_id"]
    RequestSerializer = RetrieveSystemRequestSerializer


class UpdateSystemResource(IAMV4BaseResource):
    name = "IAM V4 update system"
    action = "/api/v1/open/rbac/model/systems/{system_id}/"
    method = "PATCH"
    url_keys = ["system_id"]
    RequestSerializer = UpdateSystemRequestSerializer


class BatchCreateResourceTypeResource(IAMV4BaseResource):
    name = "IAM V4 batch create resource types"
    action = "/api/v1/open/rbac/model/systems/{system_id}/resource-types/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = BatchCreateResourceTypeRequestSerializer

    def before_request(self, kwargs):
        kwargs = super().before_request(kwargs)
        if isinstance(kwargs.get("json"), dict):
            kwargs["json"] = kwargs["json"].get("resource_types", [])
        return kwargs


class ListResourceTypeResource(IAMV4BaseResource):
    name = "IAM V4 list resource types"
    action = "/api/v1/open/rbac/model/systems/{system_id}/resource-types/"
    method = "GET"
    url_keys = ["system_id"]
    RequestSerializer = ListModelObjectRequestSerializer


class UpdateResourceTypeResource(IAMV4BaseResource):
    name = "IAM V4 update resource type"
    action = "/api/v1/open/rbac/model/systems/{system_id}/resource-types/{resource_type_id}/"
    method = "PATCH"
    url_keys = ["system_id", "resource_type_id"]
    RequestSerializer = UpdateResourceTypeRequestSerializer


class BatchCreateActionResource(IAMV4BaseResource):
    name = "IAM V4 batch create actions"
    action = "/api/v1/open/rbac/model/systems/{system_id}/actions/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = BatchCreateActionRequestSerializer

    def before_request(self, kwargs):
        kwargs = super().before_request(kwargs)
        if isinstance(kwargs.get("json"), dict):
            kwargs["json"] = kwargs["json"].get("actions", [])
        return kwargs


class ListActionResource(IAMV4BaseResource):
    name = "IAM V4 list actions"
    action = "/api/v1/open/rbac/model/systems/{system_id}/actions/"
    method = "GET"
    url_keys = ["system_id"]
    RequestSerializer = ListModelObjectRequestSerializer


class UpdateActionResource(IAMV4BaseResource):
    name = "IAM V4 update action"
    action = "/api/v1/open/rbac/model/systems/{system_id}/actions/{action_id}/"
    method = "PATCH"
    url_keys = ["system_id", "action_id"]
    RequestSerializer = UpdateActionRequestSerializer


class BatchCreateRoleResource(IAMV4BaseResource):
    name = "IAM V4 batch create roles"
    action = "/api/v1/open/rbac/model/systems/{system_id}/roles/"
    method = "POST"
    url_keys = ["system_id"]
    RequestSerializer = BatchCreateRoleRequestSerializer

    def before_request(self, kwargs):
        kwargs = super().before_request(kwargs)
        if isinstance(kwargs.get("json"), dict):
            kwargs["json"] = kwargs["json"].get("roles", [])
        return kwargs


class ListRoleResource(IAMV4BaseResource):
    name = "IAM V4 list roles"
    action = "/api/v1/open/rbac/model/systems/{system_id}/roles/"
    method = "GET"
    url_keys = ["system_id"]
    RequestSerializer = ListModelObjectRequestSerializer


class UpdateRoleResource(IAMV4BaseResource):
    name = "IAM V4 update role"
    action = "/api/v1/open/rbac/model/systems/{system_id}/roles/{role_id}/"
    method = "PATCH"
    url_keys = ["system_id", "role_id"]
    RequestSerializer = UpdateRoleRequestSerializer

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

import logging

import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET, require_POST

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.conf import settings
from gcloud.plugin_gateway.exceptions import (
    PluginGatewayConflictError,
    PluginGatewayPluginNotEnabledError,
    PluginGatewayPluginNotFoundError,
    PluginGatewaySourceUnavailableError,
    PluginGatewayVersionNotFoundError,
)
from gcloud.plugin_gateway.models import PluginGatewayRun, PluginGatewaySourceConfig
from gcloud.plugin_gateway.serializers import PluginGatewayRunCreateSerializer, PluginGatewayRunStatusQuerySerializer
from gcloud.plugin_gateway.services.catalog import PluginGatewayCatalogService
from gcloud.plugin_gateway.services.execution import PluginGatewayExecutionService

logger = logging.getLogger("root")

ERROR_TYPE_PLUGIN_NOT_ENABLED = "plugin_not_enabled"
ERROR_TYPE_PLUGIN_VERSION_UNAVAILABLE = "plugin_version_unavailable"
ERROR_TYPE_PLUGIN_REMOVED = "plugin_removed"
ERROR_TYPE_SOURCE_UNREACHABLE = "source_unreachable"


def _error_response(message, code, error_type=""):
    return {"result": False, "message": message, "code": code, "error_type": error_type}


def _load_request_body(request):
    try:
        return json.loads(request.body or "{}")
    except (ValueError, TypeError):
        raise ValueError("invalid json format")


def _caller_app_code(request):
    app = getattr(request, "app", None)
    if app is None:
        raise PermissionError("request is not authorized via apigw")

    caller_app_code = getattr(app, settings.APIGW_MANAGER_APP_CODE_KEY, "")
    if not caller_app_code:
        raise PermissionError("request app code is missing")
    return caller_app_code


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def get_plugin_gateway_categories(request):
    return {
        "result": True,
        "data": {"categories": PluginGatewayCatalogService.get_categories()},
        "code": err_code.SUCCESS.code,
    }


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def get_plugin_gateway_list(request):
    try:
        data = PluginGatewayCatalogService.get_plugin_list(request=request)
    except PluginGatewaySourceUnavailableError as e:
        return _error_response(str(e), err_code.INVALID_OPERATION.code, ERROR_TYPE_SOURCE_UNREACHABLE)

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def get_plugin_gateway_detail(request, plugin_id):
    try:
        plugin_detail = PluginGatewayCatalogService.get_plugin_detail(
            request=request,
            plugin_id=plugin_id,
            version=request.GET.get("version"),
        )
    except PluginGatewayVersionNotFoundError as e:
        return _error_response(str(e), err_code.REQUEST_PARAM_INVALID.code, ERROR_TYPE_PLUGIN_VERSION_UNAVAILABLE)
    except PluginGatewaySourceUnavailableError as e:
        return _error_response(str(e), err_code.INVALID_OPERATION.code, ERROR_TYPE_SOURCE_UNREACHABLE)

    if plugin_detail is None:
        return _error_response(
            "plugin gateway plugin({}) does not exist".format(plugin_id),
            err_code.CONTENT_NOT_EXIST.code,
            ERROR_TYPE_PLUGIN_REMOVED,
        )

    return {"result": True, "data": plugin_detail, "code": err_code.SUCCESS.code}


@login_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def create_plugin_gateway_run(request):
    try:
        raw_payload = _load_request_body(request)
    except ValueError as e:
        return _error_response(str(e), err_code.REQUEST_PARAM_INVALID.code)

    serializer = PluginGatewayRunCreateSerializer(data=raw_payload)
    if not serializer.is_valid():
        return _error_response(serializer.errors, err_code.REQUEST_PARAM_INVALID.code)

    try:
        run, _ = PluginGatewayExecutionService.create_run(
            caller_app_code=_caller_app_code(request),
            payload=serializer.validated_data,
        )
    except PluginGatewaySourceConfig.DoesNotExist:
        return _error_response(
            "plugin gateway source({}) does not exist".format(serializer.validated_data["source_key"]),
            err_code.CONTENT_NOT_EXIST.code,
            ERROR_TYPE_SOURCE_UNREACHABLE,
        )
    except PluginGatewayPluginNotFoundError as e:
        return _error_response(str(e), err_code.CONTENT_NOT_EXIST.code, ERROR_TYPE_PLUGIN_REMOVED)
    except PluginGatewayVersionNotFoundError as e:
        return _error_response(str(e), err_code.REQUEST_PARAM_INVALID.code, ERROR_TYPE_PLUGIN_VERSION_UNAVAILABLE)
    except PluginGatewayPluginNotEnabledError as e:
        return _error_response(str(e), err_code.INVALID_OPERATION.code, ERROR_TYPE_PLUGIN_NOT_ENABLED)
    except PluginGatewaySourceUnavailableError as e:
        return _error_response(str(e), err_code.INVALID_OPERATION.code, ERROR_TYPE_SOURCE_UNREACHABLE)
    except PluginGatewayConflictError as e:
        return _error_response(str(e), err_code.INVALID_OPERATION.code)
    except ValueError as e:
        return _error_response(str(e), err_code.REQUEST_PARAM_INVALID.code)
    except PermissionError as e:
        return _error_response(str(e), err_code.REQUEST_FORBIDDEN_INVALID.code)

    return {
        "result": True,
        "data": {"open_plugin_run_id": run.open_plugin_run_id, "status": run.run_status},
        "code": err_code.SUCCESS.code,
    }


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def get_plugin_gateway_run_status(request):
    serializer = PluginGatewayRunStatusQuerySerializer(data=request.GET)
    if not serializer.is_valid():
        return _error_response(serializer.errors, err_code.REQUEST_PARAM_INVALID.code)

    try:
        run = PluginGatewayExecutionService.get_run_status(
            task_tag=serializer.validated_data["task_tag"],
            caller_app_code=_caller_app_code(request),
        )
    except PluginGatewayRun.DoesNotExist:
        return _error_response(
            "plugin gateway run({}) does not exist".format(serializer.validated_data["task_tag"]),
            err_code.CONTENT_NOT_EXIST.code,
        )
    except PermissionError as e:
        return _error_response(str(e), err_code.REQUEST_FORBIDDEN_INVALID.code)

    return {
        "result": True,
        "data": {"status": run.run_status, "outputs": run.outputs, "error_message": run.error_message},
        "code": err_code.SUCCESS.code,
    }


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def get_plugin_gateway_run_detail(request, run_id):
    try:
        run = PluginGatewayExecutionService.get_run_detail(
            open_plugin_run_id=run_id,
            caller_app_code=_caller_app_code(request),
        )
    except PluginGatewayRun.DoesNotExist:
        return _error_response(
            "plugin gateway run({}) does not exist".format(run_id),
            err_code.CONTENT_NOT_EXIST.code,
        )
    except PermissionError as e:
        return _error_response(str(e), err_code.REQUEST_FORBIDDEN_INVALID.code)

    return {
        "result": True,
        "data": {
            "open_plugin_run_id": run.open_plugin_run_id,
            "status": run.run_status,
            "plugin_id": run.plugin_id,
            "plugin_version": run.plugin_version,
            "outputs": run.outputs,
            "error_message": run.error_message,
        },
        "code": err_code.SUCCESS.code,
    }


@login_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
def cancel_plugin_gateway_run(request, run_id):
    try:
        run = PluginGatewayExecutionService.cancel_run(
            open_plugin_run_id=run_id,
            caller_app_code=_caller_app_code(request),
        )
    except PluginGatewayRun.DoesNotExist:
        return _error_response(
            "plugin gateway run({}) does not exist".format(run_id),
            err_code.CONTENT_NOT_EXIST.code,
        )
    except PermissionError as e:
        return _error_response(str(e), err_code.REQUEST_FORBIDDEN_INVALID.code)

    logger.info("[plugin_gateway] cancel endpoint succeeded, run_id=%s", run_id)
    return {
        "result": True,
        "data": {"open_plugin_run_id": run.open_plugin_run_id, "status": run.run_status},
        "code": err_code.SUCCESS.code,
    }

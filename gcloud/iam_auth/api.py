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

import ujson as json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService, conf
from gcloud.iam_auth.apply_service import ApplyService, checks_from_permission_payload, checks_from_simple_payload
from gcloud.iam_auth.exceptions import IAMResourceNotFound, IAMV4ProtocolError
from gcloud.iam_auth.scope_resolver import ScopeResolver
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.shortcuts.http import standard_response


def meta_info(request):
    return standard_response(
        result=True, data={"system": conf.SYSTEM_INFO, "resources": conf.RESOURCES, "actions": conf.ACTIONS}
    )


@csrf_exempt
@require_POST
def apply_perms_url(request):
    application = json.loads(request.body)
    tenant_id = request.user.tenant_id
    try:
        checks = checks_from_permission_payload(application, tenant_id)
        url = ApplyService().generate_url(tenant_id, checks)
    except (KeyError, TypeError, ValueError, IAMResourceNotFound, IAMV4ProtocolError) as error:
        return standard_response(False, str(error), {"url": None})
    return standard_response(True, "success", {"url": url})


@csrf_exempt
@require_POST
def is_allow(request):

    data = json.loads(request.body)

    tenant_id = request.user.tenant_id
    try:
        checks = checks_from_simple_payload(data["action"], data.get("resources", []), tenant_id)
        service = PermissionService()
        is_allowed = all(service.is_allowed(request.user.username, tenant_id, check) for check in checks)
    except (KeyError, TypeError, ValueError, IAMResourceNotFound, IAMV4ProtocolError) as error:
        return standard_response(False, str(error))

    return standard_response(True, "success", {"is_allow": is_allowed})


@swagger_auto_schema(methods=["GET"], auto_schema=AnnotationAutoSchema)
@api_view(["GET"])
def is_allow_common_flow_management(request):
    """
    判断当前用户是否有公共流程管理页面权限

    return: dict 根据 result 字段判断是否请求成功
    {
        "result": "是否请求成功(boolean)",
        "data": {
            "is_allow": "当前用户是否有公共流程管理页面权限(boolean)"
        },
        "message": "错误时提示(string)"
    }
    """

    try:
        is_allowed = _has_common_flow_management_permission(request.user.username, request.user.tenant_id)
    except IAMV4ProtocolError as error:
        return standard_response(False, str(error))
    return standard_response(True, "success", {"is_allow": is_allowed})


def _has_common_flow_management_permission(username, tenant_id):
    service = PermissionService()
    if service.is_allowed(
        username,
        tenant_id,
        PermissionCheck(IAMMeta.COMMON_FLOW_CREATE_ACTION),
    ):
        return True
    resolver = ScopeResolver()
    return any(
        resolver.authorized_scope(username, tenant_id, action_id).exists(IAMMeta.COMMON_FLOW_RESOURCE)
        for action_id in (
            IAMMeta.COMMON_FLOW_VIEW_ACTION,
            IAMMeta.COMMON_FLOW_EDIT_ACTION,
            IAMMeta.COMMON_FLOW_DELETE_ACTION,
        )
    )

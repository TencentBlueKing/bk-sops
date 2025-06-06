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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_yasg.utils import swagger_auto_schema
from iam import Action, MultiActionRequest, Request, Resource, Subject
from iam.exceptions import AuthAPIError, AuthInvalidRequest
from rest_framework.decorators import api_view

from gcloud.iam_auth import IAMMeta, conf, get_iam_api_client, get_iam_client
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.shortcuts.http import standard_response

logger = logging.getLogger("root")


def meta_info(request):
    return standard_response(
        result=True, data={"system": conf.SYSTEM_INFO, "resources": conf.RESOURCES, "actions": conf.ACTIONS}
    )


@csrf_exempt
@require_POST
def apply_perms_url(request):
    application = json.loads(request.body)
    username = request.user.username
    tenant_id = request.user.tenant_id
    iam = get_iam_client(tenant_id)

    try:
        result, message, url = iam.get_apply_url(application, bk_username=username)
    except AuthInvalidRequest as e:
        result = False
        message = str(e)
        url = None

    return standard_response(result, message, {"url": url})


@csrf_exempt
@require_POST
def is_allow(request):

    data = json.loads(request.body)

    action_id = data["action"]
    resources = data.get("resources", [])

    subject = Subject("user", request.user.username)
    action = Action(action_id)
    resource = [Resource(r["system"], r["type"], str(r["id"]), r["attributes"]) for r in resources]
    tenant_id = request.user.tenant_id
    iam = get_iam_client(tenant_id)

    try:
        is_allow = iam.is_allowed(Request(conf.SYSTEM_ID, subject, action, resource, None))
    except (AuthInvalidRequest, AuthAPIError) as e:
        return standard_response(False, str(e))

    return standard_response(True, "success", {"is_allow": is_allow})


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

    subject = Subject("user", request.user.username)
    tenant_id = request.user.tenant_id
    iam = get_iam_client(tenant_id)

    # 先检查是否拥有公共流程创建权限
    try:
        is_allow = iam.is_allowed(Request(conf.SYSTEM_ID, subject, Action(IAMMeta.COMMON_FLOW_CREATE_ACTION), [], None))
    except (AuthInvalidRequest, AuthAPIError) as e:
        logger.exception("COMMON_FLOW_CREATE_ACTION is_allow check raise error")
        return standard_response(False, str(e))

    # 拥有公共流程创建权限，不需要再进行后续判断
    if is_allow:
        logger.info("%s has COMMON_FLOW_CREATE_ACTION permission" % request.user.username)
        return standard_response(True, "success", {"is_allow": is_allow})

    iam_api = get_iam_api_client(tenant_id)

    try:
        ok, message, data = iam_api.policy_query_by_actions(
            MultiActionRequest(
                conf.SYSTEM_ID, subject, [Action("common_flow_edit"), Action("common_flow_delete")], [], None
            ).to_dict()
        )
    except (AuthInvalidRequest, AuthAPIError) as e:
        logger.exception("policy query raise error")
        return standard_response(False, str(e))

    if not ok:
        return standard_response(False, "iam policy query failed: %s" % message)

    is_allow = False
    logger.info("common flow edit and delete policy for %s is : %s" % (request.user.username, data))

    # 任意一个操作有策略则放行
    for action_policy in data:
        if action_policy.get("condition", {}):
            is_allow = True
            break

    return standard_response(True, "success", {"is_allow": is_allow})

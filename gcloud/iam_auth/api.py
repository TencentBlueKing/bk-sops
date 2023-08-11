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
import logging

from drf_yasg.utils import swagger_auto_schema

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework.decorators import api_view

from iam import Subject, Action, Resource, Request, MultiActionRequest
from iam.exceptions import AuthInvalidRequest, AuthAPIError

from gcloud.iam_auth import conf
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client, get_iam_api_client
from gcloud.iam_auth.res_factory import (
    resources_for_flow,
    resources_for_task,
    resources_for_common_flow,
    resources_list_for_mini_app,
)
from gcloud.shortcuts.http import standard_response
from gcloud.openapi.schema import AnnotationAutoSchema

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

    iam = get_iam_client()

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

    iam = get_iam_client()

    try:
        is_allow = iam.is_allowed(Request(conf.SYSTEM_ID, subject, action, resource, None))
    except (AuthInvalidRequest, AuthAPIError) as e:
        return standard_response(False, str(e))

    return standard_response(True, "success", {"is_allow": is_allow})


@csrf_exempt
@require_POST
def is_view_action_allow(request):
    """
    @param request:
    @return:
    """
    action_map = {
        IAMMeta.FLOW_RESOURCE: IAMMeta.FLOW_VIEW_ACTION,
        IAMMeta.TASK_RESOURCE: IAMMeta.TASK_VIEW_ACTION,
        IAMMeta.COMMON_FLOW_RESOURCE: IAMMeta.COMMON_FLOW_VIEW_ACTION,
        IAMMeta.MINI_APP_RESOURCE: IAMMeta.MINI_APP_VIEW_ACTION,
    }

    resource_map = {
        IAMMeta.FLOW_RESOURCE: resources_for_flow,
        IAMMeta.TASK_RESOURCE: resources_for_task,
        IAMMeta.COMMON_FLOW_RESOURCE: resources_for_common_flow,
        IAMMeta.MINI_APP_RESOURCE: resources_list_for_mini_app,
    }

    data = json.loads(request.body)
    resource_id = data["resource_id"]
    resource_type = data["resource_type"]
    subject = Subject("user", request.user.username)

    try:
        action = Action(action_map[resource_type])
        resources = resource_map[resource_type](resource_id)
    except Exception as e:
        return standard_response(False, str(e))

    iam = get_iam_client()

    allow_or_raise_auth_failed(
        iam=iam,
        system=IAMMeta.SYSTEM_ID,
        subject=subject,
        action=action,
        resources=resources,
    )

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

    iam = get_iam_client()

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

    iam_api = get_iam_api_client()

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

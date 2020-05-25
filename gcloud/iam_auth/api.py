# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import ujson as json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from iam import Subject, Action, Resource, Request
from iam.exceptions import AuthInvalidRequest, AuthAPIError

from gcloud.iam_auth import conf
from gcloud.iam_auth.shortcuts import get_iam_client
from gcloud.shortcuts.http import standard_response


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
        result, message, url = iam.get_apply_url("", username, application)
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

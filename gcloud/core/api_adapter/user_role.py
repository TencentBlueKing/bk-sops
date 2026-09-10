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

from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.models import Action, Request, Subject
from gcloud.iam_auth.scope_resolver import ScopeResolver

logger = logging.getLogger("root")
CACHE_PREFIX = __name__.replace(".", "_")


def is_user_functor(request):
    """
    判断是否是职能化人员
    """
    username = request.user.username
    if not username:
        return False
    try:
        return bool(
            ScopeResolver()
            .authorized_scope(username, request.user.tenant_id, IAMMeta.FUNCTION_TASK_VIEW_ACTION)
            .ids(IAMMeta.PROJECT_RESOURCE)
        )
    except Exception:
        logger.exception("function task authorized scope request failed")
        return False


def is_user_auditor(request):
    """
    判断是否是审计人员
    """
    username = request.user.username
    if not username:
        return False
    return is_user_role(username, IAMMeta.AUDIT_VIEW_ACTION, request.user.tenant_id)


def is_user_role(username, role_action, tenant_id):

    subject = Subject("user", username)
    action = Action(role_action)
    request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
    iam = get_iam_client(tenant_id=tenant_id)
    # can not raise exception at here, will cause index access error
    try:
        return iam.is_allowed(request)
    except Exception:
        logger.exception(
            "user {username} role action({role_action}) allow request failed.".format(
                username=username, role_action=role_action
            )
        )

    return False

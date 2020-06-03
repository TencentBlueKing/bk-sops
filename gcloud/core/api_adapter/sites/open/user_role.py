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

import logging

from iam import Subject, Action, Request

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client

logger = logging.getLogger("root")
iam = get_iam_client()
CACHE_PREFIX = __name__.replace(".", "_")


def is_user_functor(request):
    """
    判断是否是职能化人员
    """
    return is_user_role(request.user.username, IAMMeta.FUNCTION_VIEW_ACTION)


def is_user_auditor(request):
    """
    判断是否是审计人员
    """
    return is_user_role(request.user.username, IAMMeta.AUDIT_VIEW_ACTION)


def is_user_role(username, role_action):

    subject = Subject("user", username)
    action = Action(role_action)
    request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})

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

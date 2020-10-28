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
import traceback

import ujson as json
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE

from gcloud.iam_auth import get_iam_client

logger = logging.getLogger("root")
iam = get_iam_client()


def handle_api_error(system, api_name, params, result):

    if result.get("code") == HTTP_AUTH_FORBIDDEN_CODE:
        permission = result.get("permission", {})

        if not permission:
            message = _(
                "调用{system}接口{api_name}无权限，返回数据中 permission 为空，请联系第三方平台开发者\ndetails: {result}".format(
                    system=system, api_name=api_name, result=result
                )
            )

        else:
            try:
                apply_result, apply_message, url = iam.get_apply_url(
                    permission, bk_username=settings.SYSTEM_USE_API_ACCOUNT
                )
            except Exception:
                apply_result = False
                apply_message = traceback.format_exc()
                url = None

            if apply_result:
                message = _("调用{system}接口{api_name}无权限：<a href='{url}' target='_blank'>申请权限</a>。").format(
                    system=system, api_name=api_name, url=url
                )
                message = "{prefix}\n details: params={params}, error={error}".format(
                    prefix=message, params=json.dumps(params), error=result.get("message", "")
                )
            else:
                message = _(
                    "调用{system}接口{api_name}无权限，获取申请权限接口失败\ndetails: {result}\n error={error}".format(
                        system=system, api_name=api_name, result=result, error=apply_message
                    )
                )

    else:
        message = _("调用{system}接口{api_name}返回失败, params={params}, error={error}").format(
            system=system, api_name=api_name, params=json.dumps(params), error=result.get("message", "")
        )

    logger.error(message)

    return message


def handle_plain_log(plain_log):
    if plain_log:
        for key_word in settings.LOG_SHIELDING_KEYWORDS:
            plain_log = plain_log.replace(key_word, "******")
    return plain_log

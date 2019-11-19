# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import logging

from django.utils.translation import ugettext_lazy as _

from auth_backend.constants import AUTH_FORBIDDEN_CODE

from gcloud.core.utils import apply_permission_url

logger = logging.getLogger('root')


def handle_api_error(system, api_name, params, result):
    if result.get('code') == AUTH_FORBIDDEN_CODE:
        permission = result.get('permission', [])
        apply_result = apply_permission_url(permission)
        if not apply_result['result']:
            logger.error("获取申请权限链接失败: {msg}".format(msg=apply_result['message']))

        url = apply_result.get('data', {}).get('url', '')

        pre_message = _("调用{system}接口{api_name}无权限: <a href='{url}' target='_blank'>申请权限</a>。").format(
            system=system,
            api_name=api_name,
            url=url,
        )
        message = "{pre_message}\n details: params={params}, error={error}".format(
            pre_message=pre_message,
            params=json.dumps(params),
            error=result.get('message', '')
        )

    else:
        message = _("调用{system}接口{api_name}返回失败, params={params}, error={error}").format(
            system=system,
            api_name=api_name,
            params=json.dumps(params),
            error=result.get('message', '')
        )

    logger.error(message)

    return message

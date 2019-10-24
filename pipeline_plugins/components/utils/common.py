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
import re
import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from auth_backend.constants import AUTH_FORBIDDEN_CODE

from gcloud.core.models import Business, Project
from gcloud.core.utils import apply_permission_url

logger = logging.getLogger('root')

ip_re = r'(([12][0-9][0-9]|[1-9][0-9]|[0-9])\.){3,3}' \
        r'([12][0-9][0-9]|[1-9][0-9]|[0-9])'
ip_pattern = re.compile(ip_re)


def supplier_account_for_project(project_id):
    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return 0

    if not proj.from_cmdb:
        return 0

    return supplier_account_for_business(proj.bk_biz_id)


def supplier_account_for_business(biz_cc_id):
    try:
        supplier_account = Business.objects.supplier_account_for_business(biz_cc_id)
    except Business.DoesNotExist:
        supplier_account = 0

    return supplier_account


def supplier_account_inject(func):
    def wrapper(*args, **kwargs):
        if 'project_id' in kwargs:
            kwargs['supplier_account'] = supplier_account_for_project(kwargs['project_id'])
        elif 'biz_cc_id' in kwargs:
            kwargs['supplier_account'] = supplier_account_for_business(kwargs['biz_cc_id'])

        return func(*args, **kwargs)

    return wrapper


def supplier_id_inject(func):
    def wrapper(*args, **kwargs):
        if 'project_id' in kwargs:
            kwargs['supplier_id'] = supplier_account_for_project(kwargs['project_id'])
        elif 'biz_cc_id' in kwargs:
            kwargs['supplier_id'] = supplier_account_for_business(kwargs['biz_cc_id'])

        return func(*args, **kwargs)

    return wrapper


def handle_api_error(system, api_name, params, result):
    if result.get('code') == AUTH_FORBIDDEN_CODE:
        permission = result.get('permission', [])
        apply_result = apply_permission_url(permission)
        if not apply_result['result']:
            logger.error(u"获取申请权限链接失败: {msg}".format(msg=apply_result['message']))

        url = apply_result.get('data', {}).get('url', '')

        pre_message = _(u"调用{system}接口{api_name}无权限: <a href='{url}' target='_blank'>申请权限</a>。").format(
            system=system,
            api_name=api_name,
            url=url,
        )
        message = u"{pre_message}\n details: params={params}, error={error}".format(
            pre_message=pre_message,
            params=json.dumps(params),
            error=result.get('message', '')
        )

    else:
        message = _(u"调用{system}接口{api_name}返回失败, params={params}, error={error}").format(
            system=system,
            api_name=api_name,
            params=json.dumps(params),
            error=result.get('message', '')
        )

    logger.error(message)

    return message


def get_ip_by_regex(ip_str):
    ip_str = "%s" % ip_str
    ret = []
    for match in ip_pattern.finditer(ip_str):
        ret.append(match.group())
    return ret


def get_s3_file_path_of_time(biz_cc_id, time_str):
    """
    @summary: 根据业务、时间戳生成实际 S3 中的文件路径
    @param biz_cc_id：
    @param time_str：上传时间
    @return:
    """
    return os.path.join(settings.APP_CODE,
                        settings.RUN_MODE,
                        'bkupload',
                        str(biz_cc_id),
                        time_str)


def format_sundry_ip(ip):
    """
    @summary: IP 格式化，如果是多 IP 的主机，只取第一个 IP 作为代表
    @param ip:
    @return:
    """
    if ',' in ip:
        logger.info('HOST[%s] has multiple ip' % ip)
        return ip.split(',')[0]
    return ip

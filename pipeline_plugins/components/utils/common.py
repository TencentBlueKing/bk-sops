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
import re
import os

import ujson as json
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import Business

logger = logging.getLogger('root')

ip_re = r'(([12][0-9][0-9]|[1-9][0-9]|[0-9])\.){3,3}' \
        r'([12][0-9][0-9]|[1-9][0-9]|[0-9])'
ip_pattern = re.compile(ip_re)


def supplier_account_inject(func):
    def wrapper(*args, **kwargs):
        if 'biz_cc_id' in kwargs:
            try:
                kwargs['supplier_account'] = Business.objects.supplier_account_for_business(kwargs['biz_cc_id'])
            except Business.DoesNotExist:
                kwargs['supplier_account'] = 0
        return func(*args, **kwargs)

    return wrapper


def supplier_id_inject(func):
    def wrapper(*args, **kwargs):
        if 'biz_cc_id' in kwargs:
            try:
                kwargs['supplier_id'] = Business.objects.supplier_id_for_business(kwargs['biz_cc_id'])
            except Business.DoesNotExist:
                kwargs['supplier_id'] = 0
        return func(*args, **kwargs)

    return wrapper


def handle_api_error(system, api_name, params, error):
    message = _(u"调用{system}接口{api_name}返回失败, params={params}, error={error}").format(
        system=system,
        api_name=api_name,
        params=json.dumps(params),
        error=error
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

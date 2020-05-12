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

from gcloud.core.models import Business, Project

logger = logging.getLogger('root')

ip_re = r'((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)'
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


def supplier_id_for_project(project_id):
    try:
        proj = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return 0

    if not proj.from_cmdb:
        return 0

    return supplier_id_for_business(proj.bk_biz_id)


def supplier_id_for_business(biz_cc_id):
    try:
        supplier_id = Business.objects.supplier_id_for_business(biz_cc_id)
    except Business.DoesNotExist:
        supplier_id = 0

    return supplier_id


def supplier_account_inject(func):
    def wrapper(*args, **kwargs):
        if 'project_id' in kwargs:
            kwargs['supplier_account'] = supplier_account_for_project(kwargs['project_id'])
        elif 'biz_cc_id' in kwargs:
            kwargs['supplier_account'] = supplier_account_for_business(kwargs['biz_cc_id'])
        elif 'bk_biz_id' in kwargs:
            kwargs['supplier_account'] = supplier_account_for_business(kwargs['bk_biz_id'])

        return func(*args, **kwargs)

    return wrapper


def supplier_id_inject(func):
    def wrapper(*args, **kwargs):
        if 'project_id' in kwargs:
            kwargs['supplier_id'] = supplier_id_for_project(kwargs['project_id'])
        elif 'biz_cc_id' in kwargs:
            kwargs['supplier_id'] = supplier_id_for_business(kwargs['biz_cc_id'])
        elif 'bk_biz_id' in kwargs:
            kwargs['supplier_id'] = supplier_id_for_business(kwargs['bk_biz_id'])

        return func(*args, **kwargs)

    return wrapper

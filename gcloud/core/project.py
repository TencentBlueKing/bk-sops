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

import logging

from gcloud.conf import settings
from gcloud.core.utils import get_all_business_list
from gcloud.core.models import Business, Project, UserDefaultProject

logger = logging.getLogger("root")

CACHE_PREFIX = __name__.replace('.', '_')
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def sync_projects_from_cmdb(use_cache=True):
    biz_list = get_all_business_list(use_cache=use_cache)
    business_dict = {}

    for biz in biz_list:
        if biz['bk_biz_name'] == u"资源池":
            continue
        defaults = {
            'cc_name': biz['bk_biz_name'],
            'cc_owner': biz['bk_supplier_account'],
            'cc_company': biz.get('bk_supplier_id') or 0,
            'time_zone': biz.get('time_zone', ''),
            'life_cycle': biz.get('life_cycle', ''),
            'status': biz.get('bk_data_status', 'enable')
        }

        # update or create business obj
        Business.objects.update_or_create(
            cc_id=biz['bk_biz_id'],
            defaults=defaults
        )

        business_dict[biz['bk_biz_id']] = {
            'cc_name': defaults['cc_name'],
            'time_zone': defaults['time_zone'],
            'creator': settings.SYSTEM_USE_API_ACCOUNT
        }

    # sync projects from business
    Project.objects.sync_project_from_cmdb_business(business_dict)


def get_default_project_for_user(username):
    # TODO change this implementation after introduce auth backend, and add cache
    project = None

    try:
        project = UserDefaultProject.objects.get(username=username).default_project
    except UserDefaultProject.DoesNotExist:
        all_projects = Project.objects.all()
        if all_projects:
            project = all_projects[0]

    return project

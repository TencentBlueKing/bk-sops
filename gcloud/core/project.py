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

from django.core.cache import cache

from auth_backend.plugins.utils import search_all_resources_authorized_actions

from gcloud.conf import settings
from gcloud.core import roles
from gcloud.core.utils import get_user_business_list
from gcloud.core.models import Business, Project, UserDefaultProject
from gcloud.core.permissions import project_resource

logger = logging.getLogger("root")

CACHE_PREFIX = __name__.replace('.', '_')
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC


def prepare_projects(request, use_cache=True):
    user = request.user
    cache_key = "%s_prepare_projects_%s" % (CACHE_PREFIX, user.username)
    is_cache_valid = cache.get(cache_key)
    maintainer_key = roles.CC_V2_ROLE_MAP[roles.MAINTAINERS]

    if not (use_cache and is_cache_valid):
        biz_list = get_user_business_list(request, use_cache)
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

            if defaults['status'] == 'disabled':
                try:
                    Business.objects.get(cc_id=biz['bk_biz_id'])
                except Business.DoesNotExist:
                    continue

            # create business obj
            Business.objects.update_or_create(
                cc_id=biz['bk_biz_id'],
                defaults=defaults
            )

            # set first business maintainer
            business_dict[biz['bk_biz_id']] = {
                'cc_name': defaults['cc_name'],
                'time_zone': defaults['time_zone'],
                'creator': biz[maintainer_key].split(',')[0]
            }

        # sync projects from business
        projects = Project.objects.sync_project_from_cmdb_business(business_dict)

        # set user default project when user first login
        if projects:
            UserDefaultProject.objects.init_user_default_project(username=user.username, project=projects[0])

        cache.set(cache_key, True, DEFAULT_CACHE_TIME_FOR_CC)


def get_default_project_for_user(username):
    project = None
    try:
        project = UserDefaultProject.objects.get(username=username).default_project
    except UserDefaultProject.DoesNotExist:
        resources_perms = search_all_resources_authorized_actions(username, project_resource.rtype, project_resource,
                                                                  [project_resource.actions.view.id])
        if resources_perms:
            project = Project.objects.filter(id__in=resources_perms.items()).first()
    return project

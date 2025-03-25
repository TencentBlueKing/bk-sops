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

from django.db import IntegrityError

from gcloud.conf import settings
from gcloud.core.models import Business, EnvironmentVariables, Project, UserDefaultProject
from gcloud.core.utils import get_user_business_list
from gcloud.iam_auth.utils import get_user_projects

logger = logging.getLogger("root")

CACHE_PREFIX = __name__.replace(".", "_")
DEFAULT_CACHE_TIME_FOR_CC = settings.DEFAULT_CACHE_TIME_FOR_CC
BUSINESS_LOCATION_V1 = "v1.0"
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def sync_projects_from_cmdb(username, tenant_id, use_cache=True):
    biz_list = get_user_business_list(username=username, tenant_id=tenant_id, use_cache=use_cache)
    business_dict = {}
    all_biz_cc_ids = set()
    archived_biz_cc_ids = set()
    active_biz_cc_ids = set()

    for biz in biz_list:
        if biz["bk_biz_name"] == "资源池":
            continue

        biz_cc_id = biz["bk_biz_id"]
        biz_status = biz.get("bk_data_status", "enable")

        all_biz_cc_ids.add(biz_cc_id)

        if biz_status == "disabled":
            archived_biz_cc_ids.add(biz_cc_id)

            # do not create model for archived business
            try:
                Business.objects.get(cc_id=biz_cc_id)
            except Business.DoesNotExist:
                continue
        else:
            active_biz_cc_ids.add(biz_cc_id)

        defaults = {
            "cc_name": biz["bk_biz_name"],
            "cc_owner": EnvironmentVariables.objects.get_var("BKAPP_DEFAULT_SUPPLIER_ACCOUNT", 0),
            "cc_company": biz.get("bk_supplier_id") or 0,
            "time_zone": biz.get("time_zone", ""),
            "life_cycle": biz.get("life_cycle") or "",
            "status": biz_status,
            "tenant_id": tenant_id,
        }

        # update or create business obj
        Business.objects.update_or_create(cc_id=biz_cc_id, defaults=defaults)

        business_dict[biz_cc_id] = {
            "cc_name": defaults["cc_name"],
            "time_zone": defaults["time_zone"],
            "creator": username,
            "tenant_id": tenant_id,
        }

    # sync projects from business
    try:
        Project.objects.sync_project_from_cmdb_business(business_dict)
    except IntegrityError as e:
        logger.warning("[sync_project_from_cmdb_business] create projects failed due to: {}".format(e))

    # 计算出 CC 已删除并且存在于项目中的业务 ID 集合，对这部分项目也需要进行归档
    exist_sync_biz_cc_ids = set(Project.objects.filter(from_cmdb=True).values_list("bk_biz_id", flat=True))
    deleted_biz_cc_ids = exist_sync_biz_cc_ids - all_biz_cc_ids

    # update project's status which sync from cmdb
    Project.objects.update_business_project_status(
        archived_cc_ids=archived_biz_cc_ids | deleted_biz_cc_ids, active_cc_ids=active_biz_cc_ids
    )


def get_default_project_for_user(username, tenant_id):
    project = None

    if not username:
        return project

    try:
        project = UserDefaultProject.objects.get(username=username).default_project
    except UserDefaultProject.DoesNotExist:
        projects = get_user_projects(username, tenant_id)
        if projects:
            project = projects.first()

    return project

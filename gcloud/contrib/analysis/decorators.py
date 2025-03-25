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

import functools

import ujson as json
from django.http import JsonResponse

from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.iam_auth import IAMMeta
from gcloud.utils.strings import check_and_rename_params


def standardize_params(func):
    @functools.wraps(func)
    def wrapper(request):
        bk_audit_add_event(username=request.user.username, action_id=IAMMeta.STATISTICS_VIEW_ACTION)
        params = json.loads(request.body)
        conditions = params.get("conditions", {})
        page_index = int(params.get("pageIndex", 1))
        limit = int(params.get("limit", 10))
        group_by = params.get("group_by", None)
        # 参数校验
        result_dict = check_and_rename_params(conditions, group_by)
        if not result_dict["success"]:
            return JsonResponse({"result": False, "message": result_dict["content"]})
        conditions = result_dict["conditions"]
        group_by = result_dict["group_by"]
        # 过滤参数填写
        filters = {"is_deleted": False, "project__tenant_id": request.user.tenant_id}
        filters.update(conditions)
        # 根据不同的view_funciton进行不同的处理
        inner_args = (group_by, filters, page_index, limit)
        success, content = func(*inner_args)
        # 统一处理返回逻辑
        if not success:
            return JsonResponse({"result": False, "message": content})
        return JsonResponse({"result": True, "data": content})

    return wrapper

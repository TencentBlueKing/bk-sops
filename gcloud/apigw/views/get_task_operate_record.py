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
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.contrib.operate_record.apis.drf.serilaziers.operate_record import TaskOperateRecordSetSerializer
from gcloud.contrib.operate_record.models import TaskOperateRecord
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TaskViewInterceptor())
def get_task_operate_record(request, task_id, project_id):
    filters = {"project_id": project_id, "instance_id": task_id}
    node_id = request.GET.get("node_id")
    if node_id:
        filters.update({"node_id": node_id})

    queryset = TaskOperateRecord.objects.filter(**filters)
    record_data = TaskOperateRecordSetSerializer(queryset, many=True)
    return {"result": True, "data": record_data.data, "code": err_code.SUCCESS.code}

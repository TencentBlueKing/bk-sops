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

from django.views.decorators.http import require_GET
from django.http.response import JsonResponse

from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.admin import AdminEditViewInterceptor


@require_GET
@iam_intercept(AdminEditViewInterceptor())
def fix_engine_version_zero_task(request):
    rows = TaskFlowInstance.objects.filter(engine_ver=0).update(engine_ver=1)
    return JsonResponse({"result": True, "message": "fix {} tasks".format(rows)})

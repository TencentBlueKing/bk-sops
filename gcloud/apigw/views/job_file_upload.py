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
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gcloud import err_code
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ
from gcloud.apigw.decorators import (
    check_job_file_upload_white_apps,
    mark_request_whether_is_trust,
    return_json_response,
)
from gcloud.apigw.utils import get_project_with
from gcloud.core.models import Project
from pipeline_plugins.components.query.sites.open.file_upload import file_upload


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@check_job_file_upload_white_apps
def job_file_upload(request, project_id, **kwargs):
    """
    @summary: 作业平台(JOB)-分发本地文件插件 上传文件
    @return:
    """
    obj_scope = request.META.get("HTTP_APP_PROJECT_SCOPE", PROJECT_SCOPE_CMDB_BIZ)

    try:
        project = get_project_with(obj_id=project_id, scope=obj_scope)
    except Project.DoesNotExist:
        return JsonResponse(
            {
                "result": False,
                "message": "project({id}) with scope({scope}) does not exist.".format(id=project_id, scope=obj_scope),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
        )

    request.META["HTTP_APP_PROJECTID"] = project.id

    # 文件大小不能大于 20M
    if request.FILES["file"].size > settings.JOB_UPLOAD_FILE_SIZE_LIMIT:
        return JsonResponse(
            {
                "result": False,
                "message": (
                    "File upload failed: The file size cannot exceed"
                    f"{settings.JOB_UPLOAD_FILE_SIZE_LIMIT / 1024 / 1024}M."
                ),
                "code": err_code.VALIDATION_ERROR.code,
            }
        )

    return file_upload(request)

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

from blueapps.account.decorators import login_exempt

from gcloud.apigw.decorators import (
    mark_request_whether_is_trust,
    return_json_response,
    check_job_file_upload_white_apps,
)
from apigw_manager.apigw.decorators import apigw_require
from pipeline_plugins.components.query.sites.open.file_upload import apply_upload_ticket


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@check_job_file_upload_white_apps
def apply_job_file_upload_ticket(request):
    """
    @summary: 作业平台(JOB)-分发本地文件插件 申请上传凭证
    @return:
    """

    return apply_upload_ticket(request)

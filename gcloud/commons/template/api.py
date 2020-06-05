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

import base64
import hashlib
import logging
import traceback

import ujson as json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from gcloud import err_code
from gcloud.conf import settings
from gcloud.exceptions import FlowExportError
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.utils import read_template_data_file
from gcloud.utils.dates import time_now_str
from gcloud.utils.strings import string_to_boolean
from gcloud.utils.decorators import request_validate
from gcloud.commons.template.validators import (
    FormValidator,
    ExportTemplateValidator,
    ImportValidator,
    CheckBeforeImportValidator,
)
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.common_template import FormInterceptor, ExportInterceptor, ImportInterceptor


logger = logging.getLogger("root")


@require_GET
@request_validate(FormValidator)
@iam_intercept(FormInterceptor())
def form(request):
    template_id = request.GET["template_id"]
    version = request.GET.get("version")

    template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)

    ctx = {
        "form": template.get_form(version),
        "outputs": template.get_outputs(version),
        "version": version or template.version,
    }

    return JsonResponse({"result": True, "data": ctx, "message": "", "code": err_code.SUCCESS.code})


@require_POST
@request_validate(ExportTemplateValidator)
@iam_intercept(ExportInterceptor())
def export_templates(request):
    data = json.loads(request.body)
    template_id_list = data["template_id_list"]

    # wash
    try:
        templates_data = json.loads(
            json.dumps(CommonTemplate.objects.export_templates(template_id_list), sort_keys=True)
        )
    except FlowExportError as e:
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOW_ERROR.code, "data": None})

    data_string = (json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).encode("utf-8")
    digest = hashlib.md5(data_string).hexdigest()

    file_data = base64.b64encode(
        json.dumps({"template_data": templates_data, "digest": digest}, sort_keys=True).encode("utf-8")
    )
    filename = "bk_sops_%s_%s.dat" % ("common", time_now_str())
    response = HttpResponse()
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    response["mimetype"] = "application/octet-stream"
    response["Content-Type"] = "application/octet-stream"
    response.write(file_data)
    return response


@require_POST
@request_validate(ImportValidator)
@iam_intercept(ImportInterceptor())
def import_templates(request):
    f = request.FILES["data_file"]
    override = string_to_boolean(request.POST["override"])

    r = read_template_data_file(f)
    templates_data = r["data"]["template_data"]

    try:
        result = CommonTemplate.objects.import_templates(templates_data, override, request.user.username)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        return JsonResponse(
            {
                "result": False,
                "message": "invalid flow data or error occur, please contact administrator",
                "code": err_code.UNKNOW_ERROR.code,
                "data": None,
            }
        )

    return JsonResponse(result)


@require_POST
@request_validate(CheckBeforeImportValidator)
def check_before_import(request):
    r = read_template_data_file(request.FILES["data_file"])

    check_info = CommonTemplate.objects.import_operation_check(r["data"]["template_data"])

    return JsonResponse({"result": True, "data": check_info, "code": err_code.SUCCESS.code, "message": ""})

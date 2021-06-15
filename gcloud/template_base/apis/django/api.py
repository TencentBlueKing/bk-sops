# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

import ujson as json
import hashlib
import base64
import traceback

from django.db.models import Model
from django.http import HttpRequest
from django.http import JsonResponse, HttpResponse
from rest_framework.request import Request

from gcloud import err_code
from gcloud.conf import settings
from gcloud.utils.dates import time_now_str
from gcloud.utils.strings import string_to_boolean
from gcloud.exceptions import FlowExportError
from gcloud.template_base.utils import read_template_data_file

logger = logging.getLogger("root")


def base_batch_form(request: Request, template_model_cls: Model, filters: dict):
    """批量获取表单数据统一接口"""
    templates_data = request.data.get("templates")
    template_ids = [int(template["id"]) for template in templates_data]
    versions = {int(template["id"]): template["version"] for template in templates_data}

    filters["id__in"] = template_ids
    filters["is_deleted"] = False
    templates = template_model_cls.objects.filter(**filters)

    data = {
        template.id: [
            {
                "form": template.get_form(),
                "outputs": template.get_outputs(),
                "version": template.version,
                "is_current": True,
            }
        ]
        for template in templates
    }
    for template in templates:
        version = versions[template.id]
        data[template.id].append(
            {
                "form": template.get_form(version),
                "outputs": template.get_outputs(version),
                "version": version,
                "is_current": False,
            }
        )

    return JsonResponse({"result": True, "data": data, "message": "", "code": err_code.SUCCESS.code})


def base_form(request: HttpRequest, template_model_cls: object, filters: dict):
    template_id = request.GET["template_id"]
    version = request.GET.get("version")

    filters["pk"] = template_id
    filters["is_deleted"] = False

    template = template_model_cls.objects.get(**filters)

    ctx = {
        "form": template.get_form(version),
        "outputs": template.get_outputs(version),
        "version": version or template.version,
    }

    return JsonResponse({"result": True, "data": ctx, "message": "", "code": err_code.SUCCESS.code})


def base_check_before_import(request: HttpRequest, template_model_cls: object, import_args: list):
    r = read_template_data_file(request.FILES["data_file"])

    check_info = template_model_cls.objects.import_operation_check(r["data"]["template_data"], *import_args)

    return JsonResponse({"result": True, "data": check_info, "code": err_code.SUCCESS.code, "message": ""})


def base_export_templates(request: HttpRequest, template_model_cls: object, file_prefix: str, export_args: list):
    data = request.data
    template_id_list = data["template_id_list"]

    # wash
    try:
        templates_data = json.loads(
            json.dumps(template_model_cls.objects.export_templates(template_id_list, *export_args), sort_keys=True)
        )
    except FlowExportError as e:
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code, "data": None})

    data_string = (json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).encode("utf-8")
    digest = hashlib.md5(data_string).hexdigest()

    file_data = base64.b64encode(
        json.dumps({"template_data": templates_data, "digest": digest}, sort_keys=True).encode("utf-8")
    )
    filename = "bk_sops_%s_%s.dat" % (file_prefix, time_now_str())
    response = HttpResponse()
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    response["mimetype"] = "application/octet-stream"
    response["Content-Type"] = "application/octet-stream"
    response.write(file_data)
    return response


def base_import_templates(request: HttpRequest, template_model_cls: object, import_kwargs: dict):
    f = request.FILES["data_file"]
    override = string_to_boolean(request.POST["override"])

    r = read_template_data_file(f)
    templates_data = r["data"]["template_data"]

    try:
        result = template_model_cls.objects.import_templates(
            template_data=templates_data, override=override, operator=request.user.username, **import_kwargs
        )
    except Exception:
        logger.error(traceback.format_exc())
        return JsonResponse(
            {
                "result": False,
                "message": "invalid flow data or error occur, please contact administrator",
                "code": err_code.UNKNOWN_ERROR.code,
                "data": None,
            }
        )

    return JsonResponse(result)

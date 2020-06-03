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

import hashlib
import base64
import logging
import traceback

import ujson as json
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST

from pipeline_web.drawing_new.constants import CANVAS_WIDTH, POSITION
from pipeline_web.drawing_new.drawing import draw_pipeline as draw_pipeline_tree

from gcloud import err_code
from gcloud.conf import settings
from gcloud.exceptions import FlowExportError
from gcloud.core.models import Project
from gcloud.utils.strings import check_and_rename_params, string_to_boolean
from gcloud.utils.dates import time_now_str
from gcloud.utils.decorators import request_validate
from gcloud.commons.template.utils import read_template_data_file
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.validators import (
    FormValidator,
    ExportValidator,
    ImportValidator,
    CheckBeforeImportValidator,
    GetTemplateCountValidator,
    DrawPipelineValidator,
)
from gcloud.contrib.analysis.analyse_items import task_template
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.template import (
    FormInterceptor,
    ExportInterceptor,
    ImportInterceptor,
)

logger = logging.getLogger("root")


@require_GET
@request_validate(FormValidator)
@iam_intercept(FormInterceptor())
def form(request, project_id):
    template_id = request.GET["template_id"]
    version = request.GET.get("version")

    template = TaskTemplate.objects.get(pk=template_id, project_id=project_id, is_deleted=False)

    ctx = {
        "form": template.get_form(version),
        "outputs": template.get_outputs(version),
        "version": version or template.version,
    }

    return JsonResponse({"result": True, "data": ctx, "message": "", "code": err_code.SUCCESS})


@require_POST
@request_validate(ExportValidator)
@iam_intercept(ExportInterceptor())
def export_templates(request, project_id):
    data = json.loads(request.body)
    template_id_list = data["template_id_list"]

    # wash
    try:
        templates_data = json.loads(
            json.dumps(TaskTemplate.objects.export_templates(template_id_list, project_id), sort_keys=True)
        )
    except FlowExportError as e:
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOW_ERROR, "data": None})

    data_string = (json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).encode("utf-8")
    digest = hashlib.md5(data_string).hexdigest()

    file_data = base64.b64encode(
        json.dumps({"template_data": templates_data, "digest": digest}, sort_keys=True).encode("utf-8")
    )
    filename = "bk_sops_%s_%s.dat" % (project_id, time_now_str())
    response = HttpResponse()
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    response["mimetype"] = "application/octet-stream"
    response["Content-Type"] = "application/octet-stream"
    response.write(file_data)
    return response


@require_POST
@request_validate(ImportValidator)
@iam_intercept(ImportInterceptor())
def import_templates(request, project_id):
    f = request.FILES["data_file"]
    override = string_to_boolean(request.POST["override"])

    r = read_template_data_file(f)
    templates_data = r["data"]["template_data"]

    # reset biz_cc_id select in templates
    project = Project.objects.get(id=project_id)
    _reset_biz_selector_value(templates_data, project.bk_biz_id)

    try:
        result = TaskTemplate.objects.import_templates(templates_data, override, project_id, request.user.username)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        return JsonResponse(
            {
                "result": False,
                "message": "invalid flow data or error occur, please contact administrator",
                "code": err_code.UNKNOW_ERROR,
                "data": None,
            }
        )

    return JsonResponse(result)


def _reset_biz_selector_value(templates_data, bk_biz_id):
    for template in templates_data["pipeline_template_data"]["template"].values():
        for act in [act for act in template["tree"]["activities"].values() if act["type"] == "ServiceActivity"]:
            biz_cc_id_field = act["component"]["data"].get("biz_cc_id")
            if biz_cc_id_field and (not biz_cc_id_field["hook"]):
                biz_cc_id_field["value"] = bk_biz_id

        for constant in template["tree"]["constants"].values():
            if constant["source_tag"].endswith(".biz_cc_id") and constant["value"]:
                constant["value"] = bk_biz_id


@require_POST
@request_validate(CheckBeforeImportValidator)
def check_before_import(request, project_id):
    r = read_template_data_file(request.FILES["data_file"])

    check_info = TaskTemplate.objects.import_operation_check(r["data"]["template_data"], project_id)

    return JsonResponse({"result": True, "data": check_info, "code": err_code.SUCCESS, "message": ""})


def replace_all_templates_tree_node_id(request):
    """
    @summary：清理脏数据
    @param request:
    @return:
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    total, success = TaskTemplate.objects.replace_all_template_tree_node_id()
    return JsonResponse(
        {"result": True, "data": {"total": total, "success": success}, "code": err_code.SUCCESS, "message": ""}
    )


@require_GET
@request_validate(GetTemplateCountValidator)
def get_template_count(request, project_id):
    group_by = request.GET.get("group_by", "category")
    result_dict = check_and_rename_params({}, group_by)

    filters = {"is_deleted": False, "project_id": project_id}
    success, content = task_template.dispatch(result_dict["group_by"], filters)
    if not success:
        return JsonResponse({"result": False, "message": content, "code": err_code.UNKNOW_ERROR, "data": None})
    return JsonResponse({"result": True, "data": content, "code": err_code.SUCCESS, "message": ""})


@require_POST
@request_validate(DrawPipelineValidator)
def draw_pipeline(request):
    """
    @summary：自动排版画布
    @param request:
    @return:
    """
    params = json.loads(request.body)
    pipeline_tree = params["pipeline_tree"]
    canvas_width = int(params.get("canvas_width", CANVAS_WIDTH))

    kwargs = {"canvas_width": canvas_width}

    for kw in list(POSITION.keys()):
        if kw in params:
            kwargs[kw] = params[kw]
    try:
        draw_pipeline_tree(pipeline_tree, **kwargs)
    except Exception as e:
        message = "draw pipeline_tree error: %s" % e
        logger.exception(e)
        return JsonResponse({"result": False, "message": message, "code": err_code.UNKNOW_ERROR, "data": None})

    return JsonResponse(
        {"result": True, "data": {"pipeline_tree": pipeline_tree}, "code": err_code.SUCCESS, "message": ""}
    )


@require_GET
def get_templates_with_expired_subprocess(request, project_id):
    return JsonResponse(
        {
            "result": True,
            "data": TaskTemplate.objects.get_templates_with_expired_subprocess(project_id),
            "code": err_code.SUCCESS,
            "message": "",
        }
    )

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

import hashlib
import base64
import logging
import traceback

import ujson as json
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.tasktmpl3.utils import get_constant_values
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
    AnalysisConstantsRefValidator,
    BatchFormValidator,
)
from gcloud.tasktmpl3.utils import analysis_pipeline_constants_ref
from gcloud.contrib.analysis.analyse_items import task_template
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.template import (
    FormInterceptor,
    ExportInterceptor,
    ImportInterceptor,
    BatchFormInterceptor,
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

    return JsonResponse({"result": True, "data": ctx, "message": "", "code": err_code.SUCCESS.code})


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(BatchFormValidator)
@iam_intercept(BatchFormInterceptor())
def batch_form(request, project_id):
    """
   项目流程批量获取表单数据

    通过输入批量流程id和对应指定版本，获取对应流程指定版本和当前版本的表单、输出等信息。

    body: data
    {
        "templates(required)": [
            {
                "id": "流程ID(integer)",
                "version": "流程版本(string)"
            }
        ]
    }

    return: 每个流程当前版本和指定版本的表单数据列表
    {
        "template_id": [
            {
                "form": "流程表单(dict)",
                "outputs": "流程输出(dict)",
                "version": "版本号(string)",
                "is_current": "是否当前版本(boolean)"
            }
        ]
    }
    """
    templates_data = request.data.get("templates")
    template_ids = [int(template["id"]) for template in templates_data]
    versions = [template["version"] for template in templates_data]

    if len(template_ids) != len(versions):
        return JsonResponse({"result": False, "data": "", "message": "", "code": err_code.REQUEST_PARAM_INVALID.code})

    templates = TaskTemplate.objects.filter(id__in=template_ids, project_id=project_id, is_deleted=False)

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
    for template, version in zip(templates, versions):
        data[template.id].append(
            {
                "form": template.get_form(version),
                "outputs": template.get_outputs(version),
                "version": version,
                "is_current": False,
            }
        )

    return JsonResponse({"result": True, "data": data, "message": "", "code": err_code.SUCCESS.code})


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
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code, "data": None})

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


def _reset_biz_selector_value(templates_data, bk_biz_id):
    for template in templates_data["pipeline_template_data"]["template"].values():
        for act in [act for act in template["tree"]["activities"].values() if act["type"] == "ServiceActivity"]:
            act_info = act["component"]["data"]
            biz_cc_id_field = act_info.get("biz_cc_id") or act_info.get("bk_biz_id")
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

    return JsonResponse({"result": True, "data": check_info, "code": err_code.SUCCESS.code, "message": ""})


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
        {"result": True, "data": {"total": total, "success": success}, "code": err_code.SUCCESS.code, "message": ""}
    )


@require_GET
@request_validate(GetTemplateCountValidator)
def get_template_count(request, project_id):
    group_by = request.GET.get("group_by", "category")
    result_dict = check_and_rename_params({}, group_by)

    filters = {"is_deleted": False, "project_id": project_id}
    success, content = task_template.dispatch(result_dict["group_by"], filters)
    if not success:
        return JsonResponse({"result": False, "message": content, "code": err_code.UNKNOWN_ERROR.code, "data": None})
    return JsonResponse({"result": True, "data": content, "code": err_code.SUCCESS.code, "message": ""})


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
        return JsonResponse({"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code, "data": None})

    return JsonResponse(
        {"result": True, "data": {"pipeline_tree": pipeline_tree}, "code": err_code.SUCCESS.code, "message": ""}
    )


@require_GET
def get_templates_with_expired_subprocess(request, project_id):
    return JsonResponse(
        {
            "result": True,
            "data": TaskTemplate.objects.get_templates_with_expired_subprocess(project_id),
            "code": err_code.SUCCESS.code,
            "message": "",
        }
    )


@require_POST
def get_constant_preview_result(request):
    params = json.loads(request.body)
    constants = params.get("constants", {})
    extra_data = params.get("extra_data", {})

    preview_results = get_constant_values(constants, extra_data)

    return JsonResponse({"result": True, "data": preview_results, "code": err_code.SUCCESS.code, "message": ""})


@require_POST
@request_validate(AnalysisConstantsRefValidator)
def analysis_constants_ref(request):
    """
    @summary：计算模板中的变量引用
    @param request:
    @return:
    """
    tree = json.loads(request.body)
    result = None
    try:
        result = analysis_pipeline_constants_ref(tree)
    except Exception:
        logger.exception("[analysis_constants_ref] error")

    data = {"defined": {}, "nodefined": {}}
    defined_keys = tree.get("constants", {}).keys()
    if result:
        for k, v in result.items():
            if k in defined_keys:
                data["defined"][k] = v
            else:
                data["nodefined"][k] = v

    return JsonResponse({"result": True, "data": data, "code": err_code.SUCCESS.code, "message": ""})

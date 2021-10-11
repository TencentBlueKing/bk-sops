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
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from pipeline_web.drawing_new.constants import CANVAS_WIDTH, POSITION
from pipeline_web.drawing_new.drawing import draw_pipeline as draw_pipeline_tree

from gcloud import err_code
from gcloud.utils.strings import check_and_rename_params
from gcloud.utils.decorators import request_validate
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.domains.constants import analysis_pipeline_constants_ref
from gcloud.contrib.analysis.analyse_items import task_template
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.template import (
    FormInterceptor,
    ExportInterceptor,
    ImportInterceptor,
    BatchFormInterceptor,
    ParentsInterceptor,
)
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.tasktmpl3.domains.constants import get_constant_values
from .validators import (
    ImportValidator,
    GetTemplateCountValidator,
    DrawPipelineValidator,
    AnalysisConstantsRefValidator,
    CheckBeforeImportValidator,
)
from gcloud.template_base.apis.django.api import (
    base_batch_form,
    base_form,
    base_check_before_import,
    base_export_templates,
    base_import_templates,
    base_template_parents,
    is_full_param_process,
)
from gcloud.template_base.apis.django.validators import (
    BatchFormValidator,
    FormValidator,
    ExportTemplateApiViewValidator,
    TemplateParentsValidator,
)

logger = logging.getLogger("root")


@swagger_auto_schema(
    methods=["get"], auto_schema=AnnotationAutoSchema,
)
@api_view(["GET"])
@request_validate(FormValidator)
@iam_intercept(FormInterceptor())
def form(request, project_id):
    """
    项目流程获取表单数据

    通过输入流程id和对应指定版本，获取对应流程指定版本和当前版本的表单、输出等信息。

    param: project_id: 项目ID, integer, path, required
    param: template_id: 流程ID, integer, query, required
    param: version: 流程版本(string), string, query

    return: 每个流程当前版本和指定版本的表单数据列表
    {
        "form": "流程表单(dict)",
        "outputs": "流程输出(dict)",
        "version": "版本号(string)"
    }
    """
    return base_form(request, TaskTemplate, filters={"project_id": project_id})


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
    return base_batch_form(request, TaskTemplate, filters={"project_id": project_id})


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(ExportTemplateApiViewValidator)
@is_full_param_process(TaskTemplate, project_related=True)
@iam_intercept(ExportInterceptor())
def export_templates(request, project_id):
    """
    以 DAT 格式导出项目流程模板

    param: project_id: 项目ID, integer, path, required

    body: data
    {
        "template_id_list(required)": [
            "流程ID(integer)"
        ],
        "is_full(required)": "是否导出全部模板，该参数优先级大于 template_id_list(bool)"
    }

    return: DAT 文件
    {}
    """
    return base_export_templates(request, TaskTemplate, project_id, [project_id])


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(ImportValidator)
@iam_intercept(ImportInterceptor())
def import_templates(request, project_id):
    """
    导入 DAT 文件到项目流程中

    param: project_id: 项目ID, integer, path, required

    body: data
    {
        "data_file(required)": "DAT格式模板数据文件"
    }

    return: 检测结果
    {
        "data(integer)": "成功导入的流程数"
    }
    """
    return base_import_templates(request, TaskTemplate, {"project_id": project_id})


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(CheckBeforeImportValidator)
def check_before_import(request, project_id):
    """
    检测 DAT 文件是否支持导入

    param: project_id: 项目ID, integer, path, required

    body: data
    {
        "data_file(required)": "DAT格式模板数据文件"
    }

    return: 检测结果
    {
        "can_override": "是否能够进行覆盖操作(bool)",
        "new_template": [
            {
                "id": "能够新建的模板ID(integer)",
                "name": "能够新建的模板名(string)"
            }
        ],
        "override_template": [
            {
                "id": "能够覆盖的模板ID(integer)",
                "name": "能够覆盖的模板名(string)",
                "template_id": "模板UUID(string)"
            }
        ]
    }
    """
    return base_check_before_import(request, TaskTemplate, [project_id])


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


@swagger_auto_schema(
    methods=["get"], auto_schema=AnnotationAutoSchema,
)
@api_view(["GET"])
@request_validate(TemplateParentsValidator)
@iam_intercept(ParentsInterceptor())
def parents(request, project_id):
    """
    获取引用了某个项目流程的所有父流程

    param: project_id: 项目ID, integer, path, required
    param: template_id: 流程ID, integer, query, required

    return: 每个流程当前版本和指定版本的表单数据列表
    {
        "template_id": "父流程 ID(string)",
        "template_name": "模板名(string)",
        "subprocess_node_id": "子流程节点 ID(string)",
        "version": "版本号(string)",
        "always_use_latest": "是否总是使用最新版本的子流程(bool)"
    }
    """
    return base_template_parents(request, TaskTemplate, filters={"project_id": project_id})

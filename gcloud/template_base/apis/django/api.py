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

import yaml
from django.http import HttpRequest
from django.http import JsonResponse, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request

from gcloud import err_code
from gcloud.conf import settings
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.base_template import YamlExportInterceptor, YamlImportInterceptor
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.template_base.domains import TEMPLATE_TYPE_MODEL
from gcloud.template_base.apis.django.validators import (
    FileValidator,
    YamlTemplateImportValidator,
    YamlTemplateExportValidator,
)
from gcloud.template_base.domains.converter_handler import YamlSchemaConverterHandler
from gcloud.template_base.domains.importer import TemplateImporter
from gcloud.utils.dates import time_now_str
from gcloud.utils.decorators import request_validate
from gcloud.utils.strings import string_to_boolean
from gcloud.exceptions import FlowExportError
from gcloud.template_base.utils import read_template_data_file

logger = logging.getLogger("root")


def base_batch_form(request: Request, template_model_cls: object, filters: dict):
    """批量获取表单数据统一接口"""
    templates_data = request.data.get("templates")
    template_ids = [int(template["id"]) for template in templates_data]
    versions = [template["version"] for template in templates_data]

    if len(template_ids) != len(versions):
        return JsonResponse({"result": False, "data": "", "message": "", "code": err_code.REQUEST_PARAM_INVALID.code})

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


def base_export_templates(request: Request, template_model_cls: object, file_prefix: str, export_args: list):
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


@swagger_auto_schema(methods=["post"], auto_schema=AnnotationAutoSchema)
@api_view(["POST"])
@request_validate(FileValidator)
def upload_and_check_yaml_templates(request: Request):
    """
    上传Yaml格式模版文件并进行数据检查

    body: data
    {
        "data_file(required)": "Yaml格式模板数据文件(file)"
    }

    return: 上传检查结果
    {
        "yaml_docs": [
            {
                "schema_version":  "schema版本",
                "meta": "传入模版的meta数据(dict)",
                "spec": "传入模版的spec数据(dict)"
            }
        ],
        "relationship": {
            "template_id": ["父流程id"]
        },
        "error": {
            "file(非固定字段)": ["对应YAML文件结构错误信息"],
            "template_id(非固定字段)": ["对应流程配置错误信息"]
        }
    }
    """
    f = request.data.get("data_file")
    yaml_schema_handler = YamlSchemaConverterHandler("v1")
    load_yaml_result = yaml_schema_handler.load_yaml_docs(f)
    if not load_yaml_result["result"]:
        return JsonResponse({**load_yaml_result, "code": err_code.UNKNOWN_ERROR.code})
    yaml_docs = load_yaml_result["data"]
    try:
        validate_result = yaml_schema_handler.converter.validate_data(yaml_docs)
    except Exception as e:
        logger.exception("[upload_and_check_yaml_templates]: {}".format(e))
        return JsonResponse({"result": False, "code": err_code.UNKNOWN_ERROR.code, "data": {}, "message": e})

    relations = {}
    validate_errors = validate_result["message"]
    if "file" not in validate_errors:
        for template_id, template_data in validate_result["data"].items():
            for node in template_data["spec"]["nodes"]:
                if node.get("type") == "SubProcess" and node.get("template_id"):
                    relations.setdefault(node.get("template_id"), []).append(template_id)
    return JsonResponse(
        {
            "result": True,
            "code": err_code.SUCCESS.code,
            "data": {"yaml_docs": yaml_docs, "relations": relations, "error": validate_errors},
            "message": "",
        }
    )


@swagger_auto_schema(methods=["post"], auto_schema=AnnotationAutoSchema)
@api_view(["POST"])
@request_validate(YamlTemplateImportValidator)
@iam_intercept(YamlImportInterceptor())
def import_yaml_templates(request: Request):
    """
    通过Yaml格式数据文件导入流程

    body: data
    {
        "data_file(required)": "Yaml格式模板数据文件(file)",
        "template_type(required)": "导入流程类型：project/common",
        "project_id": "项目ID(当template_type=project时必填)",
        "override_mappings": "文件中流程id和所要替换的流程id的映射关系(dict)",
        "template_kwargs": "流程需要的其他创建参数(dict)"
    }

    return: 导入结果
    {
        "result": "是否导入成功，成功则读取data字段，失败则读取message字段(bool)",
        "data": {
            "template_id": {
                "result": "Yaml文件中对应流程是否导入成功",
                "message": "导入结果信息"
            }
        },
        "message": "导入失败时详情信息，返回dict类型时格式如data字段(str/dict)"
    }
    """
    f = request.data.get("data_file")
    override_mappings = request.data.get("override_mappings") or {}
    template_type = request.data.get("template_type")
    project_id = request.data.get("project_id")
    template_kwargs = request.data.get("template_kwargs") or {}

    if template_type == "project" and project_id:
        template_kwargs.update({"project_id": int(project_id)})

    convertor_handler = YamlSchemaConverterHandler("v1")
    load_yaml_result = convertor_handler.load_yaml_docs(f)
    if not load_yaml_result["result"]:
        return JsonResponse(load_yaml_result)

    yaml_docs = load_yaml_result["data"]
    convert_result = convertor_handler.reconvert(yaml_docs)

    if not convert_result["result"]:
        return JsonResponse({"result": False, "data": None, "message": convert_result["message"]})

    template_order = convert_result["data"]["template_order"]
    templates = convert_result["data"]["templates"]
    import_data = []
    for template_id in template_order:
        import_data.append(
            {
                "name": templates[template_id]["name"],
                "description": templates[template_id]["description"],
                "pipeline_tree": templates[template_id]["tree"],
                "override_template_id": override_mappings.get(template_id),
                "template_kwargs": template_kwargs,
                "id": template_id,
            }
        )

    importer = TemplateImporter(TEMPLATE_TYPE_MODEL[template_type])
    try:
        import_result = importer.import_template(request.user.username, import_data)
    except Exception as e:
        logger.exception("[import_yaml_templates] error: {}".format(e))
        return JsonResponse({"result": False, "data": None, "message": e})

    detail = [{"result": result["result"], "message": result["message"]} for result in import_result["data"]]
    if all([data["result"] for data in detail]):
        result = {"result": True, "data": detail, "message": ""}
    else:
        result = {"result": False, "data": None, "message": detail}
    return JsonResponse(result)


@swagger_auto_schema(methods=["post"], auto_schema=AnnotationAutoSchema)
@api_view(["POST"])
@request_validate(YamlTemplateExportValidator)
@iam_intercept(YamlExportInterceptor())
def export_yaml_templates(request: Request):
    """
    导出Yaml格式的流程文件

    成功为HttpResponse(下载文件)
    失败为JsonResponse（打印message)

    body: data
    {
        "template_id_list(required)": "导出的流程id列表(list)",
        "template_type(required)": "流程类型: project/common",
        "project_id": "当流程类型为project时必填"
    }
    """
    template_ids = request.data["template_id_list"]
    template_type = request.data["template_type"]
    project_id = request.data["project_id"] if template_type == "project" else None
    export_args = [project_id] if project_id else []

    converter_handler = YamlSchemaConverterHandler("v1")
    try:
        templates_data = TEMPLATE_TYPE_MODEL[template_type].objects.export_templates(template_ids, *export_args)
        convert_result = converter_handler.convert(templates_data)
    except FlowExportError as e:
        return JsonResponse({"result": False, "message": str(e), "data": None})

    if convert_result["result"] is False:
        return JsonResponse(convert_result)

    yaml_data = convert_result["data"]
    file_data = yaml.dump_all(yaml_data, allow_unicode=True, sort_keys=False)
    filename = "bk_sops_%s_%s.yaml" % (template_type, time_now_str())
    response = HttpResponse()
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    response["mimetype"] = "application/octet-stream"
    response["Content-Type"] = "application/octet-stream"
    response.write(file_data)
    return response

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

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from gcloud.common_template.models import CommonTemplate
from gcloud.iam_auth.view_interceptors.template import BatchFormInterceptor
from gcloud.openapi.schema import AnnotationAutoSchema
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
    TemplateParentsValidator,
    ExportTemplateApiViewValidator,
)
from gcloud.utils.decorators import request_validate
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.common_template import (
    FormInterceptor,
    ExportInterceptor,
    ImportInterceptor,
    ParentsInterceptor,
)
from .validators import ImportValidator, CheckBeforeImportValidator

logger = logging.getLogger("root")


@swagger_auto_schema(
    methods=["get"], auto_schema=AnnotationAutoSchema,
)
@api_view(["GET"])
@request_validate(FormValidator)
@iam_intercept(FormInterceptor())
def form(request):
    """
    公共流程获取表单数据

    通过输入流程id和对应指定版本，获取对应流程指定版本和当前版本的表单、输出等信息。

    param: template_id: 流程ID, integer, query, required
    param: version: 流程版本, string, query

    return: 每个流程当前版本和指定版本的表单数据列表
    {
        "form": "流程表单(dict)",
        "outputs": "流程输出(dict)",
        "version": "版本号(string)"
    }
    """
    return base_form(request, CommonTemplate, filters={})


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(BatchFormValidator)
@iam_intercept(BatchFormInterceptor())
def batch_form(request):
    """
    公共流程批量获取表单数据

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
    return base_batch_form(request, CommonTemplate, {})


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(ExportTemplateApiViewValidator)
@is_full_param_process(CommonTemplate, project_related=False)
@iam_intercept(ExportInterceptor())
def export_templates(request):
    """
    以 DAT 格式导出公共流程数据

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
    return base_export_templates(request, CommonTemplate, "common", [])


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(ImportValidator)
@iam_intercept(ImportInterceptor())
def import_templates(request):
    """
    导入 DAT 文件到公共流程中

    body: data
    {
        "data_file(required)": "DAT格式模板数据文件"
    }

    return: 检测结果
    {
        "data(integer)": "成功导入的流程数"
    }
    """
    return base_import_templates(request, CommonTemplate, {})


@swagger_auto_schema(
    methods=["post"], auto_schema=AnnotationAutoSchema,
)
@api_view(["POST"])
@request_validate(CheckBeforeImportValidator)
def check_before_import(request):
    """
    检测 DAT 文件是否支持导入

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
    return base_check_before_import(request, CommonTemplate, [])


@swagger_auto_schema(
    methods=["get"], auto_schema=AnnotationAutoSchema,
)
@api_view(["GET"])
@request_validate(TemplateParentsValidator)
@iam_intercept(ParentsInterceptor())
def parents(request):
    """
    获取引用了某个公共流程的所有父流程

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
    return base_template_parents(request, CommonTemplate, filters={})

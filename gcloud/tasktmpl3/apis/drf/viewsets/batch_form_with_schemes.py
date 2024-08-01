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
specific lan
"""

import itertools
import logging

from django.utils.translation import ugettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from pipeline.models import TemplateScheme
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import PROJECT
from gcloud.tasktmpl3.apis.drf.permissions import BatchTemplateFormWithSchemesPermissions
from gcloud.tasktmpl3.apis.drf.serilaziers.batch_form_with_schemes import (
    BatchTemplateFormResponseSerializer,
    BatchTemplateFormWithSchemesSerializer,
)
from gcloud.tasktmpl3.models import TaskTemplate
from pipeline_web.preview import preview_template_tree_with_schemes

logger = logging.getLogger("root")


class BatchTemplateFormWithSchemesView(APIView):
    permission_classes = [permissions.IsAuthenticated, BatchTemplateFormWithSchemesPermissions]

    @swagger_auto_schema(
        method="POST",
        operation_summary="项目流程批量根据执行方案获取表单数据",
        request_body=BatchTemplateFormWithSchemesSerializer,
        responses={200: BatchTemplateFormResponseSerializer},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        serializer = BatchTemplateFormWithSchemesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.data.get("project_id")
        template_list = serializer.data["template_list"]

        # 将项目流程和公共流程分组
        template_data = {}
        project_template_ids = []
        common_template_ids = []
        scheme_id_list = []
        for template in template_list:
            template_id = template["id"]
            template_data[template_id] = template_data.get(template_id, {})
            template_data[template_id][template["version"]] = template
            scheme_id_list.extend(template["scheme_id_list"])
            if template["template_source"] == PROJECT:
                project_template_ids.append(template_id)
            else:
                common_template_ids.append(template_id)

        # 获取公共流程和项目流程的queryset
        template_queryset = []
        common_template_queryset = []
        if project_template_ids:
            template_queryset = TaskTemplate.objects.select_related("pipeline_template").filter(
                id__in=project_template_ids, project_id=project_id, is_deleted=False
            )
        if common_template_ids:
            common_template_queryset = CommonTemplate.objects.select_related("pipeline_template").filter(
                id__in=common_template_ids, is_deleted=False
            )
        queryset = itertools.chain(template_queryset, common_template_queryset)
        template_dict = {}
        pipeline_template_ids = []
        for template in queryset:
            template_dict[template.id] = template
            template_data[template.id][template.version] = {
                "id": template.id,
                "version": template.version,
                "scheme_id_list": scheme_id_list,
            }
            pipeline_template_ids.append(template.pipeline_template.id)

        # 获取各流程对应的执行方案列表
        scheme_queryset = TemplateScheme.objects.filter(template_id__in=pipeline_template_ids).values(
            "template__id", "id", "name", "data"
        )
        scheme_dict = {}
        for scheme in scheme_queryset:
            template_id = scheme.pop("template__id")
            if template_id not in scheme_dict:
                scheme_dict[template_id] = [scheme]
            else:
                scheme_dict[template_id].append(scheme)

        data = {}
        for template_id, template in template_dict.items():
            data[template_id] = []
            # 每个模板要获取当前版本的和最新版本的表单数据
            # 两次获取数据只有模版版本不同，使用for循环减少重复逻辑,使用is_current标识是否是当前版本的表单数据
            for version, temp in template_data[template_id].items():
                is_current = False
                if version == template.version:
                    is_current = True
                scheme_id_list = temp["scheme_id_list"]
                try:
                    preview_data = preview_template_tree_with_schemes(template, version, scheme_id_list)
                except Exception as e:
                    message = _(f"请求参数信息失败: 批量获取带执行方案的流程表单失败, 错误信息: {e}, 请重试. 如持续失败可联系管理员处理 | batch form with schemes")
                    logger.error(message)
                    return Response({"result": False, "message": message, "data": {}})
                data[template_id].append(
                    {
                        "form": {**preview_data["pipeline_tree"]["constants"], **preview_data["custom_constants"]},
                        "outputs": preview_data["outputs"],
                        "constants_not_referred": preview_data["constants_not_referred"],
                        "version": preview_data["version"],
                        "is_current": is_current,
                        "scheme_id_list": scheme_id_list,
                        "template_scheme_list": scheme_dict.get(template.pipeline_template.id, []),
                    }
                )

        return Response({"result": True, "data": data, "message": "success"})

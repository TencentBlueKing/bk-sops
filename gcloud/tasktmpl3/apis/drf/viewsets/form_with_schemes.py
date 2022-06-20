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

import logging
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.response import Response

from gcloud.constants import PROJECT
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.tasktmpl3.apis.drf.serilaziers.form_with_schemes import (
    TemplateFormWithSchemesSerializer,
    TemplateFormResponseSerializer,
)
from gcloud.tasktmpl3.apis.drf.permissions import TemplateFormWithSchemesPermissions

from drf_yasg.utils import swagger_auto_schema

from pipeline_web.preview import preview_template_tree_with_schemes

logger = logging.getLogger("root")


class TemplateFormWithSchemesView(APIView):
    permission_classes = [permissions.IsAuthenticated, TemplateFormWithSchemesPermissions]

    @swagger_auto_schema(
        method="POST",
        operation_summary="流程根据执行方案获取表单数据",
        request_body=TemplateFormWithSchemesSerializer,
        responses={200: TemplateFormResponseSerializer},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):
        serializer = TemplateFormWithSchemesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template_source = serializer.data["template_source"]
        template_id = serializer.data["template_id"]
        project_id = serializer.data.get("project_id")
        scheme_id_list = serializer.data["scheme_id_list"]
        version = serializer.data["version"]

        try:
            if template_source == PROJECT:
                template = TaskTemplate.objects.get(pk=template_id, is_deleted=False, project_id=project_id)
            else:
                template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)
        except TaskTemplate.DoesNotExist:
            err_msg = "[form_with_schemes] project[{}] template[{}] doesn't exist".format(project_id, template_id)
            logger.exception(err_msg)
            return Response({"result": False, "message": err_msg, "data": {}})
        except CommonTemplate.DoesNotExist:
            err_msg = "[form_with_schemes] common template[{}] doesn't exist".format(template_id)
            logger.exception(err_msg)
            return Response({"result": False, "message": err_msg, "data": {}})

        try:
            template_data = preview_template_tree_with_schemes(template, version, scheme_id_list)
        except Exception as e:
            err_msg = "[preview_template_tree_with_schemes]get template form with schemes fail: {}".format(e)
            logger.exception(err_msg)
            return Response({"result": False, "message": err_msg, "data": {}})

        data = {
            "form": {**template_data["pipeline_tree"]["constants"], **template_data["custom_constants"]},
            "outputs": template_data["outputs"],
            "constants_not_referred": template_data["constants_not_referred"],
            "version": template_data["version"],
        }

        return Response({"result": True, "data": data, "message": "success"})

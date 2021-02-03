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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ErrorDetail
from pipeline.models import TemplateScheme

from gcloud import err_code
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.apis.drf.serilaziers.template_scheme import TemplateSchemeSerializer, ParamsSerializer

logger = logging.getLogger("root")


def get_pipeline_template_id(template_id, project_id, *args, **kwargs):
    try:
        template = TaskTemplate.objects.get(pk=template_id, project_id=project_id)
        return template.pipeline_template.id
    except TaskTemplate.DoesNotExist:
        message = "flow template[id={template_id}] in project[id={project_id}] does not exist".format(
            template_id=template_id, project_id=project_id
        )
        logger.error(message)
        raise TaskTemplate.DoesNotExist(ErrorDetail(message, err_code.UNKNOWN_ERROR.code))


class TemplateSchemeViewSet(ApiMixin, viewsets.ModelViewSet):
    queryset = TemplateScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TemplateSchemeSerializer
    params_serializer_class = ParamsSerializer

    def get_serializer_data(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_serializer_params_data(self, request):
        data = self.request.query_params or request.data
        serializer = self.params_serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @action(methods=["post"], detail=False)
    def batch_operate(self, request, *args, **kwargs):
        validated_data = self.get_serializer_params_data(request)
        current_schemes = validated_data.get("schemes", {})
        template_id = validated_data.get("template_id")
        if not template_id or not current_schemes:
            return Response(
                data={"detail": ErrorDetail("template_id or schemes is empty", err_code.REQUEST_PARAM_INVALID.code)},
                exception=True,
            )

        # 筛选待处理方案
        pipeline_template_id = get_pipeline_template_id(**validated_data)
        template_scheme_query = self.queryset.filter(template__id=pipeline_template_id)
        old_schemes_id_set = set(template_scheme_query.values_list("id", flat=True))
        need_create_schemes, scheme_id_list = [], []
        for scheme in current_schemes:
            scheme_id = scheme.get("id")
            scheme_id_list.append(scheme_id)
            if not scheme_id:
                scheme.update(
                    {
                        "unique_id": "{}-{}".format(template_id, scheme["name"]),
                        "template_id": pipeline_template_id,
                    }
                )
                need_create_schemes.append(TemplateScheme(**scheme))

        scheme_id_list_set = set(scheme_id_list)
        need_delete_schemes_id = old_schemes_id_set.difference(scheme_id_list_set)

        # 批量创建scheme
        try:
            TemplateScheme.objects.bulk_create(need_create_schemes)
        except Exception as e:
            message = "create template({}) scheme failed: {}".format(template_id, str(e))
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.UNKNOWN_ERROR.code)}, exception=True)

        # 批量删除scheme
        TemplateScheme.objects.filter(id__in=list(need_delete_schemes_id)).delete()

        # 返回流程所有方案
        serializer = self.get_serializer(template_scheme_query, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        validated_data = self.get_serializer_params_data(request)
        pipeline_template_id = get_pipeline_template_id(**validated_data)
        queryset = self.get_queryset().filter(template__id=pipeline_template_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        validated_data = self.get_serializer_data(request)
        params_validated_data = self.get_serializer_params_data(request)
        pipeline_template_id = get_pipeline_template_id(**params_validated_data)
        validated_data.update(
            {
                "unique_id": "{}-{}".format(params_validated_data["template_id"], validated_data["name"]),
                "template_id": pipeline_template_id,
            }
        )
        scheme_obj = TemplateScheme.objects.create(**validated_data)
        serializer = self.serializer_class(instance=scheme_obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):

        return super(TemplateSchemeViewSet, self).destroy(request, *args, **kwargs)

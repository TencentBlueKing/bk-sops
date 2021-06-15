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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ErrorDetail
from pipeline.models import TemplateScheme
from gcloud import err_code
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.template_base.apis.drf.permission import SchemeEditPermission
from gcloud.template_base.apis.drf.serilaziers.template_scheme import TemplateSchemeSerializer, ParamsSerializer

logger = logging.getLogger("root")


class TemplateSchemeViewSet(ApiMixin, viewsets.ModelViewSet):
    queryset = TemplateScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated, SchemeEditPermission]
    serializer_class = TemplateSchemeSerializer
    params_serializer_class = ParamsSerializer

    @staticmethod
    def get_pipeline_template_id(template_id, *args, **kwargs):
        # 如果是项目流程执行方案
        if "project_id" in kwargs:
            model_cls = TaskTemplate
            _filter = {"pk": template_id, "project_id": kwargs["project_id"]}
        # 如果是公共流程执行方案
        else:
            model_cls = CommonTemplate
            _filter = {"pk": template_id}
        try:
            return model_cls.objects.filter(**_filter).only("pipeline_template__id").first().pipeline_template.id
        except model_cls.DoesNotExist:
            template_type = f'project[{kwargs["project_id"]}]' if "project_id" in kwargs else "common_template"
            message = "flow template[id={template_id}] in {template_type} does not exist".format(
                template_id=template_id, template_type=template_type
            )
            logger.error(message)
            raise model_cls.DoesNotExist(ErrorDetail(message, err_code.UNKNOWN_ERROR.code))

    def get_serializer_data(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def get_serializer_params_data(self, request):
        data = self.request.query_params or request.data
        serializer = self.params_serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @swagger_auto_schema(
        method="post",
        operation_summary="执行方案批量更新",
        request_body=ParamsSerializer,
        responses={200: TemplateSchemeSerializer(many=True)},
    )
    @action(methods=["post"], detail=False)
    def batch_operate(self, request, *args, **kwargs):
        validated_data = self.get_serializer_params_data(request)
        current_schemes = validated_data.get("schemes")
        template_id = validated_data.get("template_id")

        # 筛选待处理方案
        pipeline_template_id = self.get_pipeline_template_id(**validated_data)
        need_create_schemes = []
        for scheme in current_schemes:
            if "id" in scheme:
                scheme.pop("id")
            scheme.update(
                {"unique_id": "{}-{}".format(template_id, scheme["name"]), "template_id": pipeline_template_id}
            )
            need_create_schemes.append(TemplateScheme(**scheme))

        # 批量删除scheme
        TemplateScheme.objects.filter(template__id=pipeline_template_id).delete()

        # 批量创建scheme
        try:
            if need_create_schemes:
                TemplateScheme.objects.bulk_create(need_create_schemes)
        except Exception as e:
            message = "create template({}) scheme failed: {}".format(template_id, str(e))
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.UNKNOWN_ERROR.code)}, exception=True)

        # 返回流程所有方案
        template_scheme_query = self.queryset.filter(template__id=pipeline_template_id)
        serializer = self.get_serializer(template_scheme_query, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        validated_data = self.get_serializer_params_data(request)
        pipeline_template_id = self.get_pipeline_template_id(**validated_data)
        queryset = self.get_queryset().filter(template__id=pipeline_template_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        validated_data = self.get_serializer_data(request)
        params_validated_data = self.get_serializer_params_data(request)
        pipeline_template_id = self.get_pipeline_template_id(**params_validated_data)
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

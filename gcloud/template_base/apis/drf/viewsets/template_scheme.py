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
specific language governing permissions and limitations under the License.
"""
import logging
from collections import Counter

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ErrorDetail
from pipeline.models import TemplateScheme, TemplateRelationship
from gcloud import err_code
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.template_base.apis.drf.permission import SchemeEditPermission
from gcloud.template_base.apis.drf.serilaziers.template_scheme import (
    TemplateSchemeSerializer,
    ParamsSerializer,
    DefaultTemplateSchemeSerializer,
)
from gcloud.template_base.models import DefaultTemplateScheme
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("root")


class DefaultTemplateSchemeViewSet(ApiMixin, viewsets.ModelViewSet):
    queryset = DefaultTemplateScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser | SchemeEditPermission]
    serializer_class = DefaultTemplateSchemeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ("project_id", "template_id")


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

        template = (
            model_cls.objects.filter(**_filter).only("pipeline_template__id", "pipeline_template__template_id").first()
        )
        if not template:
            template_type = f'project[{kwargs["project_id"]}]' if "project_id" in kwargs else "common_template"
            message = _(f"获取流程失败: 流程ID为[{template_id}]]的[{template_type}]类型流程不存在")
            logger.error(message)
            raise model_cls.DoesNotExist(ErrorDetail(message, err_code.UNKNOWN_ERROR.code))
        return template.pipeline_template.id, template.pipeline_template.template_id

    @staticmethod
    def get_scheme_quote_count_dict(template_id):
        """
        获取该模版作为子流程时，各执行方案的引用数
        @return:
        """
        queryset = TemplateRelationship.objects.prefetch_related("templatescheme_set").filter(
            descendant_template_id=template_id
        )

        total_scheme_id_list = []
        for relation in queryset:
            total_scheme_id_list += relation.templatescheme_set.all().values_list("id", flat=True)

        return Counter(total_scheme_id_list)

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

        create_schemes = []
        update_schemes = []
        update_scheme_ids = []

        pipeline_template_id, pipeline_template_template_id = self.get_pipeline_template_id(**validated_data)

        # 获取现有方案id列表
        existing_scheme_qs = TemplateScheme.objects.filter(template__id=pipeline_template_id)
        scheme_mappings = dict([(scheme.id, scheme) for scheme in existing_scheme_qs])

        for scheme in current_schemes:
            if "id" in scheme:
                scheme_id = scheme.pop("id")
                update_scheme_ids.append(scheme_id)
                scheme_obj = scheme_mappings[scheme_id]
                scheme_obj.unique_id = f'{template_id}-{scheme["name"]}'
                scheme_obj.name = scheme["name"]
                scheme_obj.data = scheme["data"]
                update_schemes.append(scheme_obj)
            else:
                scheme.update(
                    {"unique_id": "{}-{}".format(template_id, scheme["name"]), "template_id": pipeline_template_id}
                )
                create_schemes.append(TemplateScheme(**scheme))

        remove_scheme_ids_set = set(scheme_mappings.keys()) - set(update_scheme_ids)

        quote_scheme_ids_set = set(self.get_scheme_quote_count_dict(pipeline_template_template_id).keys())
        if remove_scheme_ids_set & quote_scheme_ids_set:
            message = _(f"执行方案删除失败: 待删除的[执行方案]已被引用[{quote_scheme_ids_set}], 请处理后重试 | batch_operate")
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        remove_scheme_ids = list(remove_scheme_ids_set)

        try:
            with transaction.atomic():
                # 批量删除scheme
                TemplateScheme.objects.filter(id__in=remove_scheme_ids).delete()
                # 批量更新scheme
                TemplateScheme.objects.bulk_update(update_schemes, ["unique_id", "name", "edit_time", "data"])
                # 批量创建scheme
                TemplateScheme.objects.bulk_create(create_schemes)
        except Exception as e:
            message = _(f"执行方案批量操作失败: 创建流程ID: {template_id}执行方案失败, 失败原因: {e} | batch_operate")
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.UNKNOWN_ERROR.code)}, exception=True)

        # 返回流程所有方案
        template_scheme_query = self.queryset.filter(template__id=pipeline_template_id)
        serializer = self.get_serializer(template_scheme_query, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        validated_data = self.get_serializer_params_data(request)
        pipeline_template_id, pipeline_template_template_id = self.get_pipeline_template_id(**validated_data)
        queryset = self.get_queryset().filter(template__id=pipeline_template_id)
        serializer = self.get_serializer(queryset, many=True)

        scheme_quote_count_dict = self.get_scheme_quote_count_dict(pipeline_template_template_id)
        for item in serializer.data:
            item.update({"quote_count": scheme_quote_count_dict.get(item["id"], 0)})

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        validated_data = self.get_serializer_data(request)
        params_validated_data = self.get_serializer_params_data(request)
        pipeline_template_id, _ = self.get_pipeline_template_id(**params_validated_data)
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
        scheme_quote_num = TemplateRelationship.objects.filter(templatescheme__id=kwargs["pk"]).count()

        if scheme_quote_num != 0:
            message = _(f"执行方案删除失败: 该执行方案被[{scheme_quote_num}]个子流程节点引用, 禁止删除. 请处理后重试 | destroy")
            logger.error(message)
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        return super(TemplateSchemeViewSet, self).destroy(request, *args, **kwargs)

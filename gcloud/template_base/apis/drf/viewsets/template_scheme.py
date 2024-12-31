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
import json
import logging
from collections import Counter

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from pipeline.models import TemplateRelationship, TemplateScheme
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response

from gcloud import err_code
from gcloud.clocked_task.models import ClockedTask
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import CLOCKED_TASK_NOT_STARTED
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.periodictask.models import PeriodicTask
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.apis.drf.permission import SchemeEditPermission
from gcloud.template_base.apis.drf.serilaziers.template_scheme import (
    DefaultTemplateSchemeSerializer,
    ParamsSerializer,
    TemplateSchemeSerializer,
)
from gcloud.template_base.models import DefaultTemplateScheme

logger = logging.getLogger("root")


class DefaultTemplateSchemeViewSet(ApiMixin, viewsets.ModelViewSet):
    queryset = DefaultTemplateScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated, SchemeEditPermission]
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

    @staticmethod
    def get_app_maker_names_scheme_quote(template_id, remove_scheme_ids_set):
        """
        获取该模板作为轻应用时，各执行方案的引用数
        @return:
        """
        app_maker_queryset = AppMaker.objects.filter(task_template__id=template_id, is_deleted=False)

        return list(
            {
                app_maker.name
                for app_maker in app_maker_queryset
                if app_maker.template_scheme_id and int(app_maker.template_scheme_id) in remove_scheme_ids_set
            }
        )

    @staticmethod
    def get_periodic_task_names_scheme_quote(template_id, remove_scheme_ids_set):
        periodic_task_queryset = PeriodicTask.objects.filter(template_id=template_id)
        periodic_names = []

        for periodic_task in periodic_task_queryset:
            template_scheme_ids = json.loads(periodic_task.template_scheme_ids)
            if set(template_scheme_ids) & remove_scheme_ids_set:
                periodic_names.append(periodic_task.name)

        return periodic_names

    @staticmethod
    def get_clocked_task_names_scheme_quote(template_id, remove_scheme_ids_set):
        clocked_task_queryset = ClockedTask.objects.filter(template_id=template_id, state=CLOCKED_TASK_NOT_STARTED)
        clocked_task_names = []

        for clocked_task in clocked_task_queryset:
            template_scheme_ids = json.loads(clocked_task.task_params).get("template_schemes_id", [])
            if set(template_scheme_ids) & remove_scheme_ids_set:
                clocked_task_names.append(clocked_task.task_name)

        return clocked_task_names

    def validate_batch_delete_scheme(self, pipeline_template_template_id, template_id, remove_scheme_ids_set):

        template_quote_scheme_ids_set = set(self.get_scheme_quote_count_dict(pipeline_template_template_id).keys())

        if remove_scheme_ids_set & template_quote_scheme_ids_set:
            message = _(
                f"执行方案删除失败: 待删除的[执行方案]已被引用[{template_quote_scheme_ids_set}], 请处理后重试 | batch_operate"
            )
            logger.error(message)
            return message

        app_maker_names = self.get_app_maker_names_scheme_quote(template_id, remove_scheme_ids_set)
        if app_maker_names:
            message = _(
                f"执行方案删除失败: 待删除的[执行方案]已被这些轻应用所引用{app_maker_names}, 请处理后重试 | batch_operate"
            )
            logger.error(message)
            return message

        periodic_names = self.get_periodic_task_names_scheme_quote(template_id, remove_scheme_ids_set)
        if periodic_names:
            message = _(
                f"执行方案删除失败: 待删除的[执行方案]已被这些周期任务所引用{periodic_names}, 请处理后重试 | batch_operate"
            )
            logger.error(message)
            return message

        clocked_names = self.get_clocked_task_names_scheme_quote(template_id, remove_scheme_ids_set)
        if clocked_names:
            message = _(
                f"执行方案删除失败: 待删除的[执行方案]已被这些计划任务所引用{clocked_names}, 请处理后重试 | batch_operate"
            )
            logger.error(message)
            return message

        return None

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
                scheme_obj.unique_id = "{}-{}".format(template_id, scheme["name"])
                update_schemes.append(scheme_obj)
            else:
                scheme.update(
                    {"unique_id": "{}-{}".format(template_id, scheme["name"]), "template_id": pipeline_template_id}
                )
                create_schemes.append(TemplateScheme(**scheme))

        remove_scheme_ids_set = set(scheme_mappings.keys()) - set(update_scheme_ids)

        remove_scheme_ids = list(remove_scheme_ids_set)

        error_message = self.validate_batch_delete_scheme(
            pipeline_template_template_id, template_id, remove_scheme_ids_set
        )
        if error_message:
            return Response({"detail": ErrorDetail(error_message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        template_id = instance.unique_id.split("-")[0]
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # 防止用户不传name
        instance.unique_id = "{}-{}".format(template_id, serializer.validated_data.get("name") or instance.name)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        scheme = self.get_object()
        # 获取流程所关联的模版id
        template_id = scheme.unique_id.split("-")[0]
        message = self.validate_batch_delete_scheme(scheme.template.template_id, template_id, {scheme.id})

        if message:
            return Response({"detail": ErrorDetail(message, err_code.REQUEST_PARAM_INVALID.code)}, exception=True)

        return super(TemplateSchemeViewSet, self).destroy(request, *args, **kwargs)

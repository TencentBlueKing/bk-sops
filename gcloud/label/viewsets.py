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
from functools import wraps

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from gcloud.constants import PROJECT, COMMON
from gcloud.core.apis.drf.exceptions import ValidationException
from gcloud.core.apis.drf.viewsets import ApiMixin, permissions
from gcloud.label.models import Label, TemplateLabelRelation
from gcloud.label.permissions import LabelIAMAdapter
from gcloud.label.serilaziers import NewLabelSerializer
from gcloud.openapi.schema import AnnotationAutoSchema
from gcloud.utils.models import Convert


def label_view_decorator(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        project_id = request.query_params.get("project_id") or request.data.get("project_id")
        from_space = request.query_params.get("from_space") or request.data.get("from_space")
        if project_id is not None and from_space is not None:
            raise ValidationException("[label_view_decorator] project_id and from_space can not both be filled.")
        scope_id = (
            project_id
            if not from_space
            else request.query_params.get("from_space_id") or request.data.get("from_space_id")
        )
        scope_type = PROJECT if not from_space else COMMON
        setattr(request, "scope_id", scope_id)
        setattr(request, "scope_type", scope_type)

        return func(request, *args, **kwargs)

    return wrapper


class NewLabelViewSet(ApiMixin, ModelViewSet):
    """
    流程标签相关接口

    delete: 标签删除接口，不允许删除默认标签
    update: 标签修改接口，不允许修改默认标签
    """

    queryset = Label.objects.all().order_by(Convert("name", "gbk"))
    serializer_class = NewLabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"

    @method_decorator(label_view_decorator)
    def create(self, request, *args, **kwargs):
        LabelIAMAdapter(handler_type=request.scope_type).handle(request, self.action, request.scope_id)
        return super(NewLabelViewSet, self).create(request, *args, **kwargs)

    @method_decorator(label_view_decorator)
    def list(self, request, *args, **kwargs):
        LabelIAMAdapter(handler_type=request.scope_type).handle(request, self.action, request.scope_id)
        return super(NewLabelViewSet, self).list(request, *args, **kwargs)

    @method_decorator(label_view_decorator)
    def update(self, request, *args, **kwargs):
        label = self.get_object()
        if label.is_default:
            raise ValidationException("default label cannot be updated.")
        scope_id = label.project_id or label.from_space_id
        scope_type = PROJECT if label.project_id else COMMON
        LabelIAMAdapter(handler_type=scope_type).handle(request, self.action, scope_id)
        return super(NewLabelViewSet, self).update(request, *args, **kwargs)

    @method_decorator(label_view_decorator)
    def destroy(self, request, *args, **kwargs):
        label = self.get_object()
        if label.is_default:
            raise ValidationException("default label cannot be deleted.")
        scope_id = label.project_id or label.from_space_id
        scope_type = PROJECT if label.project_id else COMMON
        LabelIAMAdapter(handler_type=scope_type).handle(request, self.action, scope_id)
        self.perform_destroy(label)
        return Response({"result": True, "message": "success"})

    @swagger_auto_schema(methods=["get"], auto_schema=AnnotationAutoSchema, ignore_filter_query=True)
    @action(methods=["get"], detail=False)
    @method_decorator(label_view_decorator)
    def list_with_default_labels(self, request, *args, **kwargs):
        """
        获取某个项目下的标签（包括默认标签）

        param: project_id: 项目ID, integer, query, required
        """
        LabelIAMAdapter(handler_type=request.scope_type).handle(request, self.action, request.scope_id)
        if request.scope_type == PROJECT:
            queryset = Label.objects.get_project_label_with_default(request.scope_id)
        else:
            queryset = Label.objects.get_common_label_with_default()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(method="get", auto_schema=AnnotationAutoSchema, ignore_filter_query=True)
    @action(methods=["get"], detail=False)
    @method_decorator(label_view_decorator)
    def get_templates_labels(self, request):
        """
        批量获取某些流程对应的标签

        param: project_id: 项目ID, integer, query, required
        param: template_ids: 流程ID列表(以`,`分隔), string, query, required

        return: 流程对应标签信息
        {
            "template_id": [
                {
                    "name": "标签名(string)",
                    "color": "标签名称(string)",
                    "label_id": "标签ID(integer)"
                }
            ]
        }
        """
        return self._fetch_label_or_template_ids(request, fetch_label=True)

    @swagger_auto_schema(method="get", auto_schema=AnnotationAutoSchema, ignore_filter_query=True)
    @action(methods=["get"], detail=False)
    @method_decorator(label_view_decorator)
    def get_label_template_ids(self, request):

        """
        批量某些标签对应的流程id

        param: project_id: 项目ID, integer, query, required
        param: label_ids: 标签ID列表(以`,`分隔), string, query, required

        return: 标签对应的流程ID列表
        {
            "label_id": ["template_id(integer)"]
        }
        """
        return self._fetch_label_or_template_ids(request, fetch_label=False)

    def _fetch_label_or_template_ids(self, request, fetch_label):
        base_id_name = "template_ids" if fetch_label else "label_ids"
        if fetch_label:
            fetch_func = TemplateLabelRelation.objects.fetch_templates_labels
        else:
            fetch_func = TemplateLabelRelation.objects.fetch_label_template_ids
        base_ids = request.query_params.get(base_id_name)
        if not base_ids:
            raise ValidationException("{} must be provided.".format(base_id_name))
        LabelIAMAdapter(handler_type=request.scope_type).handle(request, self.action, request.scope_id)
        base_ids = [int(base_id) for base_id in base_ids.strip().split(",")]
        return Response(fetch_func(base_ids, template_source=request.scope_type))

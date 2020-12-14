# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from gcloud.core.apis.drf.exceptions import ValidationException
from gcloud.core.apis.drf.viewsets import ApiMixin, permissions
from gcloud.label.models import Label, TemplateLabelRelation
from gcloud.label.serilaziers import LabelSerializer


class LabelViewSet(ApiMixin, ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id")
        if not project_id:
            raise ValidationException("project_id should be provided.")
        return super(LabelViewSet, self).list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.get_object().is_default:
            raise ValidationException("default label cannot be updated.")
        return super(LabelViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if self.get_object().is_default:
            raise ValidationException("default label cannot be deleted.")
        return super(LabelViewSet, self).destroy(request, *args, **kwargs)

    @action(methods=["get"], detail=False)
    def list_with_default_labels(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id")
        if not project_id:
            raise ValidationException("project_id should be provided.")
        queryset = Label.objects.filter(Q(project_id=project_id) | Q(is_default=True))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def get_templates_labels(self, request):
        template_ids = request.query_params.get("template_ids")
        if not template_ids:
            raise ValidationException("template_ids must be provided.")
        template_ids = [int(template_id) for template_id in template_ids.strip().split(",")]
        return Response(TemplateLabelRelation.objects.fetch_templates_labels(template_ids))

    @action(methods=["get"], detail=False)
    def get_label_template_ids(self, request):
        label_ids = request.query_params.get("label_ids")
        if not label_ids:
            raise ValidationException("label_ids must be provided.")
        label_ids = [int(label_id) for label_id in label_ids.strip().split(",")]
        return Response(TemplateLabelRelation.objects.fetch_label_template_ids(label_ids))

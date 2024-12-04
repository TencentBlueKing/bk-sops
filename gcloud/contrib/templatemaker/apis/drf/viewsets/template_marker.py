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

from rest_framework.response import Response
from rest_framework import permissions

from gcloud.contrib.templatemaker.models import TemplateSharedRecord
from gcloud.core.apis.drf.serilaziers.task_template import TaskTemplateSerializer, TaskTemplateListSerializer
from gcloud.taskflow3.models import TaskTemplate
from gcloud.label.models import TemplateLabelRelation
from gcloud.core.apis.drf.viewsets.base import GcloudModelViewSet


class HasValidTemplateID(permissions.BasePermission):
    def has_permission(self, request, view):
        template_id = view.kwargs.get("pk")

        if not template_id:
            logging.warning("template_id is required.")
            return False
        try:
            TemplateSharedRecord.objects.get(template_id=template_id)
        except Exception:
            logging.warning("template_id {} does not exist.".format(template_id))
            return False
        return True


class TemplateMakerViewSet(GcloudModelViewSet):
    queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
    permission_classes = [permissions.IsAuthenticated, HasValidTemplateID]

    def get_serializer_class(self):
        if self.action == "list":
            return TaskTemplateListSerializer
        return TaskTemplateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        labels = TemplateLabelRelation.objects.fetch_templates_labels([instance.id]).get(instance.id, [])
        data["template_labels"] = [label["label_id"] for label in labels]

        return Response(data)

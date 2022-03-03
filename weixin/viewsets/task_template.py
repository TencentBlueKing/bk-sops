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

from django.contrib.auth import get_user_model
from rest_framework.response import Response

from gcloud.core.apis.drf.viewsets import TaskTemplateViewSet
from gcloud.label.models import TemplateLabelRelation
from gcloud.iam_auth import IAMMeta
from weixin.utils import iam_based_obj_list_filter


class WxTaskTemplateViewSet(TaskTemplateViewSet):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持使用方配置不分页
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, queryset)
        user_model = get_user_model()
        collected_templates = (
            user_model.objects.get(username=request.user.username).tasktemplate_set.all().values_list("id", flat=True)
        )
        template_ids = [obj["id"] for obj in data]
        templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(template_ids)
        for obj in data:
            obj["is_add"] = 1 if obj["id"] in collected_templates else 0
            obj["template_labels"] = templates_labels.get(obj["id"], [])
        data = iam_based_obj_list_filter(data, [IAMMeta.FLOW_VIEW_ACTION, IAMMeta.FLOW_CREATE_TASK_ACTION])
        return self.get_paginated_response(data) if page is not None else Response(data)

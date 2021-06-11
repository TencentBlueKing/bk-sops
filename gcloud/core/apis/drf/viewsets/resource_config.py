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
from django.http import QueryDict
from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response

from gcloud.core.models import ResourceConfig
from gcloud.core.apis.drf.serilaziers import ResourceConfigSerializer
from gcloud.core.apis.drf.viewsets.utils import ApiMixin


class ResourceConfigViewSet(
    ApiMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ResourceConfig.objects.all().order_by("-id")
    serializer_class = ResourceConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id")
        config_type = request.query_params.get("config_type")
        queryset = self.get_queryset().filter(project_id=project_id, config_type=config_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data.update({"creator": request.user.username})
        return super(ResourceConfigViewSet, self).create(request, *args, **kwargs)

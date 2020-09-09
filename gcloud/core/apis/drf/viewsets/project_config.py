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

from rest_framework import mixins, permissions, viewsets

from gcloud.core.models import Project, ProjectConfig
from gcloud.core.apis.drf.serilaziers import ProjectConfigSerializer
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.core.apis.drf.exceptions import ObjectDoesNotExistException


class ProjectConfigViewSet(ApiMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ProjectConfig.objects.all()
    serializer_class = ProjectConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        project_id = self.kwargs["pk"]

        if not Project.objects.filter(id=project_id).exists():
            raise ObjectDoesNotExistException("Project id: {} does not exist".format(project_id))

        obj, _ = ProjectConfig.objects.get_or_create(project_id=project_id)

        return obj

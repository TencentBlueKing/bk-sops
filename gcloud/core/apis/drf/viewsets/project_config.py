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

from django.conf import settings
from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed
from rest_framework import mixins, permissions, viewsets
from rest_framework.permissions import IsAdminUser

from gcloud.contrib.audit.instances import AuditSnapshot
from gcloud.contrib.audit.utils import bk_audit_add_event_on_commit
from gcloud.core.apis.drf.exceptions import ObjectDoesNotExistException
from gcloud.core.apis.drf.serilaziers import ProjectConfigSerializer
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.core.models import Project, ProjectConfig
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

iam = get_iam_client()


class ProjectConfigPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs["pk"]
        action = IAMMeta.PROJECT_VIEW_ACTION if view.action in ["retrieve"] else IAMMeta.PROJECT_EDIT_ACTION
        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(action),
            resources=res_factory.resources_for_project(project_id),
        )
        return True


class ProjectConfigViewSet(ApiMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = ProjectConfig.objects.all()
    serializer_class = ProjectConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser | ProjectConfigPermission]

    def get_object(self):
        project_id = self.kwargs["pk"]

        if not Project.objects.filter(id=project_id).exists():
            raise ObjectDoesNotExistException("Project id: {} does not exist".format(project_id))

        obj, _ = ProjectConfig.objects.get_or_create(project_id=project_id)

        return obj

    @staticmethod
    def _audit_data(config):
        return AuditSnapshot(
            {
                "executor_proxy": config.executor_proxy,
                "executor_proxy_exempts": config.executor_proxy_exempts,
            }
        )

    def update(self, request, *args, **kwargs):
        config = self.get_object()
        project = Project.objects.get(id=config.project_id) if settings.ENABLE_BK_AUDIT else None
        origin_data = self._audit_data(config) if settings.ENABLE_BK_AUDIT else None
        response = super(ProjectConfigViewSet, self).update(request, *args, **kwargs)
        if settings.ENABLE_BK_AUDIT:
            config.refresh_from_db()
            bk_audit_add_event_on_commit(
                username=request.user.username,
                action_id=IAMMeta.PROJECT_EDIT_ACTION,
                resource_id=IAMMeta.PROJECT_RESOURCE,
                instance=project,
                origin_data=origin_data,
                data=self._audit_data(config),
            )
        return response

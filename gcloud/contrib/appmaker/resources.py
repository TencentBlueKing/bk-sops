# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest

from auth_backend.plugins.tastypie.authorization import BkSaaSLooseAuthorization

from gcloud.conf import settings
from gcloud.tasktmpl3.resources import TaskTemplateResource
from gcloud.webservice3.resources import (
    GCloudModelResource,
    ProjectResource,
)
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.appmaker.permissions import mini_app_resource


class OnlyDeleteDetailAuthorization(BkSaaSLooseAuthorization):
    def create_detail(self, object_list, bundle):
        return False

    def update_detail(self, object_list, bundle):
        return False


class AppMakerResource(GCloudModelResource):
    project = fields.ForeignKey(
        ProjectResource,
        'project',
        full=True
    )
    creator_name = fields.CharField(
        attribute='creator_name',
        readonly=True,
        null=True
    )
    editor_name = fields.CharField(
        attribute='editor_name',
        readonly=True,
        null=True
    )
    template_scheme_id = fields.CharField(
        attribute='template_scheme_id',
        readonly=True,
        blank=True
    )
    task_template = fields.ForeignKey(
        TaskTemplateResource,
        'task_template',
    )
    template_id = fields.CharField(
        attribute='task_template_id',
        readonly=True,
        null=True
    )
    template_name = fields.CharField(
        attribute='task_template_name',
        readonly=True,
        null=True
    )
    category = fields.CharField(
        attribute='category',
        readonly=True,
        null=True
    )

    class Meta(GCloudModelResource.Meta):
        queryset = AppMaker.objects.filter(is_deleted=False)
        resource_name = 'appmaker'
        auth_resource = mini_app_resource
        authorization = OnlyDeleteDetailAuthorization(auth_resource=auth_resource,
                                                      read_action_id='view',
                                                      update_action_id='edit')
        filtering = {
            "project": ALL_WITH_RELATIONS,
            "template": ALL_WITH_RELATIONS,
            "name": ALL,
            "creator": ALL,
            "editor": ALL,
            'create_time': ['gte', 'lte'],
            'edit_time': ['gte', 'lte'],
        }

    def obj_delete(self, bundle, **kwargs):
        try:
            appmaker_id = kwargs['pk']
            appmaker = AppMaker.objects.get(pk=appmaker_id)
        except Exception:
            raise BadRequest('appmaker[id=%s] does not exist' % appmaker_id)
        project_id = appmaker.project.id

        if settings.IS_LOCAL:
            fake = True
        else:
            fake = False

        result, data = AppMaker.objects.del_app_maker(
            project_id, appmaker_id, fake
        )
        if not result:
            raise BadRequest(data)

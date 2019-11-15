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
from tastypie.constants import ALL
from tastypie.authorization import ReadOnlyAuthorization

from gcloud.webservice3.resources import GCloudModelResource
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.resources import TaskTemplateResource
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.resources import TaskFlowInstanceResource
from gcloud.periodictask.models import PeriodicTaskHistory
from gcloud.periodictask.resources import PeriodicTaskResource


class AdminTaskTemplateResource(TaskTemplateResource):

    class Meta(TaskTemplateResource.Meta):
        queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False)
        resource_name = 'template'


class AdminTaskFlowInstanceResource(TaskFlowInstanceResource):

    class Meta(TaskFlowInstanceResource.Meta):
        queryset = TaskFlowInstance.objects.filter(pipeline_instance__isnull=False)
        resource_name = 'taskflow'


class AdminPeriodicTaskResource(PeriodicTaskResource):
    class Meta(PeriodicTaskResource.Meta):
        resource_name = 'periodic_task'


class AdminPeriodicTaskHistoryResource(GCloudModelResource):

    id = fields.IntegerField(
        attribute='id',
        readonly=True
    )
    task_id = fields.IntegerField(
        attribute='task_id',
        readonly=True
    )
    start_at = fields.DateTimeField(
        attribute='start_at',
        readonly=True
    )
    start_success = fields.BooleanField(
        attribute='start_success',
        readonly=True
    )
    ex_data = fields.CharField(
        attribute='ex_data',
        readonly=True
    )

    class Meta(GCloudModelResource.Meta):
        queryset = PeriodicTaskHistory.objects.all().order_by('-id')
        resource_name = 'periodic_task_history'
        authorization = ReadOnlyAuthorization()

        filtering = {
            'task_id': ALL
        }

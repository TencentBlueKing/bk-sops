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

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.resources import TaskTemplateResource
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.resources import TaskFlowInstanceResource
from gcloud.periodictask.resources import PeriodicTaskResource


class AdminTaskTemplateResource(TaskTemplateResource):

    class Meta(TaskTemplateResource.Meta):
        queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False)
        resource_name = 'admin-template'


class AdminTaskFlowInstanceResource(TaskFlowInstanceResource):

    class Meta(TaskFlowInstanceResource.Meta):
        queryset = TaskFlowInstance.objects.filter(pipeline_instance__isnull=False)
        resource_name = 'admin-taskflow'


class AdminPeriodicTaskResource(PeriodicTaskResource):
    class Meta(PeriodicTaskResource.Meta):
        resource_name = 'admin-periodic_task'

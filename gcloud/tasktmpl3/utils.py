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

import logging

from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("root")


def get_template_context(pipeline_template, data_type, username=''):
    try:
        template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
    except TaskTemplate.DoesNotExist:
        logger.warning('TaskTemplate Does not exist: pipeline_template.id=%s' % pipeline_template.pk)
        return {}
    context = {
        'project_id': template.project.id,
        'project_name': template.project.name,
        'operator': template.pipeline_template.editor or username
    }
    return context

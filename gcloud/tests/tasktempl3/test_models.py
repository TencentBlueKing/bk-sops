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

from django.test import TestCase

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class TaskTemplateTestCase(TestCase):

    @patch(TASKTEMPLATE_CREATE_PIPELINE_TEMPLATE, MagicMock(return_value='pipeline_template'))
    @patch(TASKTEMPLATE_MODEL, MagicMock())
    def test_create(self):
        kwargs = {
            'project': 'project',
            'category': 'category',
            'notify_type': 'notify_type',
            'notify_receivers': 'notify_receivers',
            'time_out': 'time_out'
        }
        self.assertIsNotNone(TaskTemplate.objects.create(**kwargs))
        TaskTemplate.objects.model.assert_called_once_with(pipeline_template='pipeline_template', **kwargs)

    def test_export_templates(self):
        pass

    def test_export_templates__extra_id(self):
        pass

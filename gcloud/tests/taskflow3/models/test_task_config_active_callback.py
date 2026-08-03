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
from django.test import TestCase

from gcloud.taskflow3.models import TaskConfig


class EnableActiveCallbackTakeoverTestCase(TestCase):
    def setUp(self):
        self.project_id = 1
        self.template_id = 100

    def _create_project_config(self, config_value, project_id=None):
        return TaskConfig.objects.create(
            scope=TaskConfig.SCOPE_TYPE_PROJECT,
            scope_id=self.project_id if project_id is None else project_id,
            config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
            config_value=config_value,
        )

    def _create_template_config(self, config_value, template_id=None):
        return TaskConfig.objects.create(
            scope=TaskConfig.SCOPE_TYPE_TEMPLATE,
            scope_id=self.template_id if template_id is None else template_id,
            config_type=TaskConfig.CONFIG_TYPE_ACTIVE_CALLBACK,
            config_value=config_value,
        )

    def test_no_config_return_false(self):
        self.assertFalse(TaskConfig.objects.enable_active_callback_takeover(self.project_id, self.template_id))

    def test_template_disable_override_project_enable(self):
        self._create_project_config(TaskConfig.ENABLE_ACTIVE_CALLBACK)
        self._create_template_config(TaskConfig.DISABLE_ACTIVE_CALLBACK)
        self.assertFalse(TaskConfig.objects.enable_active_callback_takeover(self.project_id, self.template_id))

    def test_fallback_to_project_config(self):
        self._create_project_config(TaskConfig.ENABLE_ACTIVE_CALLBACK)
        self.assertTrue(TaskConfig.objects.enable_active_callback_takeover(self.project_id, self.template_id))

    def test_template_enable_only(self):
        self._create_template_config(TaskConfig.ENABLE_ACTIVE_CALLBACK)
        self.assertTrue(TaskConfig.objects.enable_active_callback_takeover(self.project_id, self.template_id))

    def test_common_template_negative_scope_id(self):
        # 公共流程 project_id 记为 -1，模板配置以 -template_id 存储
        self._create_template_config(TaskConfig.ENABLE_ACTIVE_CALLBACK, template_id=-self.template_id)
        self.assertTrue(TaskConfig.objects.enable_active_callback_takeover(-1, self.template_id))

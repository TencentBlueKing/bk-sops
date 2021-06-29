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
from django.test import TestCase

from gcloud.project_constants.domains import context
from gcloud.project_constants.models import ProjectConstant


class ContextTestCase(TestCase):
    def test_get_project_constants_context(self):
        ProjectConstant.objects.create(project_id=1, name="string", key="key1", value="val1")
        ProjectConstant.objects.create(project_id=1, name="string", key="key2", value="val2")
        project_constants_context = context.get_project_constants_context(1)
        self.assertEqual(project_constants_context, {"${_env_key1}": "val1", "${_env_key2}": "val2"})

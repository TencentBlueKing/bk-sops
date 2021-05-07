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

from gcloud.core.models import EngineConfig


class EngineConfigTestCase(TestCase):
    def test_get_engine_ver__not_config(self):
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=1, template_source="project")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V1)

    def test_get_engine_ver__config_template(self):
        EngineConfig.objects.create(
            scope_id=1,
            scope=EngineConfig.SCOPE_TYPE_TEMPLATE,
            engine_ver=EngineConfig.ENGINE_VER_V2,
            template_source="project",
        )
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=1, template_source="project")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V2)
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=1, template_source="common")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V1)

        EngineConfig.objects.create(
            scope_id=1,
            scope=EngineConfig.SCOPE_TYPE_TEMPLATE,
            engine_ver=EngineConfig.ENGINE_VER_V2,
            template_source="common",
        )
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=1, template_source="project")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V2)

    def test_get_engine_ver__config_project(self):
        EngineConfig.objects.create(
            scope_id=1,
            scope=EngineConfig.SCOPE_TYPE_PROJECT,
            engine_ver=EngineConfig.ENGINE_VER_V2,
            template_source="project",
        )
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=2, template_source="project")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V2)
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=3, template_source="project")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V2)
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=4, template_source="common")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V2)

        EngineConfig.objects.create(
            scope_id=2,
            scope=EngineConfig.SCOPE_TYPE_TEMPLATE,
            engine_ver=EngineConfig.ENGINE_VER_V1,
            template_source="project",
        )
        engine_ver = EngineConfig.objects.get_engine_ver(project_id=1, template_id=2, template_source="project")
        self.assertEqual(engine_ver, EngineConfig.ENGINE_VER_V1)

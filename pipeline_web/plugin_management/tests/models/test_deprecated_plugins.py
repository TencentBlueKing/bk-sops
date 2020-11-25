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

from django.test import TestCase

from pipeline_web.plugin_management.models import DeprecatedPlugin


class DeprecatedPluginTestCase(TestCase):
    def setUpClass():
        DeprecatedPlugin.objects.create(
            code="bk_notify",
            version="legacy",
            type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT,
            phase=DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="bk_notify",
            version="v1.0",
            type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT,
            phase=DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="bk_job",
            version="legacy",
            type=DeprecatedPlugin.PLUGIN_TYPE_COMPONENT,
            phase=DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="ip",
            version="legacy",
            type=DeprecatedPlugin.PLUGIN_TYPE_VARIABLE,
            phase=DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="ip",
            version="v1.0",
            type=DeprecatedPlugin.PLUGIN_TYPE_VARIABLE,
            phase=DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
        )
        DeprecatedPlugin.objects.create(
            code="ip_selector",
            version="v1.0",
            type=DeprecatedPlugin.PLUGIN_TYPE_VARIABLE,
            phase=DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
        )

    def tearDownClass():
        DeprecatedPlugin.objects.all().delete()

    def test_get_components_phase_dict(self):
        phase_dict = DeprecatedPlugin.objects.get_components_phase_dict()

        self.assertEqual(
            phase_dict,
            {
                "bk_notify": {
                    "legacy": DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
                    "v1.0": DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED,
                },
                "bk_job": {"legacy": DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED},
            },
        )

    def test_get_variables_phase_dict(self):
        phase_dict = DeprecatedPlugin.objects.get_variables_phase_dict()

        self.assertEqual(
            phase_dict,
            {
                "ip": {
                    "legacy": DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
                    "v1.0": DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED,
                },
                "ip_selector": {"v1.0": DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED},
            },
        )

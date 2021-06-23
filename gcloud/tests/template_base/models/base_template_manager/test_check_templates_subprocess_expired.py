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

from mock import patch, MagicMock
from django.test import TestCase

from gcloud.tests.mock_settings import *  # noqa
from gcloud.template_base.models import BaseTemplateManager


class CheckTemplatesSubprocessExpiredTestCase(TestCase):
    def test_normal(self):
        r1 = MagicMock()
        r2 = MagicMock()
        r3 = MagicMock()
        r4 = MagicMock()
        r5 = MagicMock()

        r1.ancestor_template_id = "a1"
        r1.descendant_template_id = "d1"
        r1.subprocess_node_id = "n1"
        r1.version = "v1"
        r1.always_use_latest = True

        r2.ancestor_template_id = "a1"
        r2.descendant_template_id = "d2"
        r2.subprocess_node_id = "n2"
        r2.version = "v2"
        r2.always_use_latest = False

        r3.ancestor_template_id = "a2"
        r3.descendant_template_id = "d3"
        r3.subprocess_node_id = "n3"
        r3.version = "v3"
        r3.always_use_latest = False

        r4.ancestor_template_id = "a2"
        r4.descendant_template_id = "d4"
        r4.subprocess_node_id = "n4"
        r4.version = "v4"
        r4.always_use_latest = True

        r5.ancestor_template_id = "a3"
        r5.descendant_template_id = "d5"
        r5.subprocess_node_id = "n5"
        r5.version = "v5"
        r5.always_use_latest = False

        v1 = MagicMock()
        v2 = MagicMock()
        v3 = MagicMock()
        v4 = MagicMock()
        v5 = MagicMock()

        v1.template_id = "d1"
        v1.current_version = "v1_new"

        v2.template_id = "d2"
        v2.current_version = "v2"

        v3.template_id = "d3"
        v3.current_version = "v3_new"

        v4.template_id = "d4"
        v4.current_version = "v4_new"

        v5.template_id = "d5"
        v5.current_version = "v5"

        TemplateRelationship = MagicMock()
        TemplateRelationship.objects.filter = MagicMock(return_value=[r1, r2, r3, r4, r5])

        TemplateCurrentVersion = MagicMock()
        TemplateCurrentVersion.objects.filter = MagicMock(return_value=[v1, v2, v3, v4, v5])

        with patch(TEMPLATE_BASE_MODELS_TEMPLATE_RELATIONSHIP, TemplateRelationship):
            with patch(TEMPLATE_BASE_MODELS_TEMPLATE_CURRENT_VERSION, TemplateCurrentVersion):
                expired_template_id = BaseTemplateManager().check_templates_subprocess_expired(
                    [
                        {"id": "t1", "pipeline_template_id": "a1"},
                        {"id": "t1", "pipeline_template_id": "a1"},
                        {"id": "t2", "pipeline_template_id": "a2"},
                        {"id": "t2", "pipeline_template_id": "a2"},
                        {"id": "t3", "pipeline_template_id": "a3"},
                    ]
                )

        self.assertEqual(expired_template_id, ["t2"])

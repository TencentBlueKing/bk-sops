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

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from gcloud.common_template.models import CommonTemplateManager
from gcloud.exceptions import FlowExportError
from gcloud.template_base.models import BaseTemplateManager


class ExportTemplatesTestCase(SimpleTestCase):
    def test_template_without_pipeline_template_is_rejected(self):
        manager = BaseTemplateManager()
        manager.model = type("CommonTemplate", (), {})
        queryset = MagicMock()
        queryset.select_related.return_value.values.return_value = [{"id": 1, "pipeline_template_id": None}]
        manager.filter = MagicMock(return_value=queryset)

        with self.assertRaisesRegex(FlowExportError, r"流程 \[1\] 缺少关联的流程定义"):
            manager.export_templates([1])


class CommonTemplateExportTemplatesTestCase(SimpleTestCase):
    def test_full_export_excludes_deleted_templates(self):
        manager = CommonTemplateManager()
        active_queryset = MagicMock()
        active_queryset.values_list.return_value = [1, 2]
        unrestricted_queryset = MagicMock()
        unrestricted_queryset.values.return_value = [
            {"id": 1, "extra_info": {"project_scope": ["*"]}},
            {"id": 2, "extra_info": {"project_scope": ["*"]}},
        ]
        manager.filter = MagicMock(side_effect=[active_queryset, unrestricted_queryset])

        with patch.object(BaseTemplateManager, "export_templates", return_value={}) as export_templates:
            manager.export_templates([], is_full=True)

        manager.filter.assert_any_call(is_deleted=False)
        export_templates.assert_called_once_with([1, 2], is_full=True)

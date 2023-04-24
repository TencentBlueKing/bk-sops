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

from gcloud.template_base.models import BaseTemplateManager
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from pipeline_web.wrapper import PipelineTemplateWebWrapper


class MockArgs(object):
    """
    mock 请求参数
    """

    def __init__(self):
        self.template_data = {
            "exporter_version": 1,
            "pipeline_template_data": {},
            "template": {
                "3": {
                    "category": "Default",
                    "executor_proxy": "",
                    "id": 3,
                    "notify_type": '{"success":[],"fail":[]}',
                    "pipeline_template_id": "nb35afe8b9f335cb9f36f6c55906fcd9",
                    "pipeline_template_str_id": "nb35afe8b9f335cb9f36f6c55906fcd9",
                    "project_id": 1,
                    "time_out": 20,
                }
            },
            "template_source": "project",
        }

        self.check_info = {
            "can_override": True,
            "new_template": [
                {"id": 3, "name": "定时器1"},
            ],
            "override_template": [
                {"id": 3, "name": "定时器1", "template_id": "b7ccd053a6dc39959a9e585dfac9811b"},
            ],
        }
        self.operator = "admin"

    @staticmethod
    def defaults_getter(template_dict):
        return {
            "category": template_dict["category"],
            "notify_type": template_dict["notify_type"],
            "time_out": template_dict["time_out"],
            "pipeline_template_id": template_dict["pipeline_template_id"],
            "is_deleted": False,
        }


class MockBaseTemplateManagerModel(object):
    def __call__(self, *args, **kwargs):
        return None

    @property
    def objects(self):
        return self

    def filter(self, id__in=None, is_deleted=None, template_id__in=None, pipeline_template_id__in=None):
        # mock create_templates
        if pipeline_template_id__in:
            template = MagicMock()
            template.id = 4
            template.name = "定时器1"
            template.pipeline_template_id = list(pipeline_template_id__in)[0]
            return [template]
        return self

    def values_list(self, pipeline_template_id, flat):
        return []

    def update_or_create(self, id, defaults):
        return self, True

    def update(self, creator):
        return True

    def bulk_create(self, new_objects):
        return True

    def __name__(self):
        return "TaskTemplate"


mock_id_map = {
    PipelineTemplateWebWrapper.ID_MAP_KEY: {"nb35afe8b9f335cb9f36f6c55906fcd9": "nb35afe8b9f335cb9f36f6c55906fcd9"}
}


class PerformImportTest(TestCase):
    @mock.patch("pipeline_web.wrapper.PipelineTemplateWebWrapper.import_templates", mock.Mock(return_value=mock_id_map))
    @mock.patch("gcloud.iam_auth.resource_creator_action.signals.batch_create.send", mock.Mock(return_value=True))
    def mock_perform_import(self, override):
        """
        @param override: 是否覆盖
        """
        base_template_manager = BaseTemplateManager()
        base_template_manager.model = MockBaseTemplateManagerModel()
        base_template_manager.update_or_create = MockBaseTemplateManagerModel().update_or_create
        mock_args = MockArgs()
        return base_template_manager._perform_import(
            template_data=mock_args.template_data,
            check_info=mock_args.check_info,
            override=override,
            defaults_getter=mock_args.defaults_getter,
            operator=mock_args.operator,
        )

    def test_override(self):
        result = self.mock_perform_import(override=True)
        self.assertEqual(result["data"]["count"], 1)
        self.assertEqual(result["data"]["flows"], {3: "定时器1"})

    def test_no_override(self):
        result = self.mock_perform_import(override=False)
        self.assertEqual(result["data"]["count"], 1)
        self.assertEqual(result["data"]["flows"], {4: "定时器1"})

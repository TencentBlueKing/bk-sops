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

from mock import patch, MagicMock
from django.test import TestCase

from pipeline_web.plugin_management.utils import find_deprecated_plugins_in_unfold_tree
from pipeline_web.plugin_management.models import DeprecatedPlugin


class FindDeprecatedPluginInUnfoldTreeTestCase(TestCase):
    def setUp(self):
        self.deep_copy_return = "deep_copy_return"
        self.mock_copy = MagicMock(return_value=self.deep_copy_return)
        self.mock_wrapper = MagicMock()
        self.mock_find = MagicMock()
        self.mock_replace_id = MagicMock()

        self.copy_patcher = patch("pipeline_web.plugin_management.utils.copy.deepcopy", self.mock_copy)
        self.wrapper_patcher = patch(
            "pipeline_web.plugin_management.utils.PipelineTemplateWebWrapper", self.mock_wrapper
        )
        self.find_patcher = patch(
            "pipeline_web.plugin_management.utils.find_deprecated_plugins_in_spread_tree", self.mock_find
        )
        self.replace_id_patcher = patch(
            "pipeline_web.plugin_management.utils.replace_template_id", self.mock_replace_id
        )

        self.copy_patcher.start()
        self.wrapper_patcher.start()
        self.find_patcher.start()
        self.replace_id_patcher.start()

    def tearDown(self):
        self.copy_patcher.stop()
        self.wrapper_patcher.stop()
        self.find_patcher.stop()
        self.replace_id_patcher.stop()

    def test__whithout_phases_param(self):

        tree = "tree_token"
        template_model = "template_model_token"

        find_deprecated_plugins_in_unfold_tree(tree, template_model)

        self.mock_copy.assert_called_once_with(tree)
        self.mock_replace_id.assert_called_once_with(template_model, self.deep_copy_return)
        self.mock_wrapper.unfold_subprocess.assert_called_once_with(self.deep_copy_return, template_model)
        self.mock_find.assert_called_once_with(
            tree=self.deep_copy_return, phases=[DeprecatedPlugin.PLUGIN_PHASE_DEPRECATED]
        )

    def test__with_phases_param(self):

        tree = "tree_token"
        template_model = "template_model_token"

        find_deprecated_plugins_in_unfold_tree(tree, template_model, [DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED])

        self.mock_copy.assert_called_once_with(tree)
        self.mock_replace_id.assert_called_once_with(template_model, self.deep_copy_return)
        self.mock_wrapper.unfold_subprocess.assert_called_once_with(self.deep_copy_return, template_model)
        self.mock_find.assert_called_once_with(
            tree=self.deep_copy_return, phases=[DeprecatedPlugin.PLUGIN_PHASE_WILL_BE_DEPRECATED]
        )

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

import mock
from django.test import TestCase

from pipeline.models import PipelineTemplate
from pipeline.signals import handlers


class MockPipelineTemplate(object):
    def __init__(self, is_deleted):
        self.is_deleted = is_deleted
        self.set_has_subprocess_bit = mock.MagicMock()


class PipelineSignalHandlerTestCase(TestCase):
    def test_template_pre_save_handler(self):
        template_to_be_delete = MockPipelineTemplate(is_deleted=True)
        handlers.pipeline_template_pre_save_handler(sender=PipelineTemplate, instance=template_to_be_delete)
        template_to_be_delete.set_has_subprocess_bit.assert_not_called()

        template_to_be_save = MockPipelineTemplate(is_deleted=False)
        handlers.pipeline_template_pre_save_handler(sender=PipelineTemplate, instance=template_to_be_save)
        template_to_be_save.set_has_subprocess_bit.assert_called_once()

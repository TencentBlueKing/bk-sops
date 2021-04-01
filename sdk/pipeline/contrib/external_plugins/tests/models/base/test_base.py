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

from pipeline.contrib.external_plugins.models import base
from pipeline.contrib.external_plugins.tests.mock import *  # noqa
from pipeline.contrib.external_plugins.tests.mock_settings import *  # noqa


class BaseModuleTestCase(TestCase):
    def test_package_source(self):
        source_type = "source_type"

        cls_factory = {}

        with patch(MODELS_BASE_SOURCE_CLS_FACTORY, cls_factory):

            @base.package_source
            class APackageSource(object):
                @staticmethod
                def type():
                    return source_type

            self.assertIs(cls_factory[source_type], APackageSource)

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

from pipeline.contrib.external_plugins import loader
from pipeline.contrib.external_plugins.tests.mock import *  # noqa
from pipeline.contrib.external_plugins.tests.mock_settings import *  # noqa


class LoaderTestCase(TestCase):
    def test__import_modules_in_source(self):
        import_module = MagicMock()

        with patch(IMPORTLIB_IMPORT_MODULE, import_module):
            modules = [1, 2, 3, 4]
            source = MockPackageSource(importer="importer", modules=modules)
            loader._import_modules_in_source(source)
            import_module.assert_has_calls(
                calls=[call(modules[0]), call(modules[1]), call(modules[2]), call(modules[3])]
            )

    @patch(LOADER__IMPORT_MODULES_IN_SOURCE, MagicMock())
    def test_load_external_modules(self):
        cls_factory = Object()
        setattr(
            cls_factory,
            "items",
            MagicMock(
                return_value=[
                    ("type_1", MockPackageSourceClass(all=["source_1", "source_2"])),
                    ("type_2", MockPackageSourceClass(all=["source_3", "source_4"])),
                ]
            ),
        )
        with patch(LOADER_SOURCE_CLS_FACTORY, cls_factory):
            loader.load_external_modules()
            loader._import_modules_in_source.assert_has_calls(
                calls=[call("source_1"), call("source_2"), call("source_3"), call("source_4")]
            )

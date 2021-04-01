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

import sys

from django.test import TestCase

from pipeline.contrib.external_plugins.tests.mock import *  # noqa
from pipeline.contrib.external_plugins.tests.mock_settings import *  # noqa
from pipeline.contrib.external_plugins.utils.importer import GitRepoModuleImporter, utils


class UtilsTestCase(TestCase):
    @patch(SYS_META_PATH, [])
    def test__set_up_importer(self):
        utils._setup_importer("1")
        utils._setup_importer("2")

        self.assertEqual(sys.meta_path, ["2", "1"])

    def test__remove_importer(self):
        importer_1 = GitRepoModuleImporter(
            name="name", modules=["module_1"], repo_raw_url="https://url_1", branch="master"
        )
        importer_2 = GitRepoModuleImporter(
            name="name", modules=["module_2"], repo_raw_url="https://url_2", branch="master"
        )
        importer_3 = GitRepoModuleImporter(
            name="name", modules=["module_3"], repo_raw_url="https://url_3", branch="master"
        )
        importer_4 = GitRepoModuleImporter(
            name="name", modules=["module_4"], repo_raw_url="https://url_4", branch="master"
        )

        with patch(SYS_META_PATH, [importer_1, importer_2, importer_3]):
            utils._remove_importer(importer_4)
            self.assertEqual(sys.meta_path, [importer_1, importer_2, importer_3])
            utils._remove_importer(importer_1)
            self.assertEqual(sys.meta_path, [importer_2, importer_3])
            utils._remove_importer(importer_3)
            self.assertEqual(sys.meta_path, [importer_2])
            utils._remove_importer(importer_2)
            self.assertEqual(sys.meta_path, [])

    @patch(UTILS_IMPORTER__SETUP_IMPORTER, MagicMock())
    @patch(UTILS_IMPORTER__REMOVE_IMPORTER, MagicMock())
    def test_importer_context__normal(self):
        importer = "importer"
        with utils.importer_context(importer):
            pass
        utils._setup_importer.assert_called_once_with(importer)
        utils._remove_importer.assert_called_once_with(importer)

    @patch(UTILS_IMPORTER__SETUP_IMPORTER, MagicMock())
    @patch(UTILS_IMPORTER__REMOVE_IMPORTER, MagicMock())
    def test_importer_context__raise_exception(self):
        importer = "importer"

        class CustomException(Exception):
            pass

        try:
            with utils.importer_context(importer):
                raise CustomException()
        except CustomException:
            pass

        utils._setup_importer.assert_called_once_with(importer)
        utils._remove_importer.assert_called_once_with(importer)

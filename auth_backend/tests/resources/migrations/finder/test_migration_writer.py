# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

from mock.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings

from auth_backend.resources.migrations.finder import MigrationWriter
from auth_backend.constants import MIGRATION_TEMPLATE_NAME
from auth_backend.tests.mock_path import *  # noqa


class MigrationWriterTestCase(TestCase):
    def setUp(self):
        self.migration_name = 'MIGRATION_NAME_TOKEN'
        self.snapshot_name = 'SNAPSHOT_NAME_TOKEN'
        self.app_label = 'APP_LABEL_TOKEN'
        self.writer = MigrationWriter(migration_name=self.migration_name,
                                      snapshot_name=self.snapshot_name,
                                      last_migration=None,
                                      app_label=self.app_label)

    def test_filename(self):
        self.assertEqual(self.writer.filename, '%s.py' % self.writer.migration_name)

    def test_migration_dir(self):
        self.assertEqual(self.writer.migration_dir, 'auth_backend/migrations')

    def test_basedir(self):
        self.assertEqual(self.writer.basedir, os.path.join(settings.BASE_DIR, self.writer.migration_dir))

    def test_path(self):
        self.assertEqual(self.writer.path, os.path.join(self.writer.basedir, self.writer.filename))

    @patch(FINDER_OS_PATH_IS_DIR, MagicMock(return_value=False))
    @patch(FINDER_OS_PATH_IS_FILE, MagicMock(return_value=False))
    def test_write(self):
        mock_fp = MagicMock()
        mock_fp.__enter__ = MagicMock(return_value=mock_fp)
        open_fp = MagicMock()
        finder_mkdir = MagicMock()
        finder_open = MagicMock(return_value=open_fp)
        codec_open = MagicMock(return_value=mock_fp)
        render_return = 'TOKEN'
        finder_render_to_string = MagicMock(return_value=render_return)

        with patch(FINDER_OS_MK_DIR, finder_mkdir):
            with patch(FINDER_OPEN, finder_open):
                with patch(FINDER_CODECS_OPEN, codec_open):
                    with patch(FINDER_RENDER_TO_STRING, finder_render_to_string):
                        self.writer.write()

                        migration_dir = os.path.dirname(self.writer.path)

                        finder_mkdir.assert_called_once_with(migration_dir)

                        finder_open.assert_called_once_with(os.path.join(migration_dir, "__init__.py"), 'w')

                        open_fp.close.assert_called_once()

                        finder_render_to_string.assert_called_once_with(MIGRATION_TEMPLATE_NAME, {
                            'snapshot_name': self.writer.snapshot_name,
                            'app_label': self.writer.app_label,
                            'initial': True,
                            'last_migration_name': None
                        })

                        mock_fp.write.assert_called_once_with(render_return)

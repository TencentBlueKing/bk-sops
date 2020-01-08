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

from pipeline.contrib.external_plugins.models.base import GIT, S3, FILE_SYSTEM

from gcloud.tests.external_plugins.mock import *  # noqa
from gcloud.tests.external_plugins.mock_settings import *  # noqa
from gcloud.external_plugins.protocol.writers import (
    writer,
    writer_cls_factory,
    SourceWriter,
    FileSystemWriter,
    S3Writer
)


class TestSourceWriter(TestCase):
    def setUp(self):
        self.TEST_TYPE = 'TEST'

    def test_cls_factory(self):
        self.assertEquals(writer_cls_factory[FILE_SYSTEM], FileSystemWriter)
        self.assertEquals(writer_cls_factory[S3], S3Writer)
        self.assertNotIn(GIT, writer_cls_factory)

    def test_writer(self):
        @writer
        class TestWriter(SourceWriter):
            type = self.TEST_TYPE

            def write(self):
                pass

        self.assertEquals(writer_cls_factory[self.TEST_TYPE], TestWriter)
        writer_cls_factory.pop(self.TEST_TYPE)

    @patch(OS_PATH_EXISTS, MagicMock(return_value=False))
    @patch(OS_MAKEDIRS, MagicMock(return_value=True))
    @patch(SHUTIL_RMTREE, MagicMock(return_value=True))
    def test_not_implement_write_raise(self):
        with self.assertRaises(NotImplementedError):
            class ErrorWriter(SourceWriter):
                type = 'ERROR'

            ErrorWriter('/local/', MagicMock(return_value='')).write()


class TestS3Writer(TestCase):
    def setUp(self):
        self.from_path = '/local/cache/'

    @patch(OS_PATH_EXISTS, MagicMock(return_value=True))
    @patch(OS_WALK, mock_os_walk)
    def test_write(self):
        s3_writer = S3Writer(self.from_path, MagicMock(return_value=''))

        mock_s3 = MockBoto3()
        files = (
            '/local/cache/file',
            '/local/cache/first/file',
            '/local/cache/first/second/file',
        )
        with patch(GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_WRITERS_BOTO3, mock_s3):
            s3_writer.write()
            self.assertEquals(set(mock_s3.files), set(files))


class TestFileSystemWriter(TestCase):
    def setUp(self):
        self.from_path = '/local/cache/'

    @patch(OS_PATH_EXISTS, MagicMock(return_value=True))
    @patch(SHUTIL_MOVE, MagicMock(return_value=True))
    def test_write(self):
        fs_writer = FileSystemWriter(self.from_path, MagicMock(return_value=''))

        mock_shutil = MockShutil()
        with patch(GCLOUD_EXTERNAL_PLUGINS_PROTOCOL_WRITERS_SHUTIL, mock_shutil):
            fs_writer.write()
            self.assertEquals(mock_shutil.from_path, fs_writer.from_path)
            self.assertEquals(mock_shutil.to_path, fs_writer.base_source.path)

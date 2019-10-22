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
from django.core.serializers.json import DjangoJSONEncoder

from auth_backend.resources.migrations.finder import ResourceSnapshotWriter
from auth_backend.tests.mock_path import *  # noqa


class ResourceSnapshotWriterTestCase(TestCase):
    def setUp(self):
        self.snapshot_name = 'NAME_TOKEN'
        self.snapshot = 'SNAPSHOT_TOKEN'
        self.writer = ResourceSnapshotWriter(self.snapshot_name, self.snapshot)

    @patch(FINDER_OS_PATH_IS_DIR, MagicMock(return_value=False))
    def test_write(self):
        mock_fp = MagicMock()
        mock_fp.__enter__ = MagicMock(return_value=mock_fp)
        codec_open = MagicMock(return_value=mock_fp)
        json_dump = MagicMock()
        os_mkdir = MagicMock()

        with patch(FINDER_CODECS_OPEN, codec_open):
            with patch(FINDER_JSON_DUMP, json_dump):
                with patch(FINDER_OS_MK_DIR, os_mkdir):
                    self.writer.write()

                    os_mkdir.assert_called_once_with(os.path.dirname(self.writer.path))
                    json_dump.assert_called_once_with(self.snapshot,
                                                      fp=mock_fp,
                                                      cls=DjangoJSONEncoder,
                                                      ensure_ascii=False,
                                                      indent=4)

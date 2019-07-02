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
from mock import MagicMock, patch
from django.test import TestCase

from auth_backend.resources.migrations.finder import ResourceSnapshotReader
from auth_backend.tests.mock_path import *  # noqa


class ResourceSnapshotReaderTestCase(TestCase):
    def setUp(self):
        self.snapshot_name = 'TOKEN'
        self.reader = ResourceSnapshotReader(self.snapshot_name)

    def test_read(self):
        load_return = 'RETURN_TOKEN'
        mock_fp = MagicMock()
        mock_fp.__enter__ = MagicMock(return_value=mock_fp)
        codec_open = MagicMock(return_value=mock_fp)
        json_load = MagicMock(return_value=load_return)

        with patch(FINDER_CODECS_OPEN, codec_open):
            with patch(FINDER_JSON_LOAD, json_load):
                read_return = self.reader.read()

                self.assertEqual(read_return, load_return)
                json_load.assert_called_once_with(fp=mock_fp)

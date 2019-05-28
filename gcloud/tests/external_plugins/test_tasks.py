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

from django.test import TestCase

from pipeline.contrib.external_plugins.models import GIT, S3

from gcloud.tests.external_plugins.mock import *  # noqa
from gcloud.tests.external_plugins.mock_settings import *  # noqa
from gcloud.external_plugins.models import SyncTask
from gcloud.external_plugins.tasks import sync_task


class TestSyncTask(TestCase):
    def setUp(self):
        self.sync_task = SyncTask.objects.create(
            creator='user1',
            create_method='manual'
        )

    def tearDown(self):
        SyncTask.objects.all().delete()

    @patch(GCLOUD_EXTERNAL_PLUGINS_TASKS_TASK, MagicMock(return_value=True))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_GIT_ORIGINAL_PACKAGE_SOURCE_ALL,
           MagicMock(return_value=[MockWriterAndReader(name='git', id=1, type=GIT)]))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_S3_ORIGINAL_PACKAGE_SOURCE_ALL,
           MagicMock(return_value=[MockWriterAndReader(name='s3', id=1, type=S3)]))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_FS_ORIGINAL_PACKAGE_SOURCE_ALL, MagicMock(return_val=[]))
    def test_sync_task__git_and_s3_normal(self):
        with patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_CACHE_PACKAGE_SOURCE_ALL,
                   MagicMock(return_value=[MockWriterAndReader(name='cache', id=1, type=GIT)])):
            self.assertTrue(sync_task(self.sync_task.id))
        with patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_CACHE_PACKAGE_SOURCE_ALL,
                   MagicMock(return_value=[MockWriterAndReader(name='cache', id=1, type=GIT, raise_exception=True)])):
            self.assertFalse(sync_task(self.sync_task.id))

    @patch(GCLOUD_EXTERNAL_PLUGINS_TASKS_TASK, MagicMock(return_val=True))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_GIT_ORIGINAL_PACKAGE_SOURCE_ALL,
           MagicMock(return_value=[MockWriterAndReader(name='git', id=1, type=GIT)]))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_S3_ORIGINAL_PACKAGE_SOURCE_ALL,
           MagicMock(return_value=[MockWriterAndReader(name='s3', id=1, type=S3, raise_exception=True)]))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_FS_ORIGINAL_PACKAGE_SOURCE_ALL, MagicMock(return_val=[]))
    @patch(GCLOUD_EXTERNAL_PLUGINS_MODELS_GIT_ORIGINAL_PACKAGE_SOURCE_ALL, MagicMock(return_val=[]))
    def test_sync_task__git_normal_and_s3_abnormal(self):
        self.assertFalse(sync_task(self.sync_task.id))

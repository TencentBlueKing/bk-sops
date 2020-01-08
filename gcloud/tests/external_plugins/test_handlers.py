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

from gcloud.tests.external_plugins.mock import *  # noqa
from gcloud.tests.external_plugins.mock_settings import *  # noqa
from gcloud.external_plugins.models import SyncTask


class TestSignalsHandlers(TestCase):

    def test_post_save_handler(self):
        with patch(GCLOUD_EXTERNAL_PLUGINS_SYNC_TASK_DELAY, MagicMock()) as mocked_handler:
            self.sync_task = SyncTask.objects.create(
                creator='user1',
                create_method='manual'
            )
            self.assertEquals(mocked_handler.call_count, 1)

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

import factory
from django.db.models import signals
from django.test import TestCase

from gcloud.core.models import Project
from gcloud.core.permissions import project_resource
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class ProjectTestCase(TestCase):

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def tearDown(self):
        Project.objects.all().delete()

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    @patch(PROJECT_RESOURCE_BATCH_REGISTER_INSTANCE, MagicMock())
    def test_sync_project_from_cmdb_business__full_sync(self):
        businesses = {
            i: {
                'cc_name': 'biz_%s' % i,
                'time_zone': 'time_zone_%s' % i,
                'creator': 'creator_%s' % i
            } for i in range(1, 10)
        }

        Project.objects.sync_project_from_cmdb_business(businesses)

        projects = []

        for i in range(1, 10):
            proj = Project.objects.get(bk_biz_id=i)
            projects.append(proj)
            self.assertEqual(proj.name, businesses[i]['cc_name'])
            self.assertEqual(proj.time_zone, businesses[i]['time_zone'])
            self.assertEqual(proj.creator, businesses[i]['creator'])
            self.assertEqual(proj.desc, '')
            self.assertTrue(proj.from_cmdb)

        project_resource.batch_register_instance(projects)

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    @patch(PROJECT_RESOURCE_BATCH_REGISTER_INSTANCE, MagicMock())
    def test_sync_project_from_cmdb_business__partial_sync(self):
        for i in range(1, 3):
            Project.objects.create(name='biz_%s' % i,
                                   time_zone='time_zone_%s' % i,
                                   creator='creator_%s' % i,
                                   desc='',
                                   from_cmdb=True,
                                   bk_biz_id=i)

        businesses = {
            i: {
                'cc_name': 'biz_%s' % i,
                'time_zone': 'time_zone_%s' % i,
                'creator': 'creator_%s' % i
            } for i in range(1, 10)
        }

        Project.objects.sync_project_from_cmdb_business(businesses)

        for i in range(1, 10):
            proj = Project.objects.get(bk_biz_id=i)
            self.assertEqual(proj.name, businesses[i]['cc_name'])
            self.assertEqual(proj.time_zone, businesses[i]['time_zone'])
            self.assertEqual(proj.creator, businesses[i]['creator'])
            self.assertEqual(proj.desc, '')
            self.assertTrue(proj.from_cmdb)

        projects = Project.objects.filter(id__in=list(range(3, 10)))
        project_resource.batch_register_instance(projects)

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def test_sync_project_from_cmdb_business__no_business(self):
        Project.objects.sync_project_from_cmdb_business({})
        self.assertEqual(Project.objects.all().count(), 0)

    @patch(PROJECT_FILTER, MagicMock())
    def test_update_business_project_status(self):
        archived_cc_ids = 'archived_cc_ids_token'
        active_cc_ids = 'active_cc_ids_token'
        Project.objects.update_business_project_status(archived_cc_ids=archived_cc_ids, active_cc_ids=active_cc_ids)
        Project.objects.filter.assert_has_calls([call(bk_biz_id__in='archived_cc_ids_token', from_cmdb=True),
                                                 call().update(is_disable=True),
                                                 call(bk_biz_id__in='active_cc_ids_token', from_cmdb=True),
                                                 call().update(is_disable=False)])

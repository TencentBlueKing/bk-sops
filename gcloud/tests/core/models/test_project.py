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

import factory
from django.db.models import signals
from django.test import TestCase

from gcloud.core.models import Project


class ProjectTestCase(TestCase):

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def tearDown(self):
        Project.objects.all().delete()

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def test_sync_project_from_cmdb_business__full_sync(self):
        businesses = {
            i: {
                'cc_name': 'biz_%s' % i,
                'time_zone': 'time_zone_%s' % i,
                'creator': 'creator_%s' % i
            } for i in range(1, 10)
        }

        projs = Project.objects.sync_project_from_cmdb_business(businesses)
        self.assertEqual(len(projs), len(businesses))

        for i in range(1, 10):
            proj = Project.objects.get(cmdb_biz_id=i)
            self.assertEqual(proj.name, businesses[i]['cc_name'])
            self.assertEqual(proj.time_zone, businesses[i]['time_zone'])
            self.assertEqual(proj.creator, businesses[i]['creator'])
            self.assertEqual(proj.desc, '')
            self.assertTrue(proj.from_cmdb)

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def test_sync_project_from_cmdb_business__partial_sync(self):
        for i in range(1, 3):
            Project.objects.create(name='biz_%s' % i,
                                   time_zone='time_zone_%s' % i,
                                   creator='creator_%s' % i,
                                   desc='',
                                   from_cmdb=True,
                                   cmdb_biz_id=i)

        businesses = {
            i: {
                'cc_name': 'biz_%s' % i,
                'time_zone': 'time_zone_%s' % i,
                'creator': 'creator_%s' % i
            } for i in range(1, 10)
        }

        projs = Project.objects.sync_project_from_cmdb_business(businesses)
        self.assertEqual(len(projs), 7)

        for i in range(1, 10):
            proj = Project.objects.get(cmdb_biz_id=i)
            self.assertEqual(proj.name, businesses[i]['cc_name'])
            self.assertEqual(proj.time_zone, businesses[i]['time_zone'])
            self.assertEqual(proj.creator, businesses[i]['creator'])
            self.assertEqual(proj.desc, '')
            self.assertTrue(proj.from_cmdb)

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def test_sync_project_from_cmdb_business__no_business(self):
        projs = Project.objects.sync_project_from_cmdb_business({})
        self.assertEqual(len(projs), 0)
        self.assertEqual(Project.objects.all().count(), 0)

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

from gcloud.core.models import Project, UserDefaultProject


class UserDefaultProjectTestCase(TestCase):
    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def tearDown(self):
        Project.objects.all().delete()
        UserDefaultProject.objects.all().delete()

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def test_init_user_default_project__first_set(self):
        project = Project.objects.create(name='name',
                                         creator='creator',
                                         desc='', )
        dp = UserDefaultProject.objects.init_user_default_project('username', project)
        self.assertEqual(dp.default_project.id, project.id)

    @factory.django.mute_signals(signals.post_save, signals.post_delete)
    def test_init_user_default_project__second_set(self):
        project_1 = Project.objects.create(name='name',
                                           creator='creator',
                                           desc='', )
        project_2 = Project.objects.create(name='name',
                                           creator='creator',
                                           desc='', )
        UserDefaultProject.objects.init_user_default_project('username', project_1)
        dp = UserDefaultProject.objects.init_user_default_project('username', project_2)
        self.assertEqual(dp.default_project.id, project_1.id)

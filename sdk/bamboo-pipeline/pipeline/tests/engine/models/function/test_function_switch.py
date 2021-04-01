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

from django.test import TestCase

from pipeline.engine.conf import function_switch as fs
from pipeline.engine.models import FunctionSwitch

origin_switch_list = fs.switch_list


class TestFunctionSwitch(TestCase):
    def setUp(self):
        fs.switch_list = origin_switch_list
        FunctionSwitch.objects.init_db()

    def test_init_db(self):
        fs.switch_list = [
            {"name": "test_1", "description": "unit_test_switch_1", "is_active": False},
            {"name": "test_2", "description": "unit_test_switch_2", "is_active": False},
            {"name": "test_3", "description": "unit_test_switch_3", "is_active": True},
        ]
        FunctionSwitch.objects.init_db()
        for switch_config in fs.switch_list:
            switch = FunctionSwitch.objects.get(name=switch_config["name"])
            self.assertEqual(switch.name, switch_config["name"])
            self.assertEqual(switch.description, switch_config["description"])
            self.assertEqual(switch.is_active, switch_config["is_active"])

        fs.switch_list = [
            {"name": "test_1", "description": "unit_test_switch_1_1", "is_active": False},
            {"name": "test_2", "description": "unit_test_switch_2_2", "is_active": False},
            {"name": "test_3", "description": "unit_test_switch_3_3", "is_active": True},
            {"name": "test_4", "description": "unit_test_switch_3", "is_active": True},
        ]
        FunctionSwitch.objects.init_db()
        for switch_config in fs.switch_list:
            switch = FunctionSwitch.objects.get(name=switch_config["name"])
            self.assertEqual(switch.name, switch_config["name"])
            self.assertEqual(switch.description, switch_config["description"])
            self.assertEqual(switch.is_active, switch_config["is_active"])

    def test_is_frozen(self):
        FunctionSwitch.objects.filter(name=fs.FREEZE_ENGINE).update(is_active=False)
        self.assertFalse(FunctionSwitch.objects.is_frozen())
        FunctionSwitch.objects.filter(name=fs.FREEZE_ENGINE).update(is_active=True)
        self.assertTrue(FunctionSwitch.objects.is_frozen())

    def test_freeze_engine(self):
        FunctionSwitch.objects.filter(name=fs.FREEZE_ENGINE).update(is_active=False)
        FunctionSwitch.objects.freeze_engine()
        is_active = FunctionSwitch.objects.get(name=fs.FREEZE_ENGINE).is_active
        self.assertTrue(is_active)

    def test_unfreeze_engine(self):
        FunctionSwitch.objects.filter(name=fs.FREEZE_ENGINE).update(is_active=True)
        FunctionSwitch.objects.unfreeze_engine()
        is_active = FunctionSwitch.objects.get(name=fs.FREEZE_ENGINE).is_active
        self.assertFalse(is_active)

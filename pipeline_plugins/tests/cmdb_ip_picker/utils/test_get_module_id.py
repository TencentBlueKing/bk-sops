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

from pipeline_plugins.cmdb_ip_picker.utils import get_modules_id


class GetModuleIDTestCase(TestCase):
    def test__normal(self):
        modules = [
            {"default": 0, "bk_obj_name": "模块", "bk_obj_id": "module", "bk_inst_id": 8, "bk_inst_name": "test1"},
            {"default": 0, "bk_obj_name": "模块", "bk_obj_id": "module", "bk_inst_id": 9, "bk_inst_name": "test2"},
        ]
        self.assertEqual(get_modules_id(modules), [8, 9])

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

from mock import patch
from django.test import TestCase

from files.factory import ManagerFactory


class EnvPatcher:
    def __init__(self, not_exist_var):
        self.not_exist_var = not_exist_var

    def __getattribute__(self, attr):
        if super(EnvPatcher, self).__getattribute__("not_exist_var") == attr:
            return None
        return attr


class ManagerFactoryTestCase(TestCase):
    def test_get_not_exist_manager(self):
        self.assertRaises(LookupError, ManagerFactory.get_manager, "not_exist_type")

    def test_get_nfs_manager__config_err(self):
        for lack_var in [
            "BKAPP_NFS_CONTAINER_ROOT",
            "BKAPP_NFS_HOST_ROOT",
        ]:
            with patch("files.factory.env", EnvPatcher(lack_var)):
                self.assertRaises(EnvironmentError, ManagerFactory.get_manager, "host_nfs")

    @patch("files.factory.env", EnvPatcher(None))
    def test_get_nfs_manager(self):
        manager = ManagerFactory.get_manager("host_nfs")
        self.assertEqual(manager.location, "BKAPP_NFS_CONTAINER_ROOT")
        self.assertEqual(manager.server_location, "BKAPP_NFS_HOST_ROOT")

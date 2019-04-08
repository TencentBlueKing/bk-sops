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
from django.conf import settings
from blueapps.utils import esbclient

from pipeline_plugins.components import utils
from pipeline_plugins.tests.utils import mock_get_client_by_user
from pipeline_plugins.tests.utils import host_list_data

return_success = True


class TestUtils(TestCase):
    def setUp(self):
        self.run_ver = settings.OPEN_VER
        self.app_code = settings.APP_CODE
        self.get_client_by_user = esbclient.get_client_by_user

        setattr(settings, 'OPEN_VER', 'TEST')
        setattr(settings, 'APP_CODE', 'APP_CODE')
        utils.get_client_v1_by_user = mock_get_client_by_user

    def tearDown(self):
        setattr(settings, 'APP_CODE', self.app_code)
        setattr(settings, 'OPEN_VER', self.run_ver)
        utils.get_client_v1_by_user = self.get_client_by_user

    def test_get_ip_by_regex(self):
        self.assertEqual(utils.get_ip_by_regex('1.1.1.1,2.2.2.2,3.3.3.3'), ['1.1.1.1',
                                                                            '2.2.2.2',
                                                                            '3.3.3.3'])

    def test_local_file_path_of_time(self):
        self.assertEqual(utils.get_local_file_path_of_time(biz_cc_id=789, time_str='time_str'),
                         '/data/TEST_UPLOAD_TEST/APP_CODE/bkupload/789/time_str/')

    def test_cc_get_inner_ip_by_module_id(self):
        mock_get_client_by_user.success = True
        self.assertEqual(utils.cc_get_inner_ip_by_module_id(username='test', biz_cc_id=789, module_id_list=[]),
                         [{
                             'host': {
                                 'bk_host_innerip': '1.0.0.1',
                                 'bk_host_outerip': '1.0.0.1',
                                 'bk_host_name': '1.0.0.1',
                                 'bk_host_id': 1,
                                 'bk_cloud_id': {
                                     'bk_obj_name': '',
                                     'id': '0',
                                     'bk_obj_id': 'plat',
                                     'bk_obj_icon': '',
                                     'bk_inst_id': 0,
                                     'bk_inst_name': 'default area'
                                 }
                             },
                             'module': [
                                 {
                                     'bk_module_id': 2,
                                     'bk_module_name': 'test2'
                                 }
                             ]
                         }]
                         )
        mock_get_client_by_user.success = False
        self.assertEqual(utils.cc_get_inner_ip_by_module_id(username='test', biz_cc_id=789, module_id_list=[]), [])

    def test_cc_get_set_ids_by_names(self):
        mock_get_client_by_user.success = True
        self.assertEqual(utils.cc_get_set_ids_by_names(username='test', biz_cc_id=789, set_names=['name1', 'name2']),
                         ['1', '2'])
        self.assertEqual(utils.cc_get_set_ids_by_names(username='test', biz_cc_id=789, set_names=['name1', 'name3']),
                         ['1'])
        self.assertEqual(utils.cc_get_set_ids_by_names(username='test', biz_cc_id=789, set_names='name1'), '1')
        self.assertEqual(utils.cc_get_set_ids_by_names(username='test', biz_cc_id=789, set_names='name3'), '')
        mock_get_client_by_user.success = False
        self.assertEqual(utils.cc_get_set_ids_by_names(username='test', biz_cc_id=789, set_names=['name1', 'name2']),
                         [])
        self.assertEqual(utils.cc_get_set_ids_by_names(username='test', biz_cc_id=789, set_names='name1'), '')

    def test_cc_get_ips_by_set_and_module(self):
        mock_get_client_by_user.success = True
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=[],
                                                            set_name_list=[],
                                                            module_name_list=['1']), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=None,
                                                            set_name_list=None,
                                                            module_name_list=['1']), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['1'],
                                                            set_name_list=['1'],
                                                            module_name_list=[]), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['1'],
                                                            set_name_list=['1'],
                                                            module_name_list=None), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['0'],
                                                            set_name_list=['all'],
                                                            module_name_list=['all']), 'data')
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=[],
                                                            set_name_list=['name3'],
                                                            module_name_list=['all']), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['1'],
                                                            set_name_list=['name3'],
                                                            module_name_list=['all']), 'data')
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['1'],
                                                            set_name_list=['name1'],
                                                            module_name_list=['module_name']), 'data')
        mock_get_client_by_user.success = False
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['0'],
                                                            set_name_list=['all'],
                                                            module_name_list=['all']), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['name3'],
                                                            set_name_list=['all'],
                                                            module_name_list=['all']), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['name1'],
                                                            set_name_list=['all'],
                                                            module_name_list=['all']), [])
        self.assertEqual(utils.cc_get_ips_by_set_and_module(username='test',
                                                            biz_cc_id=789,
                                                            set_id_list=['name1'],
                                                            set_name_list=['all'],
                                                            module_name_list=['module_name']), [])

    def test_cc_get_role_users(self):
        mock_get_client_by_user.success = True
        self.assertEqual(utils.cc_get_role_users(username='test',
                                                 biz_cc_id=789,
                                                 user_roles=['role1', 'role2'],
                                                 more_users='')['data'], list({'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}))
        self.assertEqual(utils.cc_get_role_users(username='test',
                                                 biz_cc_id=789,
                                                 user_roles=['role1', 'role3'],
                                                 more_users='')['data'], list({'a', 'b', 'c', 'd'}))
        self.assertEqual(utils.cc_get_role_users(username='test',
                                                 biz_cc_id=789,
                                                 user_roles=['role3'],
                                                 more_users='')['data'], [])
        mock_get_client_by_user.success = False
        self.assertEqual(utils.cc_get_role_users(username='test',
                                                 biz_cc_id=789,
                                                 user_roles=['role1', 'role2'],
                                                 more_users='')['data'], [])
        self.assertEqual(utils.cc_get_role_users(username='test',
                                                 biz_cc_id=789,
                                                 user_roles=['role1', 'role2'],
                                                 more_users='')['result'], False)

    def test_cc_get_ip_list_by_biz_and_user(self):
        mock_get_client_by_user.success = True
        self.assertEqual(utils.cc_get_ip_list_by_biz_and_user(username='test', biz_cc_id=789), host_list_data)
        mock_get_client_by_user.success = False
        self.assertEqual(utils.cc_get_ip_list_by_biz_and_user(username='test', biz_cc_id=790), [])

    def test_cc_get_ips_info_by_str(self):
        mock_get_client_by_user.success = True
        ip_result = host_list_data
        r1 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=789,
                                          ip_str='1.1.1.1, 2.2.2.2')
        r2 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=790,
                                          ip_str='1.1.1.1, 2.2.2.2, 3.3.3.3')
        r3 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=791,
                                          ip_str='SetName1|ModuleName1|1.1.1.1, '
                                                 'SetName2|ModuleName2|2.2.2.2, '
                                                 'set|module|3.3.3.3')
        r4 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=792,
                                          ip_str='Source1:1.1.1.1, Source2:2.2.2.2, 3:3.3.3.3')
        self.assertEqual(r1['ip_result'], ip_result)
        self.assertEqual(r1['invalid_ip'], [])
        self.assertEqual(r2['ip_result'], ip_result)
        self.assertEqual(r2['invalid_ip'], ['3.3.3.3'])
        self.assertEqual(r3['ip_result'], ip_result)
        self.assertEqual(r3['invalid_ip'], ['3.3.3.3'])
        self.assertEqual(r4['ip_result'], ip_result)
        self.assertEqual(r4['invalid_ip'], ['3.3.3.3'])
        mock_get_client_by_user.success = False
        r5 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=793,
                                          ip_str='1.1.1.1, 2.2.2.2, 3.3.3.3')
        r6 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=794,
                                          ip_str='SetName1|ModuleName1|1.1.1.1, '
                                                 'SetName2|ModuleName2|2.2.2.2, '
                                                 'set|module|3.3.3.3')
        r7 = utils.cc_get_ips_info_by_str(username='test',
                                          biz_cc_id=795,
                                          ip_str='Source1:1.1.1.1, Source2:2.2.2.2, 3:3.3.3.3')
        self.assertEqual(r5['ip_result'], [])
        self.assertEqual(r6['ip_result'], [])
        self.assertEqual(r7['ip_result'], [])

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
host_list_data = [
    {
        'InnerIP': '1.1.1.1',
        'HostID': 'Host1',
        'Source': 'Source1',
        'SetID': 'Set1',
        'SetName': 'SetName1',
        'ModuleID': 'ModuleID1',
        'ModuleName': 'ModuleName1',
    },
    {
        'InnerIP': '2.2.2.2',
        'HostID': 'Host2',
        'Source': 'Source2',
        'SetID': 'SetID2',
        'SetName': 'SetName2',
        'ModuleID': 'ModuleID2',
        'ModuleName': 'ModuleName2',
    }
]


def mock_get_client_by_user(username):

    class MockCC(object):

        def __init__(self, success):
            self.success = success

        def create_set(self, kwargs):
            return {
                'result': self.success,
                'data': {'bk_set_id': 1},
                'message': 'error'
            }

        def update_set(self, kwargs):
            return {
                'result': self.success,
                'data': {},
                'message': 'error'
            }

        def batch_delete_set(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def transfer_sethost_to_idle_module(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def update_module(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def search_biz_inst_topo(self, kwargs):
            return {
                'result': self.success,
                'data': [
                    {
                        "default": 0,
                        "bk_obj_name": u"业务",
                        "bk_obj_id": "biz",
                        "child": [
                            {
                                "default": 0,
                                "bk_obj_name": u"集群",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "default": 0,
                                        "bk_obj_name": u"模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 5,
                                        "bk_inst_name": "test1"
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": u"模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 6,
                                        "bk_inst_name": "test2"
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": u"模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 7,
                                        "bk_inst_name": "test3"
                                    },
                                ],
                                "bk_inst_id": 3,
                                "bk_inst_name": "set2"
                            },
                            {
                                "default": 0,
                                "bk_obj_name": u"集群",
                                "bk_obj_id": "set",
                                "child": [
                                    {
                                        "default": 0,
                                        "bk_obj_name": u"模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 8,
                                        "bk_inst_name": "test1"
                                    },
                                    {
                                        "default": 0,
                                        "bk_obj_name": u"模块",
                                        "bk_obj_id": "module",
                                        "bk_inst_id": 9,
                                        "bk_inst_name": "test2"
                                    },
                                ],
                                "bk_inst_id": 4,
                                "bk_inst_name": "set3"
                            },
                        ],
                        "bk_inst_id": 2,
                        "bk_inst_name": u"蓝鲸"
                    }
                ],
                'message': 'error'
            }

        def get_biz_internal_module(self, kwargs):
            return {
                'result': self.success,
                'data': {
                    'bk_set_id': 2,
                    'bk_set_name': u'空闲机池',
                    'module': [

                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_module_id": 3,
                            "bk_obj_name": u"模块",
                            "bk_module_name": u"空闲机"
                        },
                        {
                            "default": 1,
                            "bk_obj_id": "module",
                            "bk_module_id": 4,
                            "bk_obj_name": u"模块",
                            "bk_module_name": u"故障机"
                        }
                    ],
                },
                'message': 'error'
            }

        def update_host(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def transfer_host_module(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def clone_host_property(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def transfer_host_to_faultmodule(self, kwargs):
            return {
                'result': self.success,
                'message': 'error'
            }

        def search_host(self, kwargs):
            return {
                'result': self.success,
                'data': {
                    'info': [
                        {
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
                        },
                    ]
                },
                'message': 'error'
            }

        def get_sets_by_property(self, kwargs):
            return {
                'result': self.success,
                'data': [
                    {
                        'SetName': 'name1',
                        'SetID': '1'
                    },
                    {
                        'SetName': 'name2',
                        'SetID': '2'
                    }
                ],
                'message': 'error'
            }

        def get_hosts_by_property(self, kwargs):
            return {
                'result': self.success,
                'data': 'data',
                'message': 'error'
            }

        def get_app_by_id(self, kwargs):
            return {
                'result': self.success,
                'data': [
                    {
                        'role1': 'a,b,c,d',
                        'role2': 'e;f;g;h'
                    }
                ],
                'message': 'get_app_by_id_message'
            }

        def get_app_host_list(self, kwargs):
            return {
                'result': self.success,
                'data': host_list_data
            }

    class MockJOB(object):
        def __init__(self, success):
            self.success = success
            self.result = {
                'result': self.success,
                'data': {
                    'job_instance_id': 1,
                    'job_instance_name': 'xx',
                },
                'message': 'error'
            }

        def execute_job(self, kwargs):
            return self.result

        def fast_push_file(self, kwargs):
            return self.result

        def fast_execute_script(self, kwargs):
            return self.result

    class MockCMSI(object):
        def __init__(self, success):
            self.success = success
            self.result = {
                'result': self.success,
                'code': 0,
                'message': 'error'
            }

        def send_weixin(self, kwargs):
            return self.result

        def send_mail(self, kwargs):
            return self.result

        def send_sms(self, kwargs):
            return self.result

    class MockGSE(object):
        def __init__(self, success):
            self.success = success
            self.result = {
                'result': self.success,
                'code': 0,
                'message': 'error'
            }

        def get_agent_status(self, kwargs):
            return {
                'result': self.success,
                'data': {
                    '0:3.3.3.3': {
                        'ip': '3.3.3.3',
                        'bk_cloud_id': 0,
                        'bk_agent_alive': 1
                    }
                },
                'message': 'error'
            }

    class MockUser(object):
        def __init__(self, username):
            self.username = username

    class MockClient(object):
        def __init__(self, success):
            self.ver = None
            self.cc = MockCC(success)
            self.job = MockJOB(success)
            self.cmsi = MockCMSI(success)
            self.gse = MockGSE(success)
            self.user = MockUser('admin')

        def set_bk_api_ver(self, ver):
            self.ver = ver

    return MockClient(mock_get_client_by_user.success)


mock_get_client_by_request = mock_get_client_by_user

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
from mock import patch

from packages.blueking.component.client import BaseComponentClient
from pipeline_plugins.components.collections.sites.open.monitor import (
    AlarmShieldDisableComponent, AlarmShieldScopeComponent,
    AlarmShieldStrategyComponent)


class Data(object):
    def __init__(self, scope=None):
        self.scope = scope

    def get_one_of_inputs(self, param):
        ret_map = {
            'biz_cc_id': 2,
            'executor': 'admin',
            'language': None,
            'bk_alarm_shield_info': {
                'bk_alarm_shield_scope': self.scope,
                'bk_alarm_shield_business': 2,
                'bk_alarm_shield_node': ['module_21', 'module_23'],
                'bk_alarm_shield_IP': '10.0.0.1,10.0.0.2'
            },
            'bk_alarm_shield_target': [1, 2, 3],
            'bk_alarm_shield_id': 1,
            'bk_alarm_shield_id_input': 1,
            'bk_alarm_shield_strategy': 29,
            'bk_alarm_shield_begin_time': "2019-11-04 00:00:00",
            'bk_alarm_shield_end_time': "2019-11-05 00:00:00",
            'bk_alarm_shield_strategy_begin_time': "2019-11-04 00:00:00",
            'bbk_alarm_shield_strategy_end_time': "2019-11-05 00:00:00"
        }
        return ret_map[param]

    @staticmethod
    def set_outputs(*args):
        pass


class Response(object):
    def __init__(self, data):
        self.status_code = 200
        self.data = data

    def json(self):
        return self.data


class TestAlarmShield(TestCase):
    def setUp(self):
        pass

    @patch.object(BaseComponentClient, 'request')
    def test_scope(self, mock_request):
        mock_request.return_value = Response(
            {'result': True, 'data': {'id': 1, 'message': 'success'}, 'code': 200,
             'message': 'success'})
        data = Data('business')
        ret = AlarmShieldScopeComponent.bound_service().execute(data, data)
        self.assertEqual(True, ret)

    @patch.object(BaseComponentClient, 'request')
    def test_node(self, mock_request):
        mock_request.return_value = Response(
            {'result': True, 'data': {'id': 1, 'message': 'success'}, 'code': 200, 'message': 'success'})
        data = Data('node')
        ret = AlarmShieldScopeComponent.bound_service().execute(data, data)
        self.assertEqual(True, ret)

    @patch.object(BaseComponentClient, 'request')
    def test_ip(self, mock_request):
        host_detail = {"message": "OK",
                       "code": 200,
                       "data": {'info': [{'host': {'bk_host_id': 2, 'bk_host_innerip': '10.0.1.11',
                                                   'bk_cloud_id': [{'id': '0', 'bk_inst_id': 0, }],
                                                   'bk_supplier_account': '0'},
                                          'biz': [{'bk_biz_id': 2, 'bk_supplier_account': '0', 'bk_supplier_id': 0}]}]},
                       "result": True}
        mock_request.side_effect = [
            Response(host_detail),
            Response({'result': True, 'data': {'id': 1, 'message': 'success'}, 'code': 200, 'message': 'success'}),

        ]
        data = Data('IP')
        ret = AlarmShieldScopeComponent.bound_service().execute(data, data)
        self.assertEqual(True, ret)

    @patch.object(BaseComponentClient, 'request')
    def test_strategy(self, mock_request):
        strategy_detail = {"message": "OK", "code": 200, "data": {"item_list": [{"level": [2, 3]}], 'id': 1},
                           "result": True}
        mock_request.side_effect = [
            Response(strategy_detail),
            Response({'result': True, 'data': {'id': 1, 'message': 'success'}, 'code': 200, 'message': 'success'}),
        ]
        data = Data('strategy')
        ret = AlarmShieldStrategyComponent.bound_service().execute(data, data)
        self.assertEqual(True, ret)

    @patch.object(BaseComponentClient, 'request')
    def test_disable(self, mock_request):
        mock_request.return_value = Response({'result': True, 'data': {'id': 1}, 'code': 200, 'message': 'success'})
        data = Data()
        ret = AlarmShieldDisableComponent.bound_service().execute(data, data)
        self.assertEqual(True, ret)

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

from abc import abstractmethod
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from packages.blueking.component.shortcuts import get_client_by_user
from pipeline.component_framework.component import Component
from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ObjectItemSchema
from gcloud.utils.handlers import handle_api_error

__group_name__ = _(u"蓝鲸监控(BK)")

monitor_handle_api_error = partial(handle_api_error, __group_name__)

SCOPE = {
    'business': 'bk_alarm_shield_business',
    'IP': 'bk_alarm_shield_IP',
    'node': 'bk_alarm_shield_node'
}


class AlarmShieldService(Service):
    def __init__(self, *args, **kwargs):
        super(AlarmShieldService, self).__init__(*args, **kwargs)

    @abstractmethod
    def execute(self, data, parent_data):
        pass

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'屏蔽Id'),
                            key='shield_id',
                            type='string',
                            schema=StringItemSchema(description=_('创建的告警屏蔽 ID'))),
            self.OutputItem(name=_(u'详情'),
                            key='message',
                            type='string',
                            schema=StringItemSchema(description=_('创建的告警屏蔽详情')))
        ]

    def get_request_body(self, bk_biz_id, begin_time, end_time, shied_type, shied_value, client):
        category_map = {
            'business': 'scope',
            'IP': 'scope',
            'node': 'scope',
            'strategy': 'strategy'
        }
        dimension_config = self.get_dimension_config(shied_type, shied_value, bk_biz_id, client)
        request_body = {'begin_time': begin_time,
                        'bk_biz_id': bk_biz_id,
                        'category': category_map[shied_type],
                        'cycle_config': {'begin_time': "", 'end_time': "", 'day_list': [], 'week_list': [], 'type': 1},
                        'description': "shield by bk_sops",
                        'dimension_config': dimension_config,
                        'end_time': end_time,
                        'notice_config': {},
                        'shield_notice': False,
                        'source': settings.APP_ID}
        return request_body

    def send_request(self, request_body, data, client):
        response = client.monitor.create_shield(request_body)
        if not response['result']:
            message = monitor_handle_api_error('monitor.create_shield', request_body, response)
            self.logger.error(message)
            shield_id = ''
            ret_flag = False
        else:
            shield_id = response['data']['id']
            ret_flag = True
            message = response['message']
        data.set_outputs('shield_id', shield_id)
        data.set_outputs('message', message)
        return ret_flag

    def get_dimension_config(self, shied_type, shied_value, bk_biz_id, client):
        pass


class AlarmShieldScopeService(AlarmShieldService):

    def inputs_format(self):
        return [self.InputItem(name=_('屏蔽范围类型'),
                               key='bk_alarm_shield_info',
                               type='object',
                               schema=ObjectItemSchema(description=_(u'屏蔽范围类型'),
                                                       property_schemas={})),
                self.InputItem(name=_('策略 ID'),
                               key='bk_alarm_shield_target',
                               type='string',
                               schema=StringItemSchema(description=_('需要执行屏蔽的指标'))),
                self.InputItem(name=_('屏蔽开始时间'),
                               key='bk_alarm_shield_begin_time',
                               type='string',
                               schema=StringItemSchema(description=_('开始屏蔽的时间'))),
                self.InputItem(name=_('屏蔽结束时间'),
                               key='bk_alarm_shield_end_time',
                               type='string',
                               schema=StringItemSchema(description=_('结束屏蔽的时间'))),
                ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        bk_biz_id = parent_data.get_one_of_inputs('biz_cc_id')
        executor = parent_data.get_one_of_inputs('executor')
        client = get_client_by_user(executor)
        combine = data.get_one_of_inputs('bk_alarm_shield_info')
        scope_type = combine.get('bk_alarm_shield_scope')
        scope_value = combine.get(SCOPE[scope_type])
        target = data.get_one_of_inputs('bk_alarm_shield_target')
        begin_time = data.get_one_of_inputs('bk_alarm_shield_begin_time')
        end_time = data.get_one_of_inputs('bk_alarm_shield_end_time')

        request_body = self.get_request_body(bk_biz_id, begin_time, end_time, scope_type, scope_value, client)
        if 'all' not in target:
            request_body['dimension_config'].update({'metric_id': target})

        result_flag = self.send_request(request_body, data, client)

        return result_flag

    def get_dimension_config(self, shied_type, shied_value, bk_biz_id, client):
        dimension_map = {'business': self.get_biz_dimension,
                         'IP': self.get_ip_dimension,
                         'node': self.get_node_dimension}
        return dimension_map[shied_type](shied_value, bk_biz_id, client)

    @staticmethod
    def get_biz_dimension(scope_value, bk_biz_id, client):
        return {'scope_type': "biz"}

    @staticmethod
    def get_node_dimension(scope_value, bk_biz_id, client):
        target = [{'bk_obj_id': node.split('_')[0],
                   'bk_inst_id': node.split('_')[1]}
                  for node in scope_value]
        return {'scope_type': "node", 'target': target}

    def get_ip_dimension(self, scope_value, bk_biz_id, client):
        ip_list = scope_value.split(',')
        request_body = {
            'ip': {
                'exact': 1,
                'flag': 'bk_host_innerip',
                'data': ip_list
            }, 'condition': [{
                'bk_obj_id': 'biz',
                'fields': [],
                'condition': [{
                    'operator': '$in',
                    'field': 'bk_biz_id',
                    'value': [bk_biz_id]
                }]
            }]
        }
        response = client.cc.search_host(request_body)
        if not response['result']:
            message = monitor_handle_api_error('cc.search_host', request_body, response)
            self.logger.error(message)
            raise message
        target = []
        response_data = response['data']["info"]

        for ip_detail in response_data:
            bk_supplier_id = ip_detail['biz'][0]['bk_supplier_id']
            for bk_cloud_id in ip_detail["host"]["bk_cloud_id"]:
                target.append({
                    'ip': ip_detail["host"]['bk_host_innerip'],
                    'bk_cloud_id': bk_cloud_id["bk_inst_id"],
                    'bk_supplier_id': bk_supplier_id
                })
        return {'scope_type': "ip", 'target': target}


class AlarmShieldStrategyService(AlarmShieldService):

    def inputs_format(self):
        return [self.InputItem(name=_('策略 ID'),
                               key='bk_alarm_shield_strategy',
                               type='string',
                               schema=StringItemSchema(description=_('需要执行屏蔽的策略 ID'))),
                self.InputItem(name=_('屏蔽开始时间'),
                               key='bk_alarm_shield_strategy_begin_time',
                               type='string',
                               schema=StringItemSchema(description=_('开始屏蔽的时间'))),
                self.InputItem(name=_('屏蔽结束时间'),
                               key='bk_alarm_shield_strategy_end_time',
                               type='string',
                               schema=StringItemSchema(description=_('结束屏蔽的时间'))),
                ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        bk_biz_id = parent_data.get_one_of_inputs('biz_cc_id')
        executor = parent_data.get_one_of_inputs('executor')
        client = get_client_by_user(executor)
        strategy = data.get_one_of_inputs('bk_alarm_shield_strategy')
        begin_time = data.get_one_of_inputs('bk_alarm_shield_strategy_begin_time')
        end_time = data.get_one_of_inputs('bk_alarm_shield_strategy_end_time')

        request_body = self.get_request_body(bk_biz_id, begin_time, end_time, 'strategy', strategy, client)

        result_flag = self.send_request(request_body, data, client)

        return result_flag

    def get_dimension_config(self, shied_type, shied_value, bk_biz_id, client):
        return {'id': shied_value}


class AlarmShieldDisableService(Service):

    def inputs_format(self):
        return [self.InputItem(name=_('屏蔽 ID'),
                               key='bk_alarm_shield_id_input',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作的屏蔽 ID')))
                ]

    def execute(self, data, parent_data):
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        executor = parent_data.get_one_of_inputs('executor')
        bk_biz_id = parent_data.get_one_of_inputs('biz_cc_id')
        shield_id = data.get_one_of_inputs('bk_alarm_shield_id_input')

        client = get_client_by_user(executor)
        request_body = {'bk_biz_id': bk_biz_id, 'id': shield_id}
        response = client.monitor.disable_shield(request_body)
        if not response['result']:
            message = monitor_handle_api_error('monitor.disable_shield', request_body, response)
            self.logger.error(message)
            result = message
            ret_flag = False
        else:
            result = response['data']
            ret_flag = True

        data.set_outputs('data', {'result': result})
        data.set_outputs('status_code', response['code'])
        return ret_flag

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'响应内容'),
                            key='data',
                            type='str',
                            schema=StringItemSchema(description=_('解除告警屏蔽的响应内容'))),
            self.OutputItem(name=_(u'状态码'),
                            key='status_code',
                            type='int',
                            schema=StringItemSchema(description=_('解除告警屏蔽的响应状态码')))
        ]


class AlarmShieldScopeComponent(Component):
    name = _(u'创建告警屏蔽(按范围)')
    code = 'alarm_shield_scope'
    desc = _(u"提示: 请在告警屏蔽解除")
    bound_service = AlarmShieldScopeService
    form = settings.STATIC_URL + 'components/atoms/monitor/shield_by_scope.js'


class AlarmShieldStrategyComponent(Component):
    name = _(u'创建告警屏蔽(按策略)')
    code = 'alarm_shield_strategy'
    desc = _(u"提示: 请在告警屏蔽解除")
    bound_service = AlarmShieldStrategyService
    form = settings.STATIC_URL + 'components/atoms/monitor/shield_by_strategy.js'


class AlarmShieldDisableComponent(Component):
    name = _(u'解除告警屏蔽')
    code = 'alarm_shield_disable'
    desc = _(u"提示: 屏蔽id请从告警屏蔽或蓝鲸监控获取")
    bound_service = AlarmShieldDisableService
    form = settings.STATIC_URL + 'components/atoms/monitor/shield_disable.js'

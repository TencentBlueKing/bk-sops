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

import logging
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.utils import get_ip_by_regex
from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCReplaceFaultMachineService(Service):

    def inputs_format(self):
        return [
            self.InputItem(name=_('业务 ID'),
                           key='biz_cc_id',
                           type='string',
                           schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
            self.InputItem(name=_('主机替换信息'),
                           key='cc_host_replace_detail',
                           type='object',
                           schema=ArrayItemSchema(description=_('主机替换信息'),
                                                  item_schema=ObjectItemSchema(
                                                      description=_('替换机与被替换机信息'),
                                                      property_schemas={
                                                          'cc_fault_ip': StringItemSchema(
                                                              description=_('故障机 内网IP')),
                                                          'cc_new_ip': StringItemSchema(
                                                              description=_('替换机 内网IP'))
                                                      })))]

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        biz_cc_id = data.get_one_of_inputs('biz_cc_id', parent_data.inputs.biz_cc_id)
        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_hosts = data.get_one_of_inputs('cc_host_replace_detail')

        # 查询主机可编辑属性
        search_attr_kwargs = {
            'bk_obj_id': 'host',
            'bk_supplier_account': supplier_account
        }
        search_attr_result = client.cc.search_object_attribute(search_attr_kwargs)
        if not search_attr_result['result']:
            message = cc_handle_api_error('cc.search_object_attribute', search_attr_kwargs, search_attr_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        editable_attrs = []
        for item in search_attr_result['data']:
            if item['editable']:
                editable_attrs.append(item['bk_property_id'])

        # 拉取所有主机信息
        search_kwargs = {
            'bk_biz_id': biz_cc_id,
            'bk_supplier_account': supplier_account,
            'condition': [{
                'bk_obj_id': 'module',
                'fields': ['bk_module_id'],
                'condition': []
            }]
        }
        fault_replace_ip_map = {}
        for item in cc_hosts:
            fault_replace_ip_map[''.join(get_ip_by_regex(item['cc_fault_ip']))] = ''.join(
                get_ip_by_regex(item['cc_new_ip']))

        all_hosts = []
        all_hosts.extend(list(fault_replace_ip_map.keys()))
        all_hosts.extend(list(fault_replace_ip_map.values()))
        search_kwargs['ip'] = {
            'data': all_hosts,
            'exact': 1,
            'flag': 'bk_host_innerip'
        }

        hosts_result = client.cc.search_host(search_kwargs)

        if not hosts_result['result']:
            message = cc_handle_api_error('cc.search_host', search_attr_kwargs, hosts_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        # 更新替换机信息

        batch_update_kwargs = {
            'bk_obj_id': 'host',
            'bk_supplier_account': supplier_account,
            'update': []
        }

        host_dict = {host_info['host']['bk_host_innerip']: host_info['host'] for host_info in
                     hosts_result['data']['info']}
        host_id_to_ip = {host_info['host']['bk_host_id']: host_info['host']['bk_host_innerip'] for host_info in
                         hosts_result['data']['info']}
        fault_replace_id_map = {}

        for fault_ip, new_ip in list(fault_replace_ip_map.items()):
            fault_host = host_dict.get(fault_ip)
            new_host = host_dict.get(new_ip)

            if not fault_host:
                data.outputs.ex_data = _("无法查询到 %s 机器信息，请确认该机器是否在当前业务下") % fault_ip
                return False

            if not new_host:
                data.outputs.ex_data = _("无法查询到 %s 机器信息，请确认该机器是否在当前业务下") % new_ip
                return False

            update_item = {
                'properties': {},
                'bk_host_id': new_host['bk_host_id']
            }
            for attr in [attr for attr in editable_attrs if attr in fault_host]:
                update_item['properties'][attr] = fault_host[attr]

            batch_update_kwargs['update'].append(update_item)
            fault_replace_id_map[fault_host['bk_host_id']] = new_host['bk_host_id']

        update_result = client.cc.batch_update_host(batch_update_kwargs)

        if not update_result['result']:
            message = cc_handle_api_error('cc.batch_update_host', batch_update_kwargs, update_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        # 将主机上交至故障机模块
        fault_transfer_kwargs = {
            'bk_supplier_account': supplier_account,
            'bk_biz_id': biz_cc_id,
            'bk_host_id': list(fault_replace_id_map.keys())
        }
        fault_transfer_result = client.cc.transfer_host_to_faultmodule(fault_transfer_kwargs)
        if not fault_transfer_result['result']:
            message = cc_handle_api_error('cc.transfer_host_to_faultmodule',
                                          fault_transfer_kwargs,
                                          fault_transfer_result)
            self.logger.error(message)
            data.set_outputs('ex_data', message)
            return False

        # 转移主机模块
        transfer_kwargs_list = []
        for host_info in hosts_result['data']['info']:
            new_host_id = fault_replace_id_map.get(host_info['host']['bk_host_id'])

            if new_host_id:
                transfer_kwargs_list.append({
                    'bk_biz_id': biz_cc_id,
                    'bk_supplier_account': supplier_account,
                    'bk_host_id': [new_host_id],
                    'bk_module_id': [module_info['bk_module_id'] for module_info in host_info['module']],
                    'is_increment': True
                })

        success = []
        for kwargs in transfer_kwargs_list:
            transfer_result = client.cc.transfer_host_module(kwargs)
            if not transfer_result['result']:
                message = cc_handle_api_error('cc.transfer_host_module', kwargs, transfer_result)
                self.logger.error(message)
                data.outputs.ex_data = "{msg}\n{success}".format(
                    msg=message,
                    success=_("成功替换的机器: %s") % ','.join(success))
                return False

            success.append(host_id_to_ip[kwargs['bk_host_id'][0]])


class CCReplaceFaultMachineComponent(Component):
    name = _("故障机替换")
    code = 'cc_replace_fault_machine'
    bound_service = CCReplaceFaultMachineService
    form = '%scomponents/atoms/cc/cc_replace_fault_machine.js' % settings.STATIC_URL

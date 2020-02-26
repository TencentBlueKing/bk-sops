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
import traceback

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import get_ip_by_regex, handle_api_error
from gcloud.conf import settings

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _(u"配置平台(CMDB)")
__group_icon__ = '%scomponents/atoms/cc/cc.png' % settings.STATIC_URL


def cc_handle_api_error(api_name, params, error):
    message = handle_api_error(__group_name__, api_name, params, error)
    return message


def cc_get_host_id_by_innerip(executor, bk_biz_id, ip_list, supplier_account):
    """
    获取主机ID
    :param executor:
    :param bk_biz_id:
    :param ip_list:
    :return: [1, 2, 3] id列表
    """
    cc_kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': supplier_account,
        'ip': {
            'data': ip_list,
            'exact': 1,
            'flag': 'bk_host_innerip'
        },
        'condition': [
            {
                'bk_obj_id': 'host',
                'fields': ['bk_host_id', 'bk_host_innerip']
            }
        ],
    }

    client = get_client_by_user(executor)
    cc_result = client.cc.search_host(cc_kwargs)

    if not cc_result['result']:
        message = cc_handle_api_error('cc.search_host', cc_kwargs, cc_result['message'])
        return {'result': False, 'message': message}

    # change bk_host_id to str to use str.join() function
    ip_to_id = {item['host']['bk_host_innerip']: str(item['host']['bk_host_id']) for item in cc_result['data']['info']}
    host_id_list = []
    invalid_ip_list = []
    for ip in ip_list:
        if ip in ip_to_id:
            host_id_list.append(ip_to_id[ip])
        else:
            invalid_ip_list.append(ip)

    if invalid_ip_list:
        result = {
            'result': False,
            'message': _(u"查询配置平台(CMDB)接口cc.search_host表明，存在不属于当前业务的IP: {ip}").format(
                ip=','.join(invalid_ip_list)
            )
        }
        return result
    return {'result': True, 'data': host_id_list}


def get_module_set_id(topo_data, module_id):
    """
    获取模块属于的集群ID
    :param topo_data:
    :param module_id:
    :return:
    """
    for item in topo_data:
        if item['bk_obj_id'] == "set" and item.get('child'):
            set_id = item['bk_inst_id']
            for mod in item['child']:
                if mod['bk_inst_id'] == module_id:
                    return set_id

        if item.get('child'):
            set_id = get_module_set_id(item['child'], module_id)
            if set_id:
                return set_id


def cc_format_prop_data(executor, obj_id, prop_id, language, supplier_account):
    ret = {
        "result": True,
        "data": {}
    }
    client = get_client_by_user(executor)
    if language:
        setattr(client, 'language', language)
    cc_kwargs = {
        "bk_obj_id": obj_id,
        "bk_supplier_account": supplier_account
    }

    cc_result = client.cc.search_object_attribute(cc_kwargs)
    if not cc_result['result']:
        message = cc_handle_api_error('cc.search_object_attribute', cc_kwargs, cc_result['message'])
        ret['result'] = False
        ret['message'] = message
        return ret

    for prop in cc_result['data']:
        if prop['bk_property_id'] == prop_id:
            for item in prop['option']:
                ret['data'][item['name'].strip()] = item['id']
            else:
                break
    return ret


def cc_format_tree_mode_id(front_id_list):
    if front_id_list is None:
        return []
    return map(lambda x: int(str(x).split('_')[1]) if len(str(x).split('_')) == 2 else int(x), front_id_list)


class CCTransferHostModuleService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        cc_module_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_module_select'))
        cc_is_increment = data.get_one_of_inputs('cc_is_increment')

        cc_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_supplier_account": supplier_account,
            "bk_host_id": [int(host_id) for host_id in host_result['data']],
            "bk_module_id": cc_module_select,
            "is_increment": True if cc_is_increment == 'true' else False
        }
        cc_result = client.cc.transfer_host_module(cc_kwargs)
        if cc_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.transfer_host_module', cc_kwargs, cc_result['message'])
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []


class CCTransferHostModuleComponent(Component):
    name = _(u"转移主机模块")
    code = 'cc_transfer_host_module'
    bound_service = CCTransferHostModuleService
    form = '%scomponents/atoms/cc/cc_transfer_host_module.js' % settings.STATIC_URL


class CCUpdateHostService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        # 更新主机属性
        cc_host_property = data.get_one_of_inputs('cc_host_property')
        if cc_host_property == "bk_isp_name":
            bk_isp_name = cc_format_prop_data(executor,
                                              'host',
                                              'bk_isp_name',
                                              parent_data.get_one_of_inputs('language'),
                                              supplier_account)
            if not bk_isp_name['result']:
                data.set_outputs('ex_data', bk_isp_name['message'])
                return False

            cc_host_prop_value = bk_isp_name['data'].get(data.get_one_of_inputs('cc_host_prop_value'))
            if not cc_host_prop_value:
                data.set_outputs('ex_data', _(u"所属运营商校验失败，请重试并修改为正确的所属运营商"))
                return False

        elif cc_host_property == "bk_state_name":
            bk_state_name = cc_format_prop_data(executor,
                                                'host',
                                                'bk_state_name',
                                                parent_data.get_one_of_inputs('language'),
                                                supplier_account)
            if not bk_state_name['result']:
                data.set_outputs('ex_data', bk_state_name['message'])
                return False

            cc_host_prop_value = bk_state_name['data'].get(data.get_one_of_inputs('cc_host_prop_value'))
            if not cc_host_prop_value:
                data.set_outputs('ex_data', _(u"所在国家校验失败，请重试并修改为正确的所在国家"))
                return False
        elif cc_host_property == "bk_province_name":
            bk_province_name = cc_format_prop_data(executor,
                                                   'host',
                                                   'bk_province_name',
                                                   parent_data.get_one_of_inputs('language'),
                                                   supplier_account)
            if not bk_province_name['result']:
                data.set_outputs('ex_data', bk_province_name['message'])
                return False
            cc_host_prop_value = bk_province_name['data'].get(data.get_one_of_inputs('cc_host_prop_value'))
            if not cc_host_prop_value:
                data.set_outputs('ex_data', _(u"所在省份校验失败，请重试并修改为正确的所在省份"))
                return False
        else:
            cc_host_prop_value = data.get_one_of_inputs('cc_host_prop_value')

        cc_kwargs = {
            "bk_host_id": ",".join(host_result['data']),
            "bk_supplier_account": supplier_account,
            "data": {
                cc_host_property: cc_host_prop_value
            }
        }
        cc_result = client.cc.update_host(cc_kwargs)
        if cc_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.update_host', cc_kwargs, cc_result['message'])
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []


class CCUpdateHostComponent(Component):
    name = _(u"更新主机属性")
    code = 'cc_update_host'
    bound_service = CCUpdateHostService
    form = '%scomponents/atoms/cc/cc_update_host.js' % settings.STATIC_URL


class CCReplaceFaultMachineService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        cc_hosts = data.get_one_of_inputs('cc_host_replace_detail')

        # 查询主机可编辑属性
        search_attr_kwargs = {
            'bk_obj_id': 'host',
            'bk_supplier_account': supplier_account
        }
        search_attr_result = client.cc.search_object_attribute(search_attr_kwargs)
        if not search_attr_result['result']:
            message = handle_api_error(__group_name__,
                                       'cc.search_object_attribute',
                                       search_attr_kwargs,
                                       search_attr_result['message'])
            logger.error(message)
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
        all_hosts.extend(fault_replace_ip_map.keys())
        all_hosts.extend(fault_replace_ip_map.values())
        search_kwargs['ip'] = {
            'data': all_hosts,
            'exact': 1,
            'flag': 'bk_host_innerip'
        }

        hosts_result = client.cc.search_host(search_kwargs)

        if not hosts_result['result']:
            message = handle_api_error(__group_name__,
                                       'cc.search_host',
                                       search_attr_kwargs,
                                       hosts_result['message'])
            logger.error(message)
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

        for fault_ip, new_ip in fault_replace_ip_map.items():
            fault_host = host_dict.get(fault_ip)
            new_host = host_dict.get(new_ip)

            if not fault_host:
                data.outputs.ex_data = _(u"无法查询到 %s 机器信息，请确认该机器是否在当前业务下") % fault_ip
                return False

            if not new_host:
                data.outputs.ex_data = _(u"无法查询到 %s 机器信息，请确认该机器是否在当前业务下") % new_ip
                return False

            update_item = {
                'datas': {},
                'inst_id': new_host['bk_host_id']
            }
            for attr in [attr for attr in editable_attrs if attr in fault_host]:
                update_item['datas'][attr] = fault_host[attr]

            batch_update_kwargs['update'].append(update_item)
            fault_replace_id_map[fault_host['bk_host_id']] = new_host['bk_host_id']

        update_result = client.cc.batch_update_inst(batch_update_kwargs)

        if not update_result['result']:
            message = handle_api_error(__group_name__,
                                       'cc.batch_update_inst',
                                       batch_update_kwargs,
                                       update_result['message'])
            logger.error(message)
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
            message = handle_api_error(__group_name__,
                                       'cc.transfer_host_to_faultmodule',
                                       fault_transfer_kwargs,
                                       fault_transfer_result['message'])
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
                message = handle_api_error(__group_name__,
                                           'cc.transfer_host_module',
                                           kwargs,
                                           transfer_result['message'])
                logger.error(message)
                data.outputs.ex_data = u"{msg}\n{success}".format(
                    msg=message,
                    success=_(u"成功替换的机器: %s") % ','.join(success))
                return False

            success.append(host_id_to_ip[kwargs['bk_host_id'][0]])

    def outputs_format(self):
        return []


class CCReplaceFaultMachineComponent(Component):
    name = _(u"故障机替换")
    code = 'cc_replace_fault_machine'
    bound_service = CCReplaceFaultMachineService
    form = '%scomponents/atoms/cc/cc_replace_fault_machine.js' % settings.STATIC_URL


class CCEmptySetHostsService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_select'))
        for set_id in cc_set_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
            }
            cc_result = client.cc.transfer_sethost_to_idle_module(cc_kwargs)
            if not cc_result['result']:
                message = cc_handle_api_error('cc.transfer_sethost_to_idle_module',
                                              cc_kwargs,
                                              cc_result['message'])
                data.set_outputs('ex_data', message)
                return False
        return True

    def outputs_format(self):
        return []


class CCEmptySetHostsComponent(Component):
    name = _(u"清空集群中主机")
    code = 'cc_empty_set_hosts'
    bound_service = CCEmptySetHostsService
    form = '%scomponents/atoms/cc/cc_empty_set_hosts.js' % settings.STATIC_URL


class CCBatchDeleteSetService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_select'))

        cc_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_supplier_account": supplier_account,
            "delete": {
                "inst_ids": cc_set_select
            }
        }
        cc_result = client.cc.batch_delete_set(cc_kwargs)
        if not cc_result['result']:
            message = cc_handle_api_error('cc.batch_delete_set',
                                          cc_kwargs,
                                          cc_result['message'])
            data.set_outputs('ex_data', message)
            return False
        return True

    def outputs_format(self):
        return []


class CCBatchDeleteSetComponent(Component):
    name = _(u"删除集群")
    code = 'cc_batch_delete_set'
    bound_service = CCBatchDeleteSetService
    form = '%scomponents/atoms/cc/cc_batch_delete_set.js' % settings.STATIC_URL


class CCUpdateSetServiceStatusService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_select'))

        for set_id in cc_set_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
                "data": {
                    "bk_service_status": data.get_one_of_inputs('cc_set_status')
                }
            }
            cc_result = client.cc.update_set(cc_kwargs)
            if not cc_result['result']:
                message = cc_handle_api_error('cc.update_set',
                                              cc_kwargs,
                                              cc_result['message'])
                data.set_outputs('ex_data', message)
                return False
        return True

    def outputs_format(self):
        return []


class CCUpdateSetServiceStatusComponent(Component):
    name = _(u"修改集群服务状态")
    code = 'cc_update_set_service_status'
    bound_service = CCUpdateSetServiceStatusService
    form = '%scomponents/atoms/cc/cc_update_set_service_status.js' % settings.STATIC_URL


class CCCreateSetService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        cc_set_parent_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_parent_select'))
        cc_set_info = data.get_one_of_inputs('cc_set_info')

        bk_set_env = cc_format_prop_data(executor,
                                         'set',
                                         'bk_set_env',
                                         parent_data.get_one_of_inputs('language'),
                                         supplier_account)
        if not bk_set_env['result']:
            data.set_outputs('ex_data', bk_set_env['message'])
            return False

        bk_service_status = cc_format_prop_data(executor,
                                                'set',
                                                'bk_service_status',
                                                parent_data.get_one_of_inputs('language'),
                                                supplier_account)
        if not bk_service_status['result']:
            data.set_outputs('ex_data', bk_service_status['message'])
            return False

        set_list = []
        for set_params in cc_set_info:
            set_property = {}
            for key, value in list(set_params.items()):
                if value:
                    if key == "bk_set_env":
                        value = bk_set_env['data'].get(value)
                        if not value:
                            data.set_outputs('ex_data', _(u"环境类型校验失败，请重试并修改为正确的环境类型"))
                            return False

                    elif key == "bk_service_status":
                        value = bk_service_status['data'].get(value)
                        if not value:
                            data.set_outputs('ex_data', _(u"服务状态校验失败，请重试并修改为正确的服务状态"))
                            return False

                    elif key == "bk_capacity":
                        try:
                            value = int(value)
                        except Exception:
                            self.logger.error(traceback.format_exc())
                            data.set_outputs('ex_data', _(u"集群容量必须为整数"))
                            return False

                    set_property[key] = value
            set_list.append(set_property)

        for parent_id in cc_set_parent_select:
            for set_data in set_list:
                cc_kwargs = {
                    'bk_biz_id': biz_cc_id,
                    'bk_supplier_account': supplier_account,
                    'data': {
                        'bk_parent_id': parent_id
                    }
                }
                cc_kwargs['data'].update(set_data)
                cc_result = client.cc.create_set(cc_kwargs)
                if not cc_result['result']:
                    message = cc_handle_api_error('cc.create_set',
                                                  cc_kwargs,
                                                  cc_result['message'])
                    data.set_outputs('ex_data', message)
                    return False

        return True

    def outputs_format(self):
        return []


class CCCreateSetComponent(Component):
    name = _(u"创建集群")
    code = 'cc_create_set'
    bound_service = CCCreateSetService
    form = '%scomponents/atoms/cc/cc_create_set.js' % settings.STATIC_URL


class CCUpdateSetService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_select'))

        cc_set_property = data.get_one_of_inputs('cc_set_property')
        if cc_set_property == "bk_service_status":
            bk_service_status = cc_format_prop_data(executor,
                                                    'set',
                                                    'bk_service_status',
                                                    parent_data.get_one_of_inputs('language'),
                                                    supplier_account)
            if not bk_service_status['result']:
                data.set_outputs('ex_data', bk_service_status['message'])
                return False

            cc_set_prop_value = bk_service_status['data'].get(data.get_one_of_inputs('cc_set_prop_value'))
            if not cc_set_prop_value:
                data.set_outputs('ex_data', _(u"服务状态校验失败，请重试并修改为正确的服务状态"))
                return False

        elif cc_set_property == "bk_set_env":
            bk_set_env = cc_format_prop_data(executor,
                                             'set',
                                             'bk_set_env',
                                             parent_data.get_one_of_inputs('language'),
                                             supplier_account)
            if not bk_set_env['result']:
                data.set_outputs('ex_data', bk_set_env['message'])
                return False

            cc_set_prop_value = bk_set_env['data'].get(data.get_one_of_inputs('cc_set_prop_value'))
            if not cc_set_prop_value:
                data.set_outputs('ex_data', _(u"环境类型校验失败，请重试并修改为正确的环境类型"))
                return False

        else:
            cc_set_prop_value = data.get_one_of_inputs('cc_set_prop_value')

        for set_id in cc_set_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
                "data": {
                    cc_set_property: cc_set_prop_value
                }
            }
            cc_result = client.cc.update_set(cc_kwargs)
            if not cc_result['result']:
                message = cc_handle_api_error('cc.update_set',
                                              cc_kwargs,
                                              cc_result['message'])
                data.set_outputs('ex_data', message)
                return False
        return True

    def outputs_format(self):
        return []


class CCUpdateSetComponent(Component):
    name = _(u"更新集群属性")
    code = 'cc_update_set'
    bound_service = CCUpdateSetService
    form = '%scomponents/atoms/cc/cc_update_set.js' % settings.STATIC_URL


class CCUpdateModuleService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_supplier_account": supplier_account
        }
        tree_data = client.cc.search_biz_inst_topo(kwargs)
        if not tree_data['result']:
            message = cc_handle_api_error('cc.search_biz_inst_topo',
                                          kwargs,
                                          tree_data['message'])
            data.set_outputs('ex_data', message)
            return False

        cc_module_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_module_select'))
        cc_module_property = data.get_one_of_inputs('cc_module_property')
        if cc_module_property == "bk_module_type":
            bk_module_type = cc_format_prop_data(executor,
                                                 'module',
                                                 'bk_module_type',
                                                 parent_data.get_one_of_inputs('language'),
                                                 supplier_account)
            if not bk_module_type['result']:
                data.set_outputs('ex_data', bk_module_type['message'])
                return False

            cc_module_prop_value = bk_module_type['data'].get(data.get_one_of_inputs('cc_module_prop_value'))
            if not cc_module_prop_value:
                data.set_outputs('ex_data', _(u"模块类型校验失败，请重试并填写正确的模块类型"))
                return False
        else:
            cc_module_prop_value = data.get_one_of_inputs('cc_module_prop_value')

        for module_id in cc_module_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": get_module_set_id(tree_data['data'], module_id),
                "bk_module_id": module_id,
                "data": {
                    cc_module_property: cc_module_prop_value
                }
            }
            cc_result = client.cc.update_module(cc_kwargs)
            if not cc_result['result']:
                message = cc_handle_api_error('cc.update_module',
                                              cc_kwargs,
                                              cc_result['message'])
                data.set_outputs('ex_data', message)
                return False
        return True

    def outputs_format(self):
        return []


class CCUpdateModuleComponent(Component):
    name = _(u"更新模块属性")
    code = 'cc_update_module'
    bound_service = CCUpdateModuleService
    form = '%scomponents/atoms/cc/cc_update_module.js' % settings.STATIC_URL


class CCTransferHostToIdleService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        transfer_kwargs = {
            'bk_supplier_account': supplier_account,
            'bk_biz_id': biz_cc_id,
            'bk_host_id': [int(host_id) for host_id in host_result['data']]
        }

        transfer_result = client.cc.transfer_host_to_idlemodule(transfer_kwargs)

        if transfer_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.transfer_host_to_idlemodule', transfer_kwargs, transfer_result['message'])
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []


class CCTransferHostToIdleComponent(Component):
    name = _(u"转移主机至空闲机")
    code = 'cc_transfer_to_idle'
    bound_service = CCTransferHostToIdleService
    form = '%scomponents/atoms/cc/cc_transfer_to_idle.js' % settings.STATIC_URL


class CmdbTransferFaultHostService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        transfer_params = {
            "bk_biz_id": biz_cc_id,
            "bk_host_id": [int(host_id) for host_id in host_result['data']]
        }
        transfer_result = client.cc.transfer_host_to_faultmodule(transfer_params)
        if transfer_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.transfer_host_to_fault_module',
                                          transfer_params, transfer_result['message'])
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []


class CmdbTransferFaultHostComponent(Component):
    name = _(u'转移主机到业务的故障机模块')
    code = 'cmdb_transfer_fault_host'
    bound_service = CmdbTransferFaultHostService
    form = '%scomponents/atoms/cc/cmdb_transfer_fault_host.js' % settings.STATIC_URL


class CmdbTransferHostResourceModuleService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')

        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        transfer_params = {
            "bk_biz_id": biz_cc_id,
            "bk_host_id": [int(host_id) for host_id in host_result['data']]
        }
        transfer_result = client.cc.transfer_host_to_resourcemodule(transfer_params)
        if transfer_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.transfer_host_to_resource_module',
                                          transfer_params, transfer_result['message'])
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []


class CmdbTransferHostResourceModuleComponent(Component):
    name = _(u'转移主机至资源池')
    code = 'cmdb_transfer_host_resource'
    bound_service = CmdbTransferHostResourceModuleService
    form = '%scomponents/atoms/cc/cmdb_transfer_host_resource.js' % settings.STATIC_URL

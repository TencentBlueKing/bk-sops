# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging
import json

from django.utils.translation import ugettext_lazy as _

from blueapps.utils.esbclient import get_client_by_user

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from pipeline.components.utils import get_ip_by_regex

logger = logging.getLogger('celery')

__group_name__ = _(u"配置平台(CMDB)")
__group_icon__ = '%scomponents/icons/cc.png' % settings.STATIC_URL


def cc_handle_api_error(api_name, params, error):
    message = _(u"调用{system}接口{api_name}返回失败, params={params}, error={error}").format(
        system=__group_name__,
        api_name=api_name,
        params=json.dumps(params),
        error=error
    )
    logger.error(message)
    return message


def cc_get_host_id_by_innerip(executor, bk_biz_id, ip_list):
    """
    获取主机ID
    :param executor:
    :param bk_biz_id:
    :param ip_list:
    :return: [1, 2, 3] id列表
    """
    cc_kwargs = {
        'bk_biz_id': bk_biz_id,
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
    client.set_bk_api_ver('v2')
    cc_result = client.cc.search_host(cc_kwargs)

    if not cc_result['result']:
        message = cc_handle_api_error('cc.search_host', cc_kwargs, cc_result['message'])
        return {'result': False, 'message': message}

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


def cc_format_prop_data(executor, obj_id, prop_id, language):
    ret = {
        "result": True,
        "data": {}
    }
    client = get_client_by_user(executor)
    client.set_bk_api_ver('v2')
    if language:
        setattr(client, 'language', language)
    cc_kwargs = {
        "bk_obj_id": obj_id
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


class CCTransferHostModuleService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))

        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        cc_module_select = data.get_one_of_inputs('cc_module_select')
        cc_is_increment = data.get_one_of_inputs('cc_is_increment')

        cc_kwargs = {
            "bk_biz_id": biz_cc_id,
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
    form = '%scomponents/atoms/sites/%s/cc/cc_transfer_host_module.js' % (settings.STATIC_URL, settings.RUN_VER)


class CCUpdateHostService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
        # 查询主机id
        ip_list = get_ip_by_regex(data.get_one_of_inputs('cc_host_ip'))
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        # 更新主机属性
        cc_host_property = data.get_one_of_inputs('cc_host_property')
        if cc_host_property == "bk_isp_name":
            bk_isp_name = cc_format_prop_data(executor, 'host', 'bk_isp_name',
                                              parent_data.get_one_of_inputs('language'))
            if not bk_isp_name['result']:
                data.set_outputs('ex_data', bk_isp_name['message'])
                return False

            cc_host_prop_value = bk_isp_name['data'].get(data.get_one_of_inputs('cc_host_prop_value'))
            if not cc_host_prop_value:
                data.set_outputs('ex_data', _(u"所属运营商校验失败，请重试并修改为正确的所属运营商"))
                return False

        elif cc_host_property == "bk_state_name":
            bk_state_name = cc_format_prop_data(executor, 'host', 'bk_state_name',
                                                parent_data.get_one_of_inputs('language'))
            if not bk_state_name['result']:
                data.set_outputs('ex_data', bk_state_name['message'])
                return False

            cc_host_prop_value = bk_state_name['data'].get(data.get_one_of_inputs('cc_host_prop_value'))
            if not cc_host_prop_value:
                data.set_outputs('ex_data', _(u"所在国家校验失败，请重试并修改为正确的所在国家"))
                return False
        elif cc_host_property == "bk_province_name":
            bk_province_name = cc_format_prop_data(executor, 'host', 'bk_province_name',
                                                   parent_data.get_one_of_inputs('language'))
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
    form = '%scomponents/atoms/sites/%s/cc/cc_update_host.js' % (settings.STATIC_URL, settings.RUN_VER)


class CCUpdateSetServiceStatusService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))

        cc_set_select = data.get_one_of_inputs('cc_set_select')
        for set_id in cc_set_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
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
    form = '%scomponents/atoms/sites/%s/cc/cc_update_set_service_status.js' % (settings.STATIC_URL, settings.RUN_VER)


class CCCreateSetService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))

        cc_set_parent_select = data.get_one_of_inputs('cc_set_parent_select')
        if not cc_set_parent_select:
            data.set_outputs('ex_data', _(u"父实例不能为空，请选择。"))
            return False
        cc_set_info = data.get_one_of_inputs('cc_set_info')
        if not cc_set_info:
            data.set_outputs('ex_data', _(u"集群信息不可为空请输入"))
            return False

        cc_kwargs = {
            'bk_biz_id': biz_cc_id,
            'data': {}
        }

        for parent_id in cc_set_parent_select:
            cc_kwargs['data']['bk_parent_id'] = parent_id
            for set_params in cc_set_info:
                for key, value in set_params.items():
                    if value:
                        if key == "bk_set_env":
                            bk_set_env = cc_format_prop_data(executor, 'set', 'bk_set_env',
                                                             parent_data.get_one_of_inputs('language'))
                            if not bk_set_env['result']:
                                data.set_outputs('ex_data', bk_set_env['message'])
                                return False

                            value = bk_set_env['data'].get(value)
                            if not value:
                                data.set_outputs('ex_data', _(u"环境类型校验失败，请重试并修改为正确的环境类型"))
                                return False

                        elif key == "bk_service_status":
                            bk_service_status = cc_format_prop_data(executor, 'set', 'bk_service_status',
                                                                    parent_data.get_one_of_inputs('language'))
                            if not bk_service_status['result']:
                                data.set_outputs('ex_data', bk_service_status['message'])
                                return False

                            value = bk_service_status['data'].get(value)
                            if not value:
                                data.set_outputs('ex_data', _(u"服务状态校验失败，请重试并修改为正确的服务状态"))
                                return False

                        cc_kwargs['data'][key] = value

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
    form = '%scomponents/atoms/sites/%s/cc/cc_create_set.js' % (settings.STATIC_URL, settings.RUN_VER)


class CCUpdateSetService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))

        cc_set_select = data.get_one_of_inputs('cc_set_select')

        cc_set_property = data.get_one_of_inputs('cc_set_property')
        if cc_set_property == "bk_service_status":
            bk_service_status = cc_format_prop_data(executor, 'set', 'bk_service_status',
                                                    parent_data.get_one_of_inputs('language'))
            if not bk_service_status['result']:
                data.set_outputs('ex_data', bk_service_status['message'])
                return False

            cc_set_prop_value = bk_service_status['data'].get(data.get_one_of_inputs('cc_set_prop_value'))
            if not cc_set_prop_value:
                data.set_outputs('ex_data', _(u"服务状态校验失败，请重试并修改为正确的服务状态"))
                return False

        elif cc_set_property == "bk_set_env":
            bk_set_env = cc_format_prop_data(executor, 'set', 'bk_set_env', parent_data.get_one_of_inputs('language'))
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
    form = '%scomponents/atoms/sites/%s/cc/cc_update_set.js' % (settings.STATIC_URL, settings.RUN_VER)


class CCUpdateModuleService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))

        kwargs = {
            "bk_biz_id": biz_cc_id
        }
        tree_data = client.cc.search_biz_inst_topo(kwargs)
        if not tree_data['result']:
            message = cc_handle_api_error('cc.search_biz_inst_topo',
                                          kwargs,
                                          tree_data['message'])
            data.set_outputs('ex_data', message)
            return False

        cc_module_select = data.get_one_of_inputs('cc_module_select')
        cc_module_property = data.get_one_of_inputs('cc_module_property')
        if cc_module_property == "bk_module_type":
            bk_module_type = cc_format_prop_data(executor, 'module', 'bk_module_type',
                                                 parent_data.get_one_of_inputs('language'))
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
    form = '%scomponents/atoms/sites/%s/cc/cc_update_module.js' % (settings.STATIC_URL, settings.RUN_VER)

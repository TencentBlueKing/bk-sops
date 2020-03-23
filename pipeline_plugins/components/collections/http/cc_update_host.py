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

import logging

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import (
    get_ip_by_regex,
    supplier_account_for_business
)
from pipeline_plugins.components.collections.sites.open.cc import (
    cc_handle_api_error
)

from gcloud.conf import settings

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")


def cc_get_host_id_by_innerip(executor, bk_biz_id, ip_list, supplier_account):
    """
    获取主机ID
    :param executor:
    :param bk_biz_id:
    :param ip_list:
    :return: {"127.0.0.q":1,"127.0.0.2":2}
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
        message = cc_handle_api_error('cc.search_host', cc_kwargs, cc_result)
        return {'result': False, 'message': message}

    # change bk_host_id to str to use str.join() function
    ip_to_id = {item['host']['bk_host_innerip']: item['host']['bk_host_id'] for item in cc_result['data']['info']}
    invalid_ip_list = []
    for ip in ip_list:
        if ip not in ip_to_id:
            result = {
                'result': False,
                'message': _("查询配置平台(CMDB)接口cc.search_host表明，存在不属于当前业务的IP: {ip}").format(
                    ip=','.join(invalid_ip_list)
                )
            }
            return result

    return {'result': True, 'data': ip_to_id}


class CCUpdateHostService(Service):

    def inputs_format(self):
        return [
            self.InputItem(name=_('业务 ID'),
                           key='biz_cc_id',
                           type='string',
                           schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
            self.InputItem(name=_('主机信息'),
                           key='cc_host_info',
                           type='array',
                           schema=ArrayItemSchema(description=_('待更新主机属性对象列表'),
                                                  item_schema=ObjectItemSchema(description=_('主机属性描述对象'),
                                                                               property_schemas={})))]

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
        cc_host_info = data.get_one_of_inputs('cc_host_info')

        # 组装参数
        host_list = []
        ip_list = ''
        innerip = 'bk_host_innerip'
        for host_params in cc_host_info:
            if not (innerip in list(host_params.keys()) and host_params[innerip]):
                data.set_outputs('ex_data', _("请填写内网ip"))
                return False

            properties = {}
            for key, value in list(host_params.items()):
                if value:
                    if key == innerip:
                        ip_list += ("%s%s" % (value, "\n"))
                        host_list.append({
                            "bk_host_id": value,
                            "properties": properties
                        })
                        continue
                    properties.update({key: value})

        # 查询主机id
        ip_list = get_ip_by_regex(ip_list)
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        # 参数内更新主机id
        for host in host_list:
            host['bk_host_id'] = host_result['data'][host['bk_host_id']]

        cc_kwargs = {
            "bk_supplier_account": supplier_account,
            "update": host_list
        }
        cc_result = client.cc.batch_update_host(cc_kwargs)
        if cc_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.update_host', cc_kwargs, cc_result)
            self.logger.error(message)
            data.set_outputs('ex_data', message)
            return False


class CCUpdateHostComponent(Component):
    name = _("更新主机属性")
    code = 'cc_update_host'
    bound_service = CCUpdateHostService
    form = '%scomponents/atoms/cc/v1.0/cc_update_host.js' % settings.STATIC_URL
    version = '1.0'

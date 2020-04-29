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

import ujson as json

from gcloud.conf import settings

logger = logging.getLogger('root')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list, supplier_account=0, host_fields=None):
    """
    @summary: 根据模块ID查询主机内网ip
    :param username:
    :param biz_cc_id:
    :param module_id_list:
    :param supplier_account: 开发商 ID，暂不使用
    :return:
    """
    client = get_client_by_user(username)
    cc_kwargs = {
        'bk_biz_id': biz_cc_id,
        'bk_supplier_account': supplier_account,
        'condition': [
            {
                'bk_obj_id': 'host',
                'fields': host_fields or ['bk_host_innerip'],
            },
            {
                'bk_obj_id': 'module',
                'fields': [],
                'condition': [
                    {
                        'field': 'bk_module_id',
                        'operator': '$in',
                        'value': module_id_list
                    }
                ]
            },
            {
                'bk_obj_id': 'set',
                'fields': [],
                'condition': []
            },
            {
                'bk_obj_id': 'biz',
                'fields': [],
                'condition': []
            }
        ]
    }
    cc_result = client.cc.search_host(cc_kwargs)
    result = []
    if cc_result['result']:
        result = cc_result['data']['info']
    else:
        logger.warning('client.cc.search_host ERROR###biz_cc_id=%s'
                       '###cc_result=%s' % (biz_cc_id, json.dumps(cc_result)))
    return result


def cc_format_module_hosts(username, biz_cc_id, module_id_list, supplier_account, data_format, host_fields):
    module_host_list = cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list, supplier_account, host_fields)
    if data_format == 'tree':
        module_host_dict = {}
        for item in module_host_list:
            for mod in item['module']:
                if mod['bk_module_id'] in module_id_list:
                    module_host_dict.setdefault('module_%s' % mod['bk_module_id'], []).append({
                        'id': '%s_%s' % (mod['bk_module_id'], item['host']['bk_host_innerip']),
                        'label': item['host']['bk_host_innerip']
                    })

        return module_host_dict
    else:
        return module_host_list

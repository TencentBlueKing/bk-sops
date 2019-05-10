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

import json
import re
import logging

from urllib import urlencode
from cryptography.fernet import Fernet
from django.core.cache import cache

from pipeline_plugins.components.utils.common import supplier_account_inject, get_ip_by_regex, ip_re, ip_pattern
from gcloud.conf import settings

logger = logging.getLogger('root')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__all__ = [
    'cc_get_ips_info_by_str',
    'cc_get_ip_list_by_biz_and_user',
    'cc_get_inner_ip_by_module_id',
    'get_job_instance_url',
    'get_node_callback_url'
]

JOB_APP_CODE = 'bk_job'


def cc_get_ips_info_by_str(username, biz_cc_id, ip_str, use_cache=True):
    """
    @summary: 从ip_str中匹配出IP信息
    @param username
    @param biz_cc_id
    @param ip_str
    @param use_cache
    @note: 需要兼容的ip_str格式有
        1： IP，IP  这种纯IP格式需要保证IP在业务中唯一，否则报错（需要注意一个IP
            属于多个集群的情况，要根据平台和IP共同判断是否是同一个IP）
        2： 集群名称|模块名称|IP，集群名称|模块名称|IP  这种格式可以唯一定位到一
            个IP（如果业务把相同IP放到同一模块，还是有问题）
        3： 平台ID:IP，平台ID:IP  这种格式可以唯一定位到一个IP，主要是兼容Job组件
            传参需要和获取Job作业模板步骤参数
    @return: {'result': True or False, 'data': [{'InnerIP': ,'HostID': ,
        'Source': , 'SetID': , 'SetName': , 'ModuleID': , 'ModuleName': },{}]}
    """
    plat_ip_reg = re.compile(r'\d+:' + ip_re)
    set_module_ip_reg = re.compile(
        ur'[\u4e00-\u9fa5\w]+\|[\u4e00-\u9fa5\w]+\|' + ip_re
    )  # 中文字符或者其他字符
    ip_input_list = get_ip_by_regex(ip_str)
    ip_result = []
    # 如果是格式2，可以返回IP的集群、模块、平台信息
    if set_module_ip_reg.match(ip_str):
        set_module_ip = []
        for match in set_module_ip_reg.finditer(ip_str):
            set_module_ip.append(match.group())

        ip_list = cc_get_ip_list_by_biz_and_user(username=username, biz_cc_id=biz_cc_id, use_cache=use_cache)
        for ip_info in ip_list:
            set_dict = {s['bk_set_id']: s for s in ip_info['set']}
            for module in ip_info['module']:
                if '%s|%s|%s' % (set_dict[module['bk_set_id']]['bk_set_name'],
                                 module['bk_module_name'],
                                 ip_info['host']['bk_host_innerip']) in set_module_ip:
                    ip_result.append({'InnerIP': ip_info['host']['bk_host_innerip'],
                                      'HostID': ip_info['host']['bk_host_id'],
                                      'Source': ip_info['host']['bk_cloud_id'][0]['id'],
                                      'SetID': module['bk_set_id'],
                                      'SetName': set_dict[module['bk_set_id']]['bk_set_name'],
                                      'ModuleID': module['bk_module_id'],
                                      'ModuleName': module['bk_module_name'],
                                      })

    # 如果是格式3，返回IP的平台信息
    elif plat_ip_reg.match(ip_str):
        plat_ip = []
        for match in plat_ip_reg.finditer(ip_str):
            plat_ip.append(match.group())

        ip_list = cc_get_ip_list_by_biz_and_user(username=username, biz_cc_id=biz_cc_id, use_cache=use_cache)
        for ip_info in ip_list:
            if '%s:%s' % (ip_info['host']['bk_cloud_id'][0]['id'], ip_info['host']['bk_host_innerip']) in plat_ip:
                ip_result.append({'InnerIP': ip_info['host']['bk_host_innerip'],
                                  'HostID': ip_info['host']['bk_host_id'],
                                  'Source': ip_info['host']['bk_cloud_id'][0]['id'],
                                  })

    else:
        ip = []
        for match in ip_pattern.finditer(ip_str):
            ip.append(match.group())

        ip_list = cc_get_ip_list_by_biz_and_user(username=username, biz_cc_id=biz_cc_id, use_cache=use_cache)
        host_id_list = []
        for ip_info in ip_list:
            if ip_info['host']['bk_host_innerip'] in ip and ip_info['host']['bk_host_id'] not in host_id_list:
                ip_result.append({'InnerIP': ip_info['host']['bk_host_innerip'],
                                  'HostID': ip_info['host']['bk_host_id'],
                                  'Source': ip_info['host']['bk_cloud_id'][0]['id'],
                                  })
                host_id_list.append(ip_info['host']['bk_host_id'])

    valid_ip = [ip_info['InnerIP'] for ip_info in ip_result]
    invalid_ip = list(set(ip_input_list) - set(valid_ip))
    result = {
        'result': True,
        'ip_result': ip_result,
        'ip_count': len(ip_result),
        'invalid_ip': invalid_ip,
    }
    return result


@supplier_account_inject
def cc_get_ip_list_by_biz_and_user(username, biz_cc_id, supplier_account, use_cache=True):
    """
    @summary：根据当前用户和业务ID获取IP
    @note: 由于获取了全业务IP，接口会比较慢，需要加缓存
    @note: 由于存在单主机多IP问题，需要取第一个IP作为实际值
    @param-username
    @param-biz_cc_id

    """
    cache_key = "cc_get_ip_list_by_biz_and_user_%s_%s" % (username, biz_cc_id)
    data = cache.get(cache_key)
    if not data or not use_cache:
        client = get_client_by_user(username)
        cc_result = client.cc.search_host({
            'bk_supplier_account': supplier_account,
            'condition': [
                {
                    'bk_obj_id': 'biz',
                    'fields': [],
                    'condition': [{
                        'field': 'bk_biz_id',
                        'operator': '$eq',
                        'value': biz_cc_id
                    }]
                },
                {
                    "bk_obj_id": "module",
                    "fields": [],
                    "condition": []
                },
                {
                    "bk_obj_id": "set",
                    "fields": [],
                    "condition": []
                }
            ]
        })
        if cc_result['result']:
            data = cc_result['data']['info']
            # 多IP主机处理，取第一个IP
            for host in data:
                if ',' in host['host']['bk_host_innerip']:
                    host['bk_host_innerip'] = host['bk_host_innerip'].split(',')[0]
            cache.set(cache_key, data, 60)
        else:
            logger.warning((u"search_host ERROR###biz_cc_id=%s"
                            u"###cc_result=%s") % (biz_cc_id,
                                                   json.dumps(cc_result)))
    if not data:
        return []
    return data


def cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list, supplier_account=0):
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
        "bk_biz_id": biz_cc_id,
        "bk_supplier_account": supplier_account,
        "condition": [
            {
                "bk_obj_id": "host",
                "fields": ["bk_host_innerip"],
            },
            {
                "bk_obj_id": "module",
                "fields": [],
                "condition": [
                    {
                        "field": "bk_module_id",
                        "operator": "$in",
                        "value": module_id_list
                    }
                ]
            },
            {
                "bk_obj_id": "set",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "biz",
                "fields": [],
                "condition": []
            }
        ]
    }
    cc_result = client.cc.search_host(cc_kwargs)
    result = []
    if cc_result['result']:
        result = cc_result['data']['info']
    else:
        logger.warning(u"client.cc.search_host ERROR###biz_cc_id=%s"
                       u"###cc_result=%s" % (biz_cc_id, json.dumps(cc_result)))
    return result


def get_job_instance_url(biz_cc_id, job_instance_id):
    url_format = u'%s?taskInstanceList&appId=%s#taskInstanceId=%s'

    if settings.OPEN_VER == 'community':
        return url_format % (
            settings.BK_JOB_HOST,
            biz_cc_id,
            job_instance_id,
        )

    else:
        query = {
            'app': JOB_APP_CODE,
            'url': url_format % (
                settings.BK_JOB_HOST,
                biz_cc_id,
                job_instance_id,
            )
        }
        return "%s/console/?%s" % (settings.BK_PAAS_HOST, urlencode(query))


def get_node_callback_url(node_id):
    f = Fernet(settings.CALLBACK_KEY)
    if settings.RUN_MODE == 'PRODUCT':
        callback_prefix = settings.APP_HOST
    else:
        callback_prefix = settings.TEST_APP_HOST
    return "%s/taskflow/api/nodes/callback/%s/" % (callback_prefix,
                                                   f.encrypt(bytes(node_id)))

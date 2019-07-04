# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json
import re
import logging

from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

from blueapps.utils.esbclient import get_client_by_user
from pipeline.conf import settings

ip_re = r'(([12][0-9][0-9]|[1-9][0-9]|[0-9])\.){3,3}' \
        r'([12][0-9][0-9]|[1-9][0-9]|[0-9])'
ip_pattern = re.compile(ip_re)

logger = logging.getLogger('root')


def get_ip_by_regex(ip_str):
    ip_str = "%s" % ip_str
    ret = []
    for match in ip_pattern.finditer(ip_str):
        ret.append(match.group())
    return ret


def cc_get_ips_info_by_str(username, biz_cc_id, ip_str):
    """
    @summary: 从ip_str中匹配出IP信息
    @param username
    @param biz_cc_id
    @param ip_str
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

        ip_list = cc_get_ip_list_by_biz_and_user(username,
                                                 biz_cc_id)
        for _ip in ip_list:
            if '%s|%s|%s' % (_ip['SetName'],
                             _ip['ModuleName'],
                             _ip['InnerIP']) in set_module_ip:
                ip_result.append({'InnerIP': _ip['InnerIP'],
                                  'HostID': _ip['HostID'],
                                  'Source': _ip['Source'],
                                  'SetID': _ip['SetID'],
                                  'SetName': _ip['SetName'],
                                  'ModuleID': _ip['ModuleID'],
                                  'ModuleName': _ip['ModuleName'],
                                  })

    # 如果是格式3，返回IP的平台信息
    elif plat_ip_reg.match(ip_str):
        plat_ip = []
        for match in plat_ip_reg.finditer(ip_str):
            plat_ip.append(match.group())

        ip_list = cc_get_ip_list_by_biz_and_user(username,
                                                 biz_cc_id)
        for _ip in ip_list:
            if '%s:%s' % (_ip['Source'], _ip['InnerIP']) in plat_ip:
                ip_result.append({'InnerIP': _ip['InnerIP'],
                                  'HostID': _ip['HostID'],
                                  'Source': _ip['Source'],
                                  })

    else:
        ip = []
        for match in ip_pattern.finditer(ip_str):
            ip.append(match.group())

        ip_list = cc_get_ip_list_by_biz_and_user(username,
                                                 biz_cc_id)
        host_id_list = []
        for _ip in ip_list:
            if _ip['InnerIP'] in ip and _ip['HostID'] not in host_id_list:
                ip_result.append({'InnerIP': _ip['InnerIP'],
                                  'HostID': _ip['HostID'],
                                  'Source': _ip['Source'],
                                  'SetID': _ip['SetID'],
                                  'SetName': _ip['SetName'],
                                  'ModuleID': _ip['ModuleID'],
                                  'ModuleName': _ip['ModuleName'],
                                  })
                host_id_list.append(_ip['HostID'])

    valid_ip = [_ip['InnerIP'] for _ip in ip_result]
    invalid_ip = list(set(ip_input_list) - set(valid_ip))
    result = {
        'result': True,
        'ip_result': ip_result,
        'ip_count': len(ip_result),
        'invalid_ip': invalid_ip,
    }
    return result


def cc_get_ip_list_by_biz_and_user(username, biz_cc_id):
    """
    @summary：根据当前用户和业务ID获取IP
    @note: 由于获取了全业务IP，接口会比较慢，需要加缓存
    @note: 由于存在单主机多IP问题，需要取第一个IP作为实际值
    @param-username
    @param-biz_cc_id

    """
    cache_key = "cc_get_ip_list_by_biz_and_user_%s_%s" % (username, biz_cc_id)
    data = cache.get(cache_key)
    if not data:
        client = get_client_by_user(username)
        cc_result = client.cc.get_app_host_list({
            'app_id': biz_cc_id
        })
        if cc_result['result']:
            data = cc_result['data']
            # 多IP主机处理，取第一个IP
            for ip in data:
                if ',' in ip['InnerIP']:
                    ip['InnerIP'] = ip['InnerIP'].split(',')[0]
            cache.set(cache_key, data, 60)
        else:
            logger.warning((u"get_app_host_list ERROR###biz_cc_id=%s"
                            u"###cc_result=%s") % (biz_cc_id,
                                                   json.dumps(cc_result)))
    if not data:
        return []
    return data


def cc_get_role_users(username, biz_cc_id, user_roles, more_users=''):
    """
    @summary: 根据业务和角色获取人员信息
    :param username:
    :param biz_cc_id:
    :param user_roles:
    :param more_users:
    :return:
    """
    client = get_client_by_user(username)
    cc_result = client.cc.get_app_by_id({'app_id': biz_cc_id})
    if not cc_result:
        message = _(u"查询配置平台(CMDB)的业务[app_id=%s]接口cc.get_app_by_id返回失败: %s") % (
            biz_cc_id, cc_result['message'])
        logger.error(message)
        return {
            'result': False,
            'message': message,
            'data': []
        }

    cc_data = cc_result['data'][0]
    for role in user_roles:
        if role in cc_data:
            more_users += ',%s' % cc_data[role]
    users = filter(lambda x: x, re.split(r'\s*[,;\s]\s*', more_users))
    users = list(set(users))
    return {
        'result': True,
        'data': users,
        'messgae': ''
    }


def cc_get_ips_by_set_and_module(username, biz_cc_id, set_id_list, set_name_list,
                                 module_name_list):
    """
    @summary: 根据集群名和模块名获取IP
    :param username:
    :param biz_cc_id:
    :param set_name_list:
    :param module_name_list:
    :return:
    """
    client = get_client_by_user(username)

    if not set_id_list and not set_name_list:
        return []
    if not module_name_list:
        return []

    if set_id_list:
        if '0' in set_id_list:
            set_id_list = []
    else:
        if _(u"所有集群(all)") in set_name_list or 'all' in set_name_list:
            set_id_list = []
        else:
            set_id_list = cc_get_set_ids_by_names(username,
                                                  biz_cc_id,
                                                  set_name_list)
            if not set_id_list:
                return []

    if _(u"所有模块(all)") in module_name_list or 'all' in module_name_list:
        module_name_list = []

    cc_kwargs = {
        'app_id': biz_cc_id,
        'set_id': ','.join(set_id_list),
        'module_name': ','.join(module_name_list),
    }
    cc_result = client.cc.get_hosts_by_property(cc_kwargs)
    result = []
    if cc_result['result']:
        result = cc_result['data']
    else:
        logger.warning(u"client.cc.get_hosts_by_property ERROR###biz_cc_id=%s"
                       u"###cc_result=%s" % (biz_cc_id, json.dumps(cc_result)))
    return result


def cc_get_set_ids_by_names(username, biz_cc_id, set_names):
    """
    @summary: 根据集群名称查询业务在配置平台的集群ID
    :param username:
    :param biz_cc_id:
    :param set_names:
    :return:
    """
    client = get_client_by_user(username)
    cc_result = client.cc.get_sets_by_property({'app_id': biz_cc_id})
    cc_sets = []
    if cc_result['result']:
        cc_sets = cc_result['data']
    else:
        logger.warning(u"client.cc.get_sets_by_property ERROR###biz_cc_id=%s"
                       u"###cc_result=%s" % (biz_cc_id, json.dumps(cc_result)))
    cc_set_names = [_set['SetName'] for _set in cc_sets]
    # 列表格式
    if isinstance(set_names, list):
        set_ids = []
        for set_name in set_names:
            if set_name in cc_set_names:
                set_ids.append(cc_sets[cc_set_names.index(set_name)]['SetID'])
        if len(set_ids) != len(set_names):
            logger.warning(u"cc_get_set_ids_by_names ERROR###error="
                           u"return set less than request set###biz_cc_id=%s"
                           u"###set_names=%s###cc_result=%s" % (
                               biz_cc_id, json.dumps(set_names),
                               json.dumps(cc_result))
                           )
    # 单个集群名称字符串
    else:
        set_ids = ""
        if set_names in cc_set_names:
            set_ids = cc_sets[cc_set_names.index(set_names)]['SetID']
        else:
            logger.warning(u"cc_get_set_ids_by_names ERROR###error="
                           u"return set less than request set###biz_cc_id=%s"
                           u"###set_names=%s###cc_result=%s" % (
                               biz_cc_id, json.dumps(set_names),
                               json.dumps(cc_result))
                           )
    return set_ids


def cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list):
    """
    @summary: 根据模块ID查询主机内网ip
    :param username:
    :param biz_cc_id:
    :param module_id_list:
    :return:
    """
    client = get_client_by_user(username)
    client.set_bk_api_ver('v2')
    cc_kwargs = {
        "bk_biz_id": biz_cc_id,
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


def get_local_file_path_of_time(biz_cc_id, time_str):
    """
    @summary: 根据业务、时间戳生成实际文件路径
    @param biz_cc_id：
    @param time_str：上传时间
    @return:
    """
    if settings.RUN_MODE == 'PRODUCT':
        prefix = '%s_UPLOAD' % settings.RUN_VER.upper()
    else:
        prefix = '%s_UPLOAD_TEST' % settings.RUN_VER.upper()
    path = '/data/%s/%s/bkupload/%s/%s/' % (
        prefix,
        settings.APP_CODE,
        biz_cc_id,
        time_str
    )
    return path

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

from pipeline.conf import settings
from pipeline.exceptions import VariableHydrateException
from pipeline.components.utils import (cc_get_ips_info_by_str,
                                       cc_get_ips_by_set_and_module)
from pipeline.core.data.var import LazyVariable
from pipeline.variables.sites.utils import get_ip_by_zoneid


logger = logging.getLogger('root')


class VarIpPickerVariable(LazyVariable):
    code = 'var_ip_picker'
    form = '%svariables/var_ip_picker.js' % settings.STATIC_URL

    def get_value(self):
        var_ip_picker = self.value
        username = self.pipeline_data['executor']
        biz_cc_id = self.pipeline_data['biz_cc_id']
        value_type = var_ip_picker['var_ip_value_type']
        ip_list = []
        dns_list = []

        produce_method = var_ip_picker['var_ip_method']
        if produce_method == 'custom':
            custom_value = var_ip_picker['var_ip_custom_value']
            if value_type == 'ip':
                data = cc_get_ips_info_by_str(username, biz_cc_id, custom_value)
                ip_list = data['ip_result']
            elif value_type == 'dns':
                dns_list = custom_value.split('\n')
            else:
                data = re.findall(r"\d+", custom_value)
                kwargs = {
                    "appid": biz_cc_id,
                    "zoneids": ",".join(data),
                    "type": "gamedb",
                }
                ips = get_ip_by_zoneid(kwargs)
                if ips["code"] == 0:  # 请求成功
                    for item in ips["data"].values():
                        dns_list += item['dbs']
                    dns_list = list(set(dns_list))
                else:
                    message = 'gcs get_ip_by_zoneid error: kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                                    json.dumps(ips))
                    logger.error(message)
                    raise VariableHydrateException(message)

        elif produce_method == 'select':
            select_set = var_ip_picker['var_ip_select_set']
            select_module = var_ip_picker['var_ip_select_module']
            # 配置平台暂无DNS相关信息，所以只需要取IP
            if value_type == 'ip':
                ip_list = cc_get_ips_by_set_and_module(
                    username,
                    biz_cc_id,
                    select_set,
                    None,
                    select_module,
                )

        else:
            input_set = var_ip_picker['var_ip_input_set']
            input_module = var_ip_picker['var_ip_input_module']
            set_names = input_set.split(',')
            module_names = input_module.split(',')
            # 配置平台暂无DNS相关信息，所以只需要取IP
            if value_type == 'ip':
                ip_list = cc_get_ips_by_set_and_module(
                    username,
                    biz_cc_id,
                    None,
                    set_names,
                    module_names,
                )

        if value_type == 'ip':
            data = ','.join(['%s:%s' % (ip['Source'], ip['InnerIP'])
                             for ip in ip_list])
        else:
            data = ','.join(dns_list)
        return data

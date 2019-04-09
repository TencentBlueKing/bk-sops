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
import re

from pipeline.conf import settings
from pipeline_plugins.cmdb_ip_picker.utils import get_ip_picker_result
from pipeline_plugins.components.utils import (
    cc_get_ips_info_by_str,
    cc_get_inner_ip_by_module_id,
)
from pipeline_plugins.components.utils.common import ip_re
from pipeline.core.data.var import LazyVariable

logger = logging.getLogger('root')


class VarIpPickerVariable(LazyVariable):
    code = 'var_ip_picker'
    form = '%svariables/sites/%s/var_ip_picker.js' % (settings.STATIC_URL, settings.RUN_VER)

    def get_value(self):
        var_ip_picker = self.value
        username = self.pipeline_data['executor']
        biz_cc_id = self.pipeline_data['biz_cc_id']

        produce_method = var_ip_picker['var_ip_method']
        if produce_method == 'custom':
            custom_value = var_ip_picker['var_ip_custom_value']
            data = cc_get_ips_info_by_str(username, biz_cc_id, custom_value)
            ip_list = data['ip_result']
            data = ','.join([ip['InnerIP'] for ip in ip_list])
        else:
            ip_pattern = re.compile(ip_re)
            supplier_account = self.pipeline_data['biz_supplier_account']
            module_id_list = var_ip_picker['var_ip_tree']
            module_inst_id_list = []
            tree_ip_list = []
            for custom_id in module_id_list:
                try:
                    ip_or_module_id = custom_id.split('_')[-1]
                    if ip_pattern.match(ip_or_module_id):
                        # select certain ip
                        tree_ip_list.append(ip_or_module_id)
                    else:
                        # select whole module
                        module_inst_id_list.append(int(ip_or_module_id))
                except Exception:
                    logger.warning('ip_picker module ip transit failed: {origin}'.format(origin=custom_id))

            # query cc to get module's ip list and filter tree_ip_list
            host_list = cc_get_inner_ip_by_module_id(username, biz_cc_id, module_inst_id_list, supplier_account)
            cc_ip_list = cc_get_ips_info_by_str(username, biz_cc_id, ','.join(tree_ip_list))['ip_result']
            select_ip = set()

            for host_info in host_list:
                select_ip.add(host_info['host']['bk_host_innerip'])

            for ip_info in cc_ip_list:
                select_ip.add(ip_info['InnerIP'])

            data = ','.join(list(set(select_ip)))

        return data


class VarCmdbIpSelector(LazyVariable):
    code = 'var_cmdb_ip_selector'
    form = '%svariables/sites/%s/var_cmdb_ip_selector.js' % (settings.STATIC_URL, settings.RUN_VER)

    def get_value(self):
        username = self.pipeline_data['executor']
        bk_biz_id = self.pipeline_data['biz_cc_id']
        bk_supplier_account = self.pipeline_data['biz_supplier_account']

        value = self.value
        ip_result = get_ip_picker_result(username, bk_biz_id, bk_supplier_account, value)
        ip = ','.join([host['bk_host_innerip'] for host in ip_result['data']])
        return ip

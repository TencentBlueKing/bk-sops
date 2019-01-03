# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging

from pipeline.conf import settings
from pipeline.components.utils import (cc_get_ips_info_by_str,
                                       cc_get_inner_ip_by_module_id)
from pipeline.core.data.var import LazyVariable
from pipeline.components.utils import get_ip_by_regex


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
            data = ','.join(['%s:%s' % (ip['Source'], ip['InnerIP'])for ip in ip_list])
        else:
            select_data = var_ip_picker['var_ip_tree']
            select_module = map(lambda x: int(x.split("_")[1]), filter(lambda x: x.split("_")[0] == "module", select_data))
            if select_module:
                ip_result = cc_get_inner_ip_by_module_id(
                    username,
                    biz_cc_id,
                    select_module
                )
                select_module_ip = map(lambda x: x['host']['bk_host_innerip'], ip_result)
            else:
                select_module_ip = []
            select_ip = map(lambda x: get_ip_by_regex(x)[0], filter(lambda x: get_ip_by_regex(x), select_data))
            data = ','.join(list(set(select_ip + select_module_ip)))

        return data

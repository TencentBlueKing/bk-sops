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
from pipeline.core.flow.io import StringItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.utils import get_ip_by_regex
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import cc_format_prop_data, cc_get_host_id_by_innerip

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCUpdateHostService(Service):

    def inputs_format(self):
        return [
            self.InputItem(name=_('业务 ID'),
                           key='biz_cc_id',
                           type='string',
                           schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
            self.InputItem(name=_('主机内网 IP'),
                           key='cc_host_ip',
                           type='string',
                           schema=StringItemSchema(description=_('待转移的主机内网 IP，多个用英文逗号 `,` 分隔'))),
            self.InputItem(name=_('主机属性'),
                           key='cc_host_property',
                           type='string',
                           schema=StringItemSchema(description=_('待修改主机属性'))),
            self.InputItem(name=_('主机属性值'),
                           key='cc_host_prop_value',
                           type='string',
                           schema=StringItemSchema(description=_('更新后的属性值')))]

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
                data.set_outputs('ex_data', _("所属运营商校验失败，请重试并修改为正确的所属运营商"))
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
                data.set_outputs('ex_data', _("所在国家校验失败，请重试并修改为正确的所在国家"))
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
                data.set_outputs('ex_data', _("所在省份校验失败，请重试并修改为正确的所在省份"))
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
            message = cc_handle_api_error('cc.update_host', cc_kwargs, cc_result)
            self.logger.error(message)
            data.set_outputs('ex_data', message)
            return False


class CCUpdateHostComponent(Component):
    name = _("更新主机属性")
    code = 'cc_update_host'
    bound_service = CCUpdateHostService
    form = '%scomponents/atoms/cc/cc_update_host.js' % settings.STATIC_URL

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
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import cc_format_tree_mode_id, cc_format_prop_data

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCCreateSetService(Service):

    def inputs_format(self):
        return [self.InputItem(name=_('业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(name=_('父实例'),
                               key='cc_set_parent_select',
                               type='array',
                               schema=ArrayItemSchema(description=_('父实例 ID 列表'),
                                                      item_schema=IntItemSchema(description=_('实例 ID')))),
                self.InputItem(name=_('集群信息'),
                               key='cc_set_info',
                               type='array',
                               schema=ArrayItemSchema(description=_('新集群信息对象列表'),
                                                      item_schema=ObjectItemSchema(description=_('集群信息描述对象'),
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
                            data.set_outputs('ex_data', _("环境类型校验失败，请重试并修改为正确的环境类型"))
                            return False

                    elif key == "bk_service_status":
                        value = bk_service_status['data'].get(value)
                        if not value:
                            data.set_outputs('ex_data', _("服务状态校验失败，请重试并修改为正确的服务状态"))
                            return False

                    elif key == "bk_capacity":
                        try:
                            value = int(value)
                        except Exception:
                            self.logger.error(traceback.format_exc())
                            data.set_outputs('ex_data', _("集群容量必须为整数"))
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
                    message = cc_handle_api_error('cc.create_set', cc_kwargs, cc_result)
                    self.logger.error(message)
                    data.set_outputs('ex_data', message)
                    return False

        return True


class CCCreateSetComponent(Component):
    name = _("创建集群")
    code = 'cc_create_set'
    bound_service = CCCreateSetService
    form = '%scomponents/atoms/cc/create_set/legacy.js' % settings.STATIC_URL

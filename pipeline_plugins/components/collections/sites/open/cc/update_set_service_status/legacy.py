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
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import cc_format_tree_mode_id

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCUpdateSetServiceStatusService(Service):

    def inputs_format(self):
        return [self.InputItem(name=_('业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(name=_('集群列表'),
                               key='cc_set_select',
                               type='array',
                               schema=ArrayItemSchema(description=_('需要清空的集群 ID 列表'),
                                                      item_schema=IntItemSchema(description=_('集群 ID')))),
                self.InputItem(name=_('服务状态'),
                               key='cc_set_status',
                               type='string',
                               schema=StringItemSchema(description=_('集群服务器状态，开放(1)或关闭(2)'),
                                                       enum=['1', '2']))]

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
        cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_select'))

        for set_id in cc_set_select:
            cc_kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account,
                "bk_set_id": set_id,
                "data": {
                    "bk_service_status": data.get_one_of_inputs('cc_set_status')
                }
            }
            cc_result = client.cc.update_set(cc_kwargs)
            if not cc_result['result']:
                message = cc_handle_api_error('cc.update_set', cc_kwargs, cc_result)
                self.logger.error(message)
                data.set_outputs('ex_data', message)
                return False
        return True


class CCUpdateSetServiceStatusComponent(Component):
    name = _("修改集群服务状态")
    code = 'cc_update_set_service_status'
    bound_service = CCUpdateSetServiceStatusService
    form = '%scomponents/atoms/cc/cc_update_set_service_status.js' % settings.STATIC_URL

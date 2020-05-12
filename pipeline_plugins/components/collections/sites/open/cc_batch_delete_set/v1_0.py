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
from pipeline_plugins.components.collections.sites.open.cc import (
    cc_format_tree_mode_id,
    cc_parse_textarea_path,
    cc_list_match_node_inst_id
)

from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = 'v1.0'

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCBatchDeleteSetService(Service):

    def inputs_format(self):
        return [self.InputItem(name=_('业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(
                    name=_(u'填参方式'),
                    key="cc_set_select_method",
                    type="string",
                    schema=StringItemSchema(description=_(u'模块填入方式，拓扑(topo)，层级文本(text)'),
                                            enum=["topo", "text"])),
                self.InputItem(name=_('拓扑 -集群列表'),
                               key='cc_set_select_topo',
                               type='array',
                               schema=ArrayItemSchema(description=_('需要清空的集群 ID 列表'),
                                                      item_schema=IntItemSchema(description=_('集群 ID')))),
                self.InputItem(name=_(u'文本路径 -模块'),
                               key='cc_set_select_text',
                               type='string',
                               schema=StringItemSchema(description=_(u'模块文本路径')))]

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
        cc_set_select_method = data.get_one_of_inputs('cc_set_select_method')
        cc_set_select = []

        if cc_set_select_method == 'topo':
            cc_set_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_select_topo'))
        elif cc_set_select_method == 'text':
            kwargs = {
                "bk_biz_id": biz_cc_id,
                "bk_supplier_account": supplier_account
            }
            topo_tree = client.cc.search_biz_inst_topo(kwargs)
            if not topo_tree['result']:
                message = cc_handle_api_error('cc.search_biz_inst_topo', kwargs, topo_tree)
                self.logger.error(message)
                data.set_outputs('ex_data', message)
                return False
            # 文本路径解析
            cc_set_select_text = data.get_one_of_inputs('cc_set_select_text')
            path_list = cc_parse_textarea_path(textarea_path=cc_set_select_text)

            # 获取主线模型业务拓扑
            mainline = client.cc.get_mainline_object_topo({'bk_supplier_account': supplier_account})
            # 主线模型中集群所处的深度（包含集群）= 主线模型的业务拓扑级数 - 主机/模块（2）
            set_depth = len(mainline['data']) - 2
            for path in path_list:
                if len(path) != set_depth:
                    data.set_outputs('ex_data', '输入文本路径[{}]与业务拓扑层级不匹配'.format('>'.join(path)))
                    return False
            # 获取集群bk_inst_id
            cc_list_match_node_inst_id_result = cc_list_match_node_inst_id(topo_tree['data'], path_list)
            if cc_list_match_node_inst_id_result['result']:
                cc_set_select = cc_list_match_node_inst_id_result['data']
            else:
                data.set_outputs('ex_data', cc_list_match_node_inst_id_result['message'])
                return False
        else:
            data.set_outputs('ex_data', u'请选择填参方式')
        cc_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_supplier_account": supplier_account,
            "delete": {
                "inst_ids": cc_set_select
            }
        }
        cc_result = client.cc.batch_delete_set(cc_kwargs)
        if not cc_result['result']:
            message = cc_handle_api_error('cc.batch_delete_set', cc_kwargs, cc_result)
            self.logger.error(message)
            data.set_outputs('ex_data', message)
            return False
        return True


class CCBatchDeleteSetComponent(Component):
    name = _("删除集群")
    code = 'cc_batch_delete_set'
    bound_service = CCBatchDeleteSetService
    form = '{static_url}components/atoms/cc/{ver}/cc_batch_delete_set.js'.format(static_url=settings.STATIC_URL,
                                                                                 ver=VERSION)
    version = VERSION

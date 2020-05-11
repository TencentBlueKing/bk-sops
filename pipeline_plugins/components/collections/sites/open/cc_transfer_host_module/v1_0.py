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
    cc_get_host_id_by_innerip,
    cc_format_tree_mode_id,
    cc_parse_textarea_path,
    cc_list_match_node_inst_id
)

from pipeline_plugins.components.utils import get_ip_by_regex
from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = 'v1.0'

cc_handle_api_error = partial(handle_api_error, __group_name__)


class CCTransferHostModuleService(Service):

    def inputs_format(self):
        return [
            self.InputItem(name=_(u'业务 ID'),
                           key='biz_cc_id',
                           type='string',
                           schema=StringItemSchema(description=_(u'当前操作所属的 CMDB 业务 ID'))),
            self.InputItem(
                name=_(u'填参方式'),
                key="cc_module_select_method",
                type="string",
                schema=StringItemSchema(description=_(u'模块填入方式，拓扑(topo)，层级文本(text)'),
                                        enum=["topo", "text"])),
            self.InputItem(name=_(u'主机内网 IP'),
                           key='cc_host_ip',
                           type='string',
                           schema=StringItemSchema(description=_('待转移的主机内网 IP，多个用英文逗号 `,` 分隔'))),
            self.InputItem(name=_(u'拓扑 -模块'),
                           key='cc_module_select_topo',
                           type='array',
                           schema=ArrayItemSchema(description=_(u'转移目标模块 ID 列表'),
                                                  item_schema=IntItemSchema(description=_(u'模块 ID')))),
            self.InputItem(name=_(u'文本路径 -模块'),
                           key='cc_module_select_text',
                           type='string',
                           schema=StringItemSchema(description=_(u'模块文本路径'))),
            self.InputItem(name=_(u'转移方式'),
                           key='cc_is_increment',
                           type='string',
                           schema=StringItemSchema(description=_(u'主机转移方式，覆盖(false)或追加(true)'),
                                                   enum=['false', 'true'])),
        ]

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
        # 获取主机id列表
        host_result = cc_get_host_id_by_innerip(executor, biz_cc_id, ip_list, supplier_account)
        if not host_result['result']:
            data.set_outputs('ex_data', host_result['message'])
            return False

        cc_is_increment = data.get_one_of_inputs('cc_is_increment')
        cc_module_select_method = data.get_one_of_inputs('cc_module_select_method')
        # 选择的模块id列表
        cc_module_select = []
        if cc_module_select_method == 'topo':
            cc_module_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_module_select_topo'))
        elif cc_module_select_method == 'text':
            # 文本路径解析
            cc_module_select_text = data.get_one_of_inputs('cc_module_select_text')
            path_list = cc_parse_textarea_path(textarea_path=cc_module_select_text)

            # 获取主线模型业务拓扑
            mainline = client.cc.get_mainline_object_topo({'bk_supplier_account': supplier_account})
            # 主线模型中模块所处的深度（包含模块）= 主线模型的业务拓扑级数 - 主机（1）
            module_depth = len(mainline['data']) - 1

            for path in path_list:
                if len(path) != module_depth:
                    data.set_outputs('ex_data', '输入文本路径[{}]与业务拓扑层级不匹配'.format('>'.join(path)))
                    return False
            # 获取业务拓扑
            topo_tree = client.cc.search_biz_inst_topo({
                'bk_biz_id': biz_cc_id,
                'bk_supplier_account': supplier_account,
            })['data']
            # 获取模块bk_inst_id
            cc_list_match_node_inst_id_result = cc_list_match_node_inst_id(topo_tree, path_list)
            if cc_list_match_node_inst_id_result['result']:
                cc_module_select = cc_list_match_node_inst_id_result['data']
            else:
                data.set_outputs('ex_data', cc_list_match_node_inst_id_result['message'])
                return False

        else:
            data.set_outputs('ex_data', u'请选择填参方式')

        cc_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_supplier_account": supplier_account,
            "bk_host_id": [int(host_id) for host_id in host_result['data']],
            "bk_module_id": cc_module_select,
            "is_increment": True if cc_is_increment == 'true' else False
        }
        cc_result = client.cc.transfer_host_module(cc_kwargs)
        if cc_result['result']:
            return True
        else:
            message = cc_handle_api_error('cc.transfer_host_module', cc_kwargs, cc_result)
            self.logger.error(message)
            data.set_outputs('ex_data', message)
            return False


class CCTransferHostModuleComponent(Component):
    """
    @version log（v1.0）: 支持以文本路径形式选择模块，并提供相应输入容错： 冗余回车/换行
    """
    name = _(u"转移主机模块")
    code = 'cc_transfer_host_module'
    bound_service = CCTransferHostModuleService
    form = '%scomponents/atoms/cc/cc_transfer_host_module.js' % settings.STATIC_URL
    form = '{static_url}components/atoms/cc/{ver}/cc_transfer_host_module.js'.format(static_url=settings.STATIC_URL,
                                                                                     ver=VERSION)
    version = VERSION

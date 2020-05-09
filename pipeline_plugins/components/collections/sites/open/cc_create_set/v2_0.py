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
from copy import deepcopy

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, ArrayItemSchema, IntItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.collections.sites.open.cc import (
    cc_format_tree_mode_id,
    cc_format_prop_data,
    cc_parse_textarea_path
)
from pipeline_plugins.base.utils.inject import supplier_account_for_business

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _("配置平台(CMDB)")
VERSION = 'v2.0'
BREAK_LINE = '\n'

cc_handle_api_error = partial(handle_api_error, __group_name__)


def chunk_table_data(column):
    """
    @summary: 表格参数值支持以换行符 `\n` 分隔的多条数据，对一行数据，当有一列有多条数据时（包含换行符），其他列要么也有相等个数的
        数据（换行符个数相等），要么只有一条数据（不包含换行符，此时表示多条数据此列参数值都相同）
    @param column: 表格单行数据，字典格式
    @return:
    """
    count = 1
    chunk_data = []
    multiple_keys = []
    for key, value in column.items():
        if not isinstance(value, str):
            return {'result': False, 'message': _("数据[%s]格式错误，请改为字符串") % value, 'data': []}
        value = value.strip()
        if BREAK_LINE in value:
            multiple_keys.append(key)
            value = value.split(BREAK_LINE)
            if len(value) != count and count != 1:
                return {'result': False,
                        'message': _("单行数据[%s]的各列换行符个数不一致，请改为一致或者去掉换行符") % value,
                        'data': []}
            count = len(value)
        column[key] = value

    if count == 1:
        return {'result': True, 'data': [column], 'message': ''}

    for i in range(count):
        item = deepcopy(column)
        for key in multiple_keys:
            item[key] = column[key][i]
        chunk_data.append(item)
    return {'result': True, 'data': chunk_data, 'message': ''}


class CCCreateSetService(Service):

    def inputs_format(self):
        return [self.InputItem(name=_(u'业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_(u'当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(
                    name=_(u"填参方式"),
                    key="cc_select_set_parent_method",
                    type="string",
                    schema=StringItemSchema(
                        description=_("父实例填入方式，拓扑(topo)，层级文本(text)"),
                        enum=["topo", "text"],
                    ),
                ),
                self.InputItem(name=_(u'拓扑-父实例'),
                               key='cc_set_parent_select_topo',
                               type='array',
                               schema=ArrayItemSchema(description=_(u'父实例 ID 列表'),
                                                      item_schema=IntItemSchema(description=_(u'实例 ID')))),
                self.InputItem(name=_(u'文本路径-父实例'),
                               key='cc_set_parent_select_text',
                               type='string',
                               schema=StringItemSchema(description=_('父实例文本路径'))),
                self.InputItem(name=_(u'集群信息'),
                               key='cc_set_info',
                               type='array',
                               schema=ArrayItemSchema(description=_(u'新集群信息对象列表'),
                                                      item_schema=ObjectItemSchema(description=_(u'集群信息描述对象'),
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
        cc_select_set_parent_method = data.get_one_of_inputs('cc_select_set_parent_method')

        supplier_account = supplier_account_for_business(biz_cc_id)
        cc_set_parent_select = []
        if cc_select_set_parent_method == 'topo':
            # topo类型直接通过cc_format_tree_mode_id解析父节点bz_inst_id
            cc_set_parent_select = cc_format_tree_mode_id(data.get_one_of_inputs('cc_set_parent_select_topo'))
        elif cc_select_set_parent_method == 'text':
            cc_set_parent_select_text = data.get_one_of_inputs('cc_set_parent_select_text')
            # 文本路径解析，example：'a>b>c/n a>b' -> [[a, b, c], [a, b]]
            path_list = cc_parse_textarea_path(textarea_path=cc_set_parent_select_text)
            # 获取主线模型业务拓扑
            mainline = client.cc.get_mainline_object_topo({'bk_supplier_account': supplier_account})['data']
            # 自定义层级数 = 主线模型的业务拓扑级数 - 业务层级数（1） - 集群/模块/主机（3）
            custom_level_length = len(mainline) - 4

            for path in path_list:
                # 输入路径中自定义层级数 = 主线模型业务拓扑的自定义层级数
                if len(path) - 1 != custom_level_length:
                    data.set_outputs('ex_data', '输入文本路径[{}]与业务层级拓扑层级不匹配'.format('>'.join(path)))
                    return False
            # 获取业务拓扑
            topo_tree = client.cc.search_biz_inst_topo({
                'bk_biz_id': biz_cc_id,
                'bk_supplier_account': supplier_account,
            })['data']

            # 路径匹配，匹配父节点并将父节点的bk_inst_id加入cc_set_parent_select
            for path in path_list:
                begin = 0
                topo_node_list = topo_tree
                while len(path) > begin:
                    match_node = None
                    for topo_node in topo_node_list:
                        if path[begin] == topo_node['bk_inst_name']:
                            match_node = topo_node
                            break
                    if match_node:
                        begin = begin + 1
                        # 匹配到最后一层自定义层级，记录该层级的bk_inst_id
                        if begin == len(path):
                            cc_set_parent_select.append(match_node['bk_inst_id'])
                        topo_node_list = match_node['child']
                    else:
                        data.set_outputs('ex_data', '不存在该拓扑路径：{}'.format('>'.join(path)))
                        return False
        else:
            data.set_outputs('ex_data', u'请选择填参方式')

        cc_set_info = deepcopy(data.get_one_of_inputs('cc_set_info'))

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
            chunk_result = chunk_table_data(set_params)
            if not chunk_result['result']:
                data.set_outputs('ex_data', chunk_result['message'])
                return False

            for property_data in chunk_result['data']:
                set_property = {}
                for key, value in property_data.items():
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
                            except ValueError:
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
    """
    @version log（v2.0）:在v1.0基础上，支持以文本路径形式选择所增加集群的父节点，并提供相应输入容错： 冗余回车/换行
    """
    name = _(u"创建集群")
    code = 'cc_create_set'
    bound_service = CCCreateSetService
    form = '{static_url}components/atoms/cc/{ver}/cc_create_set.js'.format(static_url=settings.STATIC_URL,
                                                                           ver=VERSION)
    version = VERSION

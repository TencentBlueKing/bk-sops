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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pipeline.core.data.var import LazyVariable
from pipeline.core.flow.io import StringItemSchema

logger = logging.getLogger('root')


class DataTableValue(object):
    def __init__(self, data):
        self.value = data
        item_values = {}
        for item in data:
            for key, val in item.items():
                item_values.setdefault(key, []).append(val)
        for attr, attr_val in item_values.items():
            setattr(self, attr, attr_val)
            flat_val = '\n'.join(map(str, attr_val))
            setattr(self, 'flat__{}'.format(attr), flat_val)


class DataTable(LazyVariable):
    code = 'datatable'
    name = _("表格")
    type = 'meta'
    tag = 'datatable.datatable'
    meta_tag = 'datatable.datatable_meta'
    form = '%svariables/%s.js' % (settings.STATIC_URL, code)
    schema = StringItemSchema(description=_('表格变量'))

    def get_value(self):
        return DataTableValue(self.value)

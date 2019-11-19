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

from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.data.var import LazyVariable


logger = logging.getLogger('root')


class BkUserSelector(LazyVariable):
    code = 'bk_user_selector'
    name = _("人员选择器")
    type = 'general'
    tag = 'bk_manage_user_selector.bk_user_selector'
    form = '%svariables/bk_manage_user_selector.js' % settings.STATIC_URL

    def get_value(self):
        return self.value

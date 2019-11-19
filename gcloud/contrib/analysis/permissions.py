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

from django.utils.translation import ugettext_lazy as _

from auth_backend.backends import get_backend_from_config
from auth_backend.resources.base import Action, NeverInitiateResource

statistics_resource = NeverInitiateResource(
    rtype='statistics',
    name=_("统计数据"),
    scope_type='system',
    scope_id='bk_sops',
    scope_name=_("标准运维"),
    actions=[Action(id='view', name=_("查看"), is_instance_related=False)],
    backend=get_backend_from_config())

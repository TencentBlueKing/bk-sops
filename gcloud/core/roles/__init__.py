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

import importlib

from django.conf import settings

roles = importlib.import_module('gcloud.core.roles.sites.%s.roles' % settings.RUN_VER)

export_var = ['ROLES_DECS',
              'ALL_ROLES',
              'ADMIN_ROLES',
              'CC_ROLES',
              'CC_PERSON_GROUP',
              'DEFAULT_CC_NOTIFY_SET',
              'MAINTAINERS',
              'PRODUCTPM',
              'DEVELOPER',
              'TESTER',
              'OWNER',
              'COOPERATION',
              'ADMIN',
              'FUNCTOR',
              'AUDITOR',
              'CC_V2_ROLE_MAP']

for role_var in export_var:
    locals()[role_var] = getattr(roles, role_var)

__all__ = export_var

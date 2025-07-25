# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.translation import gettext_lazy as _

MAINTAINERS = "Maintainers"
PRODUCTPM = "ProductPm"
DEVELOPER = "Developer"
TESTER = "Tester"
OWNER = "Owner"
COOPERATION = "Cooperation"
ADMIN = "Admin"
FUNCTOR = "Functor"  # 职能化人员
AUDITOR = "Auditor"
NORMAL = "Normal"

ROLES_DECS = {
    MAINTAINERS: _("运维人员"),
    PRODUCTPM: _("产品人员"),
    COOPERATION: _("合作商"),
    OWNER: _("业务创建人"),
    ADMIN: _("超级管理员"),
    FUNCTOR: _("职能化人员"),
    TESTER: _("测试人员"),
    DEVELOPER: _("开发人员"),
    AUDITOR: _("审计人员"),
}

ALL_ROLES = [
    MAINTAINERS,
    PRODUCTPM,
    DEVELOPER,
    TESTER,
    OWNER,
    ADMIN,
    FUNCTOR,
    AUDITOR,
]


ADMIN_ROLES = [
    MAINTAINERS,
    OWNER,
]

CC_ROLES = [
    MAINTAINERS,
    PRODUCTPM,
    DEVELOPER,
    TESTER,
]

# 默认通知分组
CC_PERSON_GROUP = [{"value": role, "text": ROLES_DECS[role]} for role in CC_ROLES]

DEFAULT_CC_NOTIFY_SET = (MAINTAINERS,)

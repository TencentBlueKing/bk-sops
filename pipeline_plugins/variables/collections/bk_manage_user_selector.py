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

import logging
from typing import List

from django.utils.translation import gettext_lazy as _
from pipeline.conf import settings
from pipeline.core.data.var import LazyVariable

from gcloud.constants import Type
from packages.bkapi.bk_user.shortcuts import get_client_by_username
from pipeline_plugins.variables.base import FieldExplain, SelfExplainVariable

logger = logging.getLogger("root")


class BkUserSelector(LazyVariable, SelfExplainVariable):
    code = "bk_user_selector"
    name = _("人员选择器")
    type = "general"
    tag = "bk_manage_user_selector.bk_user_selector"
    form = "%svariables/bk_manage_user_selector.js" % settings.STATIC_URL

    def get_value(self):
        client = get_client_by_username(self.value, stage=settings.BK_APIGW_STAGE_NAME)
        response = client.api.display_info(
            {"bk_usernames": self.value}, headers={"X-Bk-Tenant-Id": self.pipeline_data["tenant_id"]}
        )
        user_list = response.get("data") or []
        display_names = [user.get("display_name") for user in user_list]
        return ",".join(display_names)

    @classmethod
    def _self_explain(cls, **kwargs) -> List[FieldExplain]:
        return [FieldExplain(key="${KEY}", type=Type.STRING, description="人员列表，以,分隔")]

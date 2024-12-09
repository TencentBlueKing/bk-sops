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
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield.base import MonitorAlarmShieldServiceBase

__group_name__ = _("监控平台(Monitor)")


class MonitorAlarmShieldService(MonitorAlarmShieldServiceBase):
    def get_scope_value(self, bk_biz_id, scope_type, combine):
        scope = {"IP": "bk_alarm_shield_IP", "node": "bk_alarm_shield_node"}
        if scope_type == "business":
            scope_value = bk_biz_id
        else:
            scope_value = combine.get(scope[scope_type])

        return scope_value


class MonitorAlarmShieldComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按范围)")
    code = "monitor_alarm_shield"
    bound_service = MonitorAlarmShieldService
    form = "{static_url}components/atoms/monitor/alarm_shield/v1_2.js".format(static_url=settings.STATIC_URL)
    version = "1.2"
    desc = _(
        "注意： 1.屏蔽方案选择自定义监控时，屏蔽范围CC大区和集群必须选择all, 2.当按业务屏蔽时，使用当前项目选择的业务值"
    )

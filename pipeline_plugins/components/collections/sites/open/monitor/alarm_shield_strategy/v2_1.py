# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.component import Component

from gcloud.conf import settings
from pipeline_plugins.components.collections.sites.open.monitor.alarm_shield_strategy.v2_0 import (
    MonitorAlarmShieldStrategyService as MonitorAlarmShieldStrategyServiceV2,
)
from pipeline_plugins.components.collections.sites.open.monitor.end_policy import ShieldEndPolicyMixin

__group_name__ = _("监控平台(Monitor)")


class MonitorAlarmShieldStrategyService(ShieldEndPolicyMixin, MonitorAlarmShieldStrategyServiceV2):
    pass


class MonitorAlarmShieldStrategyComponent(Component):
    name = _("蓝鲸监控告警屏蔽(按策略)")
    code = "monitor_alarm_shield_strategy"
    bound_service = MonitorAlarmShieldStrategyService
    form = "{static_url}components/atoms/monitor/alarm_shield_strategy/v2_1.js".format(static_url=settings.STATIC_URL)
    version = "2.1"
    desc = _("按策略屏蔽，新增结束处理方式 end_policy（默认 notify_once）")

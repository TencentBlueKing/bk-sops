# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.io import StringItemSchema


class ShieldEndPolicyMixin:
    """仅供支持结束处理方式的新版本屏蔽插件使用。"""

    def inputs_format(self):
        return super().inputs_format() + [
            self.InputItem(
                name=_("屏蔽结束处理方式"),
                key="bk_alarm_shield_end_policy",
                type="string",
                schema=StringItemSchema(description=_("notify_once：结束后补发一次通知；close：结束时关闭期间告警")),
            )
        ]

    def send_request(self, tenant_id, request_body, data, client):
        end_policy = data.get_one_of_inputs("bk_alarm_shield_end_policy") or "notify_once"
        if end_policy not in ("notify_once", "close"):
            message = _("屏蔽结束处理方式仅支持 notify_once 或 close")
            self.logger.error(message)
            data.set_outputs("ex_data", message)
            return False
        request_body["end_policy"] = end_policy
        return super().send_request(tenant_id, request_body, data, client)

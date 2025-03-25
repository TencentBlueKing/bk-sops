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

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcloud import err_code
from gcloud.template_base.models import BaseTemplate, BaseTemplateManager
from gcloud.template_base.utils import fill_default_version_to_service_activities

logger = logging.getLogger("root")


class CommonTemplateManager(BaseTemplateManager):
    def import_operation_check(self, template_data):
        data = super(CommonTemplateManager, self).import_operation_check(template_data)

        # business template cannot override common template
        has_business_template = any(
            [tmpl.get("business_id") or tmpl.get("project_id") for _, tmpl in list(template_data["template"].items())]
        )
        if has_business_template:
            data["can_override"] = False
            data["override_template"] = []
        return data

    def export_templates(self, template_id_list, **kwargs):
        if kwargs.get("is_full"):
            template_id_list = list(self.all().values_list("id", flat=True))
        return super().export_templates(template_id_list, **kwargs)

    def import_templates(self, template_data, override, operator=None):
        check_info = self.import_operation_check(template_data)

        for template in template_data["pipeline_template_data"]["template"].values():
            fill_default_version_to_service_activities(template["tree"])

        # operation validation check
        if override and (not check_info["can_override"]):
            message = _("流程导入失败, 不能使用项目流程覆盖公共流程, 请检查后重试 | import_templates")
            logger.error(message)
            return {"result": False, "message": message, "data": 0, "code": err_code.INVALID_OPERATION.code}

        def defaults_getter(template_dict):
            return {
                "category": template_dict["category"],
                "notify_type": template_dict["notify_type"],
                "notify_receivers": template_dict["notify_receivers"],
                "time_out": template_dict["time_out"],
                "pipeline_template_id": template_dict["pipeline_template_id"],
                "is_deleted": False,
            }

        return super(CommonTemplateManager, self)._perform_import(
            template_data=template_data,
            check_info=check_info,
            override=override,
            defaults_getter=defaults_getter,
            operator=operator,
        )


class CommonTemplate(BaseTemplate):
    """
    @summary: common templates maintained by admin, which all businesses could use to creating tasks
    """

    tenant_id = models.CharField(_("租户ID"), default="default", max_length=64, db_index=True)

    objects = CommonTemplateManager()

    class Meta(BaseTemplate.Meta):
        verbose_name = _("公共流程模板 CommonTemplate")
        verbose_name_plural = _("公共流程模板 CommonTemplate")

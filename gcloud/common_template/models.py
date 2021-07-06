# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.translation import ugettext_lazy as _

from gcloud import err_code
from gcloud.constants import TEMPLATE_EXPORTER_SOURCE_COMMON
from gcloud.template_base.models import BaseTemplateManager, BaseTemplate


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

    def import_templates(self, template_data, override, operator=None):
        check_info = self.import_operation_check(template_data)

        # operation validation check
        if override and (not check_info["can_override"]):
            return {
                "result": False,
                "message": "Unable to override common flows or keep ID when importing business flows data",
                "data": 0,
                "code": err_code.INVALID_OPERATION.code,
            }

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

    def export_templates(self, template_id_list):
        data = super(CommonTemplateManager, self).export_templates(template_id_list)
        data["template_source"] = TEMPLATE_EXPORTER_SOURCE_COMMON
        return data


class CommonTemplate(BaseTemplate):
    """
    @summary: common templates maintained by admin, which all businesses could use to creating tasks
    """

    objects = CommonTemplateManager()

    class Meta(BaseTemplate.Meta):
        verbose_name = _("公共流程模板 CommonTemplate")
        verbose_name_plural = _("公共流程模板 CommonTemplate")

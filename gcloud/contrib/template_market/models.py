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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from gcloud import err_code


class TemplateSharedManager(models.Manager):
    def update_shared_record(self, new_template_ids, market_record_id, project_id, creator, existing_template_ids=None):
        market_record_id = int(market_record_id)

        if existing_template_ids:
            templates_to_remove = existing_template_ids - set(new_template_ids)
            if templates_to_remove:
                for template_id in templates_to_remove:
                    current_template_record = TemplateSharedRecord.objects.get(template_id=template_id)
                    current_market_ids = current_template_record.extra_info.get("market_record_ids", [])
                    if market_record_id in current_market_ids:
                        current_market_ids.remove(market_record_id)
                        current_template_record.extra_info["market_record_ids"] = current_market_ids
                        current_template_record.save()
                        if not current_template_record.extra_info["market_record_ids"]:
                            current_template_record.delete()
                    else:
                        return {
                            "result": False,
                            "message": "template {} is not in record {}".format(template_id, market_record_id),
                            "code": err_code.REQUEST_PARAM_INVALID.code,
                        }

            templates_to_add = set(new_template_ids) - existing_template_ids
            if templates_to_add:
                new_template_ids = list(templates_to_add)

        new_records = []
        for template_id in new_template_ids:
            existing_record, created = TemplateSharedRecord.objects.get_or_create(
                project_id=project_id,
                template_id=template_id,
                defaults={"creator": creator, "extra_info": {"market_record_ids": [market_record_id]}},
            )
            if not created:
                market_ids = existing_record.extra_info.setdefault("market_record_ids", [])
                if market_record_id not in market_ids:
                    market_ids.append(market_record_id)
                    new_records.append(existing_record)

        if new_records:
            TemplateSharedRecord.objects.bulk_update(new_records, ["extra_info"])

        return {"result": True, "message": "update shared record successfully", "code": err_code.SUCCESS.code}


class TemplateSharedRecord(models.Model):
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="项目 ID")
    template_id = models.JSONField(_("模板 ID 列表"), help_text="模板 ID 列表", db_index=True)
    creator = models.CharField(_("创建者"), max_length=32, default="")
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    update_at = models.DateTimeField(verbose_name=_("更新时间"), auto_now=True)
    extra_info = models.JSONField(_("额外信息"), blank=True, null=True)

    objects = TemplateSharedManager()

    class Meta:
        verbose_name = _("模板共享记录 TemplateSharedRecord")
        verbose_name_plural = _("模板共享记录 TemplateSharedRecord")

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

TEMPLATE_SHARED_RECORD_BATCH_OPERATION_COUNT = 50


class TemplateSharedManager(models.Manager):
    def update_shared_record(
        self, new_template_ids, market_record_id, project_id, creator, existing_market_template_ids=None
    ):
        market_record_id = int(market_record_id)

        if existing_market_template_ids:
            ids_to_delete = []
            templates_to_remove = existing_market_template_ids - set(new_template_ids)
            current_template_records = TemplateSharedRecord.objects.filter(
                project_id=project_id, template_id__in=templates_to_remove
            )
            for current_template_record in current_template_records:
                market_record_ids = current_template_record.extra_info.get("market_record_ids")
                market_record_ids.remove(market_record_id)
                if not market_record_ids:
                    ids_to_delete.append(current_template_record.id)
                current_template_record.save()

            if ids_to_delete:
                TemplateSharedRecord.objects.filter(id__in=ids_to_delete).delete()

            templates_to_add = set(new_template_ids) - existing_market_template_ids
            if templates_to_add:
                new_template_ids = list(templates_to_add)

        new_records = []
        records_to_update = []
        existing_records = TemplateSharedRecord.objects.filter(project_id=project_id, template_id__in=new_template_ids)

        existing_template_ids = {record.template_id: record for record in existing_records}

        for template_id in new_template_ids:
            if template_id in existing_template_ids:
                existing_record = existing_template_ids[template_id]
                market_ids = existing_record.extra_info.setdefault("market_record_ids", [])
                if market_record_id not in market_ids:
                    market_ids.append(market_record_id)
                    records_to_update.append(existing_record)
            else:
                new_record = TemplateSharedRecord(
                    project_id=project_id,
                    template_id=template_id,
                    creator=creator,
                    extra_info={"market_record_ids": [market_record_id]},
                )
                new_records.append(new_record)

        if new_records:
            TemplateSharedRecord.objects.bulk_create(
                new_records, batch_size=TEMPLATE_SHARED_RECORD_BATCH_OPERATION_COUNT
            )

        if records_to_update:
            TemplateSharedRecord.objects.bulk_update(
                records_to_update, ["extra_info"], batch_size=TEMPLATE_SHARED_RECORD_BATCH_OPERATION_COUNT
            )

        return {"result": True, "message": "update shared record successfully", "code": err_code.SUCCESS.code}


class TemplateSharedRecord(models.Model):
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="项目 ID")
    template_id = models.IntegerField(_("模板 ID"), help_text="模板 ID", db_index=True)
    creator = models.CharField(_("创建者"), max_length=32, default="")
    extra_info = models.JSONField(_("额外信息"), blank=True, null=True)

    objects = TemplateSharedManager()

    class Meta:
        verbose_name = _("模板共享记录 TemplateSharedRecord")
        verbose_name_plural = _("模板共享记录 TemplateSharedRecord")

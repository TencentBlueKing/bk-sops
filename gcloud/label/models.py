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

import logging
from collections import defaultdict

from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("root")


class LabelManager(models.Manager):
    def check_label_ids(self, label_ids):
        if len(label_ids) != self.filter(id__in=label_ids).count():
            return False
        return True


class Label(models.Model):
    name = models.CharField(_("标签名称"), max_length=255, db_index=True, help_text="标签名称")
    creator = models.CharField(_("创建者"), max_length=255, help_text="标签创建人")
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="标签对应project id")  # 默认标签时project_id=-1
    is_default = models.BooleanField(_("默认标签"), default=False, help_text="是否是默认标签")
    color = models.CharField(_("标签颜色"), max_length=7, default="#dcffe2", help_text="标签颜色值")
    description = models.CharField(_("标签描述"), max_length=255, blank=True, null=True, help_text="标签描述")

    objects = LabelManager()

    class Meta:
        verbose_name = _("用户标签 Label")
        verbose_name_plural = _("用户标签 Label")
        unique_together = ("project_id", "name")

    def __str__(self):
        return "label name:{}, description:{}".format(self.name, self.description)


class TemplateLabelManager(models.Manager):
    def set_labels_for_template(self, template_id, label_ids):
        existing_labels = self.filter(template_id=template_id).values_list("label_id", flat=True)
        add_labels = list(set(label_ids).difference(set(existing_labels)))
        add_relations = [TemplateLabelRelation(template_id=template_id, label_id=label_id) for label_id in add_labels]
        remove_labels = list(set(existing_labels).difference(set(label_ids)))
        self.filter(template_id=template_id, label_id__in=remove_labels).delete()
        self.bulk_create(add_relations)

    def fetch_labels_for_templates(self, template_ids):
        label_ids = self.filter(template_id__in=template_ids).distinct().values_list("label_id", flat=True)
        labels = Label.objects.filter(id__in=label_ids).values_list("id", "name", "color")
        return labels

    def fetch_templates_labels(self, template_ids, label_fields=("name", "color")):
        select_fields = {field_name: field_name for field_name in label_fields if field_name != "id"}
        relations = (
            self.filter(template_id__in=template_ids)
            .extra(select=select_fields, tables=["label_label"], where=["label_label.id=label_id"])
            .values("template_id", "label_id", *select_fields.values())
        )
        templates_labels = defaultdict(list)
        for relation in relations:
            template_id = relation.pop("template_id")
            templates_labels[template_id].append(relation)
        return dict(templates_labels)

    def fetch_common_labels_for_templates(self, template_ids, label_fields=("name", "color")):
        label_ids = (
            self.filter(template_id__in=template_ids)
            .values_list("label_id", flat=True)
            .annotate(num_labels=Count("label_id"))
            .filter(num_labels=len(template_ids))
        )
        labels = Label.objects.filter(id__in=label_ids).values_list("id", *label_fields)
        return labels

    def fetch_template_ids_using_labels(self, label_ids):
        template_ids = self.filter(label_id__in=label_ids).distinct().values_list("template_id", flat=True)
        return template_ids

    def fetch_template_ids_using_union_labels(self, label_ids):
        template_ids = (
            self.filter(label_id__in=label_ids)
            .values_list("template_id", flat=True)
            .annotate(num_templates=Count("template_id"))
            .filter(num_templates=len(label_ids))
        )
        return template_ids

    def fetch_label_template_ids(self, label_ids):
        relations = self.filter(label_id__in=label_ids)
        label_template_ids = defaultdict(list)
        for relation in relations:
            label_template_ids[relation.label_id].append(relation.template_id)
        return label_template_ids

    def delete_relations_based_on_template(self, template_id):
        self.filter(template_id=template_id).delete()

    def delete_relations_based_on_label(self, label_id):
        self.filter(label_id=label_id).delete()


class TemplateLabelRelation(models.Model):
    template_id = models.IntegerField(_("模版ID"), db_index=True)
    label_id = models.IntegerField(_("标签ID"), db_index=True)

    objects = TemplateLabelManager()

    class Meta:
        verbose_name = _("模版标签关系 TemplateLabelRelation")
        verbose_name_plural = _("模版标签关系 TemplateLabelRelation")
        unique_together = ("template_id", "label_id")

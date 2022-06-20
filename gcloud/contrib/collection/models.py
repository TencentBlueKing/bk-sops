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
import json

from django.db import models
from django.utils.translation import ugettext_lazy as _


class CollectionManager(models.Manager):
    def cascade_delete(self, category, instance_id):
        self.filter(category=category, instance_id=instance_id).delete()

    def get_user_project_collection_category_ids(self, username, project_id, category):
        user_collections = self.filter(category=category, username=username).values()
        collection_template_ids = []
        for user_collection in user_collections:
            extra_info = json.loads(user_collection["extra_info"])
            if int(extra_info["project_id"]) == project_id:
                collection_template_ids.append(user_collection["id"])
        return collection_template_ids


class Collection(models.Model):
    COLLECTION_TYPE = (
        ("flow", _(u"项目流程")),
        ("common_flow", _(u"公共流程")),
        ("periodic_task", _(u"周期任务")),
        ("mini_app", _(u"轻应用")),
    )
    username = models.CharField(_(u"用户名"), max_length=255)
    category = models.CharField(_(u"收藏对象类型"), max_length=255, choices=COLLECTION_TYPE)
    instance_id = models.IntegerField(_(u"收藏对象ID"))
    extra_info = models.TextField(_(u"额外信息"), blank=True)

    objects = CollectionManager()

    class Meta:
        verbose_name = _(u"用户收藏 Collection")
        verbose_name_plural = _(u"用户收藏 Collection")
        index_together = ["category", "instance_id"]

    def __unicode__(self):
        return "%s_%s_%s" % (self.id, self.username, self.category)

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
from django.utils.translation import gettext_lazy as _


class CollectionManager(models.Manager):
    def cascade_delete(self, category, instance_id):
        self.filter(category=category, instance_id=instance_id).delete()

    def add_user_favorite_project(self, username, project):
        return self.get_or_create(
            category="project",
            username=username,
            instance_id=project.id,
            defaults={"extra_info": json.dumps({"id": project.id, "name": project.name})},
        )

    def remove_user_favorite_project(self, username, project_id):
        return self.filter(category="project", username=username, instance_id=project_id).delete()

    def get_user_favorite_projects(self, username):
        return self.filter(category="project", username=username).values_list("instance_id", flat=True)

    def get_user_project_collection_category_ids(self, username, project_id, category):
        user_collections = self.filter(category=category, username=username).values()
        collection_template_ids = []
        for user_collection in user_collections:
            extra_info = json.loads(user_collection["extra_info"])
            if int(extra_info["project_id"]) == project_id:
                collection_template_ids.append(user_collection["id"])
        return collection_template_ids

    def update_collection_info_name(self, category, instance_id, name):
        inst = self.filter(category=category, instance_id=instance_id).first()
        if not inst:
            return
        extra_info = json.loads(inst.extra_info)
        if extra_info.get("name") != name:
            extra_info["name"] = name
            inst.extra_info = json.dumps(extra_info)
            inst.save(update_fields=["extra_info"])

    def get_user_project_collection_instance_info(self, project_id: int, username: str, category: str):
        project_id = int(project_id)
        user_collections = self.filter(category=category, username=username).values()
        instance_ids = []
        instance_collection_mappings = {}
        for user_collection in user_collections:
            extra_info = json.loads(user_collection["extra_info"])
            if int(extra_info["project_id"]) == project_id:
                instance_id = user_collection["instance_id"]
                instance_ids.append(instance_id)
                instance_collection_mappings[instance_id] = user_collection["id"]
        return instance_ids, instance_collection_mappings


class Collection(models.Model):
    COLLECTION_TYPE = (
        ("project", _("项目")),
        ("flow", _("项目流程")),
        ("common_flow", _("公共流程")),
        ("periodic_task", _("周期任务")),
        ("mini_app", _("轻应用")),
    )
    username = models.CharField(_("用户名"), max_length=255)
    category = models.CharField(_("收藏对象类型"), max_length=255, choices=COLLECTION_TYPE)
    instance_id = models.IntegerField(_("收藏对象ID"))
    extra_info = models.TextField(_("额外信息"), blank=True)

    objects = CollectionManager()

    class Meta:
        verbose_name = _("用户收藏 Collection")
        verbose_name_plural = _("用户收藏 Collection")
        index_together = ["category", "instance_id"]

    def __unicode__(self):
        return "%s_%s_%s" % (self.id, self.username, self.category)

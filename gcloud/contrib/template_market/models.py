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


class TemplateSharedRecord(models.Model):
    project_id = models.IntegerField(_("项目 ID"), default=-1, help_text="项目 ID")
    template_id = models.IntegerField(_("模版 ID"), help_text="模版 ID")
    scene_instance_id = models.IntegerField(_("场景实例 ID"), db_index=True, help_text="场景实例 ID")
    creator = models.CharField(_("创建者"), max_length=32, default="")
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    extra_info = models.JSONField(_("额外信息"), blank=True, null=True)

    class Meta:
        verbose_name = _("模板共享记录 TemplateSharedRecord")
        verbose_name_plural = _("模板共享记录 TemplateSharedRecord")

    @classmethod
    def create(cls, project_id, template_id, scene_instance_id, creator="", extra_info=None):
        if not scene_instance_id:
            raise ValueError("场景实例 ID 不能为空")

        instance = cls(
            project_id=project_id,
            template_id=template_id,
            scene_instance_id=scene_instance_id,
            creator=creator,
            extra_info=extra_info,
        )
        instance.save()
        return instance

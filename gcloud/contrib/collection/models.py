# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Collection(models.Model):
    COLLECTION_TYPE = (
        ("flow", _(u"项目流程")),
        ("common_flow", _(u"公共流程")),
        ("periodic_task", _(u"周期任务")),
        ("mini_app", _(u"轻应用")),
    )
    username = models.CharField(_(u"用户名"), max_length=255)
    category = models.CharField(_(u"收藏对象类型"), max_length=255, choices=COLLECTION_TYPE)
    extra_info = models.TextField(_(u"额外信息"), blank=True)

    class Meta:
        verbose_name = _(u"用户收藏 Collection")
        verbose_name_plural = _(u"用户收藏 Collection")

    def __unicode__(self):
        return "%s_%s_%s" % (self.id, self.username, self.category)

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone


class BusinessManager(models.Manager):
    def supplier_account_for_business(self, cc_id):
        return self.get(cc_id=cc_id).cc_owner

    def supplier_id_for_business(self, cc_id):
        return self.get(cc_id=cc_id).cc_company or 0


class Business(models.Model):
    cc_id = models.IntegerField(unique=True)
    cc_name = models.CharField(max_length=256)
    # 开发商账号 bk_supplier_account
    cc_owner = models.CharField(max_length=100)
    # 开发商ID bk_supplier_id
    cc_company = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100, blank=True)
    # LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是非法值
    life_cycle = models.CharField(_(u"生命周期"), max_length=100, blank=True)
    executor = models.CharField(_(u"任务执行者"), max_length=100, blank=True)
    # null 表未归档，disabled 表示已归档
    status = models.CharField(_(u"业务状态"), max_length=32, null=True)
    always_use_executor = models.BooleanField(_(u"是否始终使用任务执行者"), default=False)

    groups = models.ManyToManyField(
        Group,
        through='BusinessGroupMembership'
    )

    objects = BusinessManager()

    class Meta:
        verbose_name = _(u"业务 Business")
        verbose_name_plural = _(u"业务 Business")
        permissions = (
            ("view_business", "Can view business"),
            ("manage_business", "Can manage business"),
        )

    def __unicode__(self):
        return u"%s_%s" % (self.cc_id, self.cc_name)


class UserBusiness(models.Model):
    """
    用户默认业务表
    """
    user = models.CharField(_(u"用户QQ"), max_length=255, unique=True)
    default_buss = models.IntegerField(_(u"默认业务"))

    def __unicode__(self):
        return u'%s_%s' % (self.user, self.default_buss)

    class Meta:
        verbose_name = _(u"用户默认业务 UserBusiness")
        verbose_name_plural = _(u"用户默认业务 UserBusiness")


class BusinessGroupMembership(models.Model):
    business = models.ForeignKey(Business)
    group = models.ForeignKey(Group)

    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _(u"业务用户组 BusinessGroupMembership")
        verbose_name_plural = _(u"业务用户组 BusinessGroupMembership")
        unique_together = ('business', 'group')

    def __unicode__(self):
        return u"B%s:G%s" % (self.business_id, self.group_id)


class EnvVarManager(models.Manager):

    def get_var(self, key):
        objs = self.filter(key=key)
        if objs.exists():
            return objs[0].value
        return None


class EnvironmentVariables(models.Model):
    key = models.CharField(_(u"变量KEY"), max_length=255, unique=True)
    name = models.CharField(_(u"变量描述"), max_length=255, blank=True)
    value = models.CharField(_(u"变量值"), max_length=1000, blank=True)

    objects = EnvVarManager()

    def __unicode__(self):
        return u"%s_%s" % (self.key, self.name)

    class Meta:
        verbose_name = _(u"环境变量 EnvironmentVariables")
        verbose_name_plural = _(u"环境变量 EnvironmentVariables")

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

from django.db import models
from django.utils import timezone


class BkWeixinUserManager(models.Manager):
    def create_user(self, openid, **extra_fields):
        now = timezone.now()
        if not openid:
            raise ValueError('The given openid must be set')
        user = self.model(openid=openid, date_joined=now, **extra_fields)
        user.save()
        return user

    def get_update_or_create_user(self, openid, **extra_fields):
        """
        获取用户，无则创建，有则更新
        """
        try:
            user = self.get(openid=openid)
            update_fields = ['nickname', 'gender', 'country', 'city', 'province', 'avatar_url']
            for field in update_fields:
                field_value = extra_fields.get(field) or ''
                if field_value:
                    setattr(user, field, field_value)
            user.save()
        except self.model.DoesNotExist:
            user = self.create_user(openid, **extra_fields)
        return user


class BkWeixinUser(models.Model):
    """微信公众号用户"""
    openid = models.CharField(u"微信用户应用唯一标识", max_length=128, unique=True)
    nickname = models.CharField(u"昵称", max_length=127, blank=True)
    gender = models.CharField(u"性别", max_length=15, blank=True)
    country = models.CharField(u"国家", max_length=63, blank=True)
    province = models.CharField(u"省份", max_length=63, blank=True)
    city = models.CharField(u"城市", max_length=63, blank=True)
    avatar_url = models.CharField(u"头像", max_length=255, blank=True)
    date_joined = models.DateTimeField(u"加入时间", default=timezone.now)

    class Meta:
        db_table = 'bk_weixin_user'
        verbose_name = u"微信用户"
        verbose_name_plural = u"微信用户"

    objects = BkWeixinUserManager()

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

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
from django.utils import timezone
from django.utils.translation import ugettext as _


class BkWeixinUserManager(models.Manager):
    def create_user(self, userid, **extra_fields):
        now = timezone.now()
        if not userid:
            raise ValueError('The given userid must be set')
        user = self.model(userid=userid, date_joined=now, **extra_fields)
        user.save()
        return user

    def get_update_or_create_user(self, userid, **extra_fields):
        """
        获取用户，无则创建，有则更新
        """
        update_fields = ['name', 'gender', 'country', 'city', 'province', 'avatar_url']
        # 清理无需字段
        for field in extra_fields:
            if field not in update_fields:
                extra_fields.pop(field)
        try:
            user = self.get(userid=userid)
            for field in update_fields:
                field_value = extra_fields.get(field) or ''
                if field_value:
                    setattr(user, field, field_value)
            user.save()
        except self.model.DoesNotExist:
            user = self.create_user(userid, **extra_fields)
        return user


class BkWeixinUser(models.Model):
    """微信公众号或企业微信用户"""
    userid = models.CharField(_("微信用户在应用里的唯一标识(公众号openid/企业微信userid)"), max_length=128, unique=True)
    name = models.CharField(_("名称"), max_length=127, blank=True)
    gender = models.CharField(_("性别"), max_length=15, blank=True)
    avatar_url = models.CharField(_("头像"), max_length=255, blank=True)
    date_joined = models.DateTimeField(_("加入时间"), default=timezone.now)
    # 公众号特有信息，需要添加更多字段，需修改
    # (1)weixin.core.models.BkWeixinUserManager.get_update_or_create_user里update_fields
    # (2)weixin.core.api.WeiXinApi.get_user_info_for_account返回需要的字段
    country = models.CharField(_("国家"), max_length=63, blank=True)
    province = models.CharField(_("省份"), max_length=63, blank=True)
    city = models.CharField(_("城市"), max_length=63, blank=True)
    # 企业微信特有信息，需要添加更多字段，需修改
    # (1)weixin.core.models.BkWeixinUserManager.get_update_or_create_user里update_fields
    # (2)weixin.core.api.QyWeiXinApi.get_user_info_for_account返回需要的字段

    class Meta:
        db_table = 'bk_weixin_user'
        verbose_name = _("微信用户")
        verbose_name_plural = _("微信用户")

    objects = BkWeixinUserManager()

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

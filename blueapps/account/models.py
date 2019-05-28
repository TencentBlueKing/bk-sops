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

from __future__ import unicode_literals

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from blueapps.account.conf import BkUserCompatibleMixin


class UserManager(BaseUserManager):

    def _create_user(self, username, is_staff=False, is_superuser=False,
                     password=None, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, is_active=True,
                          is_staff=is_staff, is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        return self._create_user(username, False, False, password,
                                 **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        return self._create_user(username, True, True, password,
                                 **extra_fields)

    def update_or_create(self, defaults=None, **kwargs):
        props = []

        for k in defaults.keys():
            if k in User.custom_fields:
                props.append({'key': k, 'value': defaults.pop(k)})
        obj, created = super(UserManager, self).update_or_create(defaults, **kwargs)
        for p in props:
            obj.set_property(p['key'], p['value'])
        return obj, created


class User(AbstractBaseUser, PermissionsMixin, BkUserCompatibleMixin):

    username = models.CharField(
        _('username'),
        max_length=64,
        unique=True,
        help_text=_('Required. 64 characters or fewer. Letters, '
                    'digits and underlined only.'),
        validators=[
            validators.RegexValidator(r'^[a-zA-Z0-9_]+$',
                                      _('Enter a valid openid. '
                                        'This value may contain only letters, '
                                        'numbers and underlined characters.'),
                                      'invalid'),
        ],
        error_messages={
            'unique': _("A user with that openid already exists."),
        },
    )

    nickname = models.CharField(
        _('nick name'),
        max_length=64,
        blank=True,
        help_text=_('Required. 64 characters or fewer.'),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this '
                    'admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

        # Pass platform default user table
        # db_table = 'auth_user'

    @property
    def full_name(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = '%s(%s)' % (self.username, self.nickname or self.username)
        return full_name.strip()

    def get_short_name(self):
        return self.nickname

    def get_property(self, key):
        try:
            return self.properties.get(key=key).value
        except UserProperty.DoesNotExist:
            return None

    def set_property(self, key, value):
        key_property, _ = self.properties.get_or_create(key=key)
        key_property.value = value
        key_property.save()

    @property
    def avatar_url(self):
        return self.get_property('avatar_url')

    @avatar_url.setter
    def avatar_url(self, a_url):
        self.set_property('avatar_url', a_url)


class UserProperty(models.Model):
    """
    Add user extra property
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='properties',
    )
    key = models.CharField(
        max_length=64,
        help_text=_('Required. 64 characters or fewer. Letters, '
                    'digits and underlined only.'),
        validators=[
            validators.RegexValidator(r'^[a-zA-Z0-9_]+$',
                                      _('Enter a valid key. '
                                        'This value may contain only letters, '
                                        'numbers and underlined characters.'),
                                      'invalid'),
        ],
    )
    value = models.TextField()

    class Meta:
        verbose_name = _('user property')
        verbose_name_plural = _('user properties')
        db_table = 'account_user_property'
        unique_together = (('user', 'key'),)

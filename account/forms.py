# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""BK user form."""
from django import forms

from account.models import BkUser


class BkUserCreationForm(forms.ModelForm):
    """A form that creates a user, with no privileges"""
    class Meta:
        model = BkUser
        fields = ("username",)

    def save(self, commit=True):
        user = super(BkUserCreationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class BkUserChangeForm(forms.ModelForm):
    """A form for updating users.

    Includes all the fields onthe user,
    """
    class Meta:
        model = BkUser
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super(BkUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

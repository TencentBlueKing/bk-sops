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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from blueapps.account.forms import UserCreationForm
from blueapps.account.models import User


class UserAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("nickname",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("username",)}),)
    add_form = UserCreationForm
    filter_horizontal = ["groups"]
    list_display = [
        "username",
        "nickname",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
    ]
    list_filter = ("is_superuser", "is_staff")
    search_fields = ("username",)


admin.site.register(User, UserAdmin)

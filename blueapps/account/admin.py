# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from blueapps.account.forms import UserCreationForm
from blueapps.account.models import User


class UserAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('nickname',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )
    add_form = UserCreationForm
    filter_horizontal = ['groups']
    list_display = ['username', 'nickname', 'is_active', 'is_staff',
                    'is_superuser', 'last_login']


admin.site.register(User, UserAdmin)

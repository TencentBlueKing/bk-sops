# -*- coding=utf-8 -*-
from blueapps.account.models import (
    User as BaseUser,
    UserManager as BaseUserManager
)


class UserProxyManager(BaseUserManager):
    pass


class UserProxy(BaseUser):
    objects = UserProxyManager()

    class Meta:
        proxy = True

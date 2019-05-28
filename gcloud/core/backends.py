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

from guardian.shortcuts import get_perms

from gcloud.core.models import Business


class GCloudPermissionBackend(object):

    def authenticate(self, username, password):
        """
        We do not authenticate user in this backend, so always return None.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        """
        If a user has manage_business perm for a exact business instance,
        he/she has all other perms of this business and related objects.
        """
        if isinstance(obj, Business):
            business = obj
        elif hasattr(obj, 'business'):
            business = getattr(obj, 'business')
        elif hasattr(obj, 'biz_cc_id'):
            try:
                business = Business.objects.get(cc_id=getattr(obj, 'biz_cc_id'))
            except Business.DoesNotExist:
                return
        else:
            return

        if isinstance(business, Business) and \
                'manage_business' in get_perms(user_obj, business):
            return True

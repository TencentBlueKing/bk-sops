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

from tastypie.authorization import ReadOnlyAuthorization


class CollectionAuthorization(ReadOnlyAuthorization):

    def read_detail(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        return bundle.obj.username == bundle.request.user.username

    def read_list(self, object_list, bundle):
        # Is the requested object owned by the user?
        return object_list.filter(username=bundle.request.user.username)

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.username == bundle.request.user.username

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.username == bundle.request.user.username:
                allowed.append(obj)
        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.username == bundle.request.user.username

    def delete_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list.filter(username=bundle.request.user.username)

    def delete_detail(self, object_list, bundle):
        return bundle.obj.username == bundle.request.user.username

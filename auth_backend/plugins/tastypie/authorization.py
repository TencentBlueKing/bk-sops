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

import logging

from tastypie.authorization import ReadOnlyAuthorization
from tastypie.exceptions import ImmediateHttpResponse

from ..http import HttpResponseAuthFailed

logger = logging.getLogger('root')


class BkSaaSReadOnlyAuthorization(ReadOnlyAuthorization):
    def __init__(self, auth_resource, create_action_id='create', read_action_id='read', update_action_id='update',
                 delete_action_id='delete'):
        self.auth_resource = auth_resource
        self.create_action_id = create_action_id
        self.read_action_id = read_action_id
        self.update_action_id = update_action_id
        self.delete_action_id = delete_action_id

    def build_auth_failed_response(self, resource_name, action_id):
        return ImmediateHttpResponse(HttpResponseAuthFailed(
            resource_type_name=self.auth_resource.name,
            resource_name=resource_name,
            action_name=self.auth_resource.action_id_to_name(action_id)
        ))

    def authorized_list(self, username, action_id):
        authorized_result = self.auth_resource.search_authorized_resources(username, action_id)
        if not authorized_result['result']:
            logger.error('Search authorized resources of Resource[{resource}] return error: {error}'.format(
                resource=self.auth_resource.name,
                error=authorized_result['message']
            ))
            return []
        authorized_resources = authorized_result['data']
        authorized_resource_pks = []
        for action_resource in authorized_resources:
            if action_resource['action_id'] == action_id:
                for resource in action_resource['resource_ids']:
                    if resource['resource_type'] == self.auth_resource.rtype:
                        authorized_resource_pks.append(resource['resource_id'])
        return authorized_resource_pks

    def read_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.read_action_id)
        return object_list.objects.filter(pk__in=authorized_pks)

    def read_detail(self, object_list, bundle):
        if bundle.obj not in self.read_list(object_list, bundle):
            raise self.build_auth_failed_response(bundle.obj.name, self.read_action_id)
        return True


class BkSaaSAuthorization(BkSaaSReadOnlyAuthorization):
    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_result = self.auth_resource.verify_resource_perms(username, self.create_action_id, bundle.obj.pk)
        if not authorized_result or not authorized_result['data'][0]['is_paas']:
            return False
        return True

    def update_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.update_action_id)
        return object_list.objects.filter(pk__in=authorized_pks)

    def update_detail(self, object_list, bundle):
        if not self.update_list(object_list, bundle).filter(pk=bundle.obj.pk).exists():
            raise self.build_auth_failed_response(bundle.obj.name, self.update_action_id)
        return True

    def delete_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.delete_action_id)
        return object_list.objects.filter(pk__in=authorized_pks)

    def delete_detail(self, object_list, bundle):
        if not self.delete_list(object_list, bundle).filter(pk=bundle.obj.pk).exists():
            raise self.build_auth_failed_response(bundle.obj.name, self.delete_action_id)
        return True


class BkSaaSLooseReadOnlyAuthorization(BkSaaSReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        return object_list

    def read_detail(self, object_list, bundle):
        if bundle.obj not in super(BkSaaSLooseReadOnlyAuthorization, self).read_list(object_list, bundle):
            raise self.build_auth_failed_response(bundle.obj.name, self.read_action_id)
        return True


class BkSaaSLooseAuthorization(BkSaaSLooseReadOnlyAuthorization, BkSaaSAuthorization):
    pass

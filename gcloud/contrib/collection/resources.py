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

import json
import logging

from tastypie.resources import ModelResource, ALL

from auth_backend.plugins.utils import search_all_resources_authorized_actions

from gcloud.contrib.collection.models import Collection
from gcloud.contrib.collection.authorization import CollectionAuthorization
from gcloud.tasktmpl3.permissions import task_template_resource
from gcloud.commons.template.permissions import common_template_resource
from gcloud.contrib.appmaker.permissions import mini_app_resource
from gcloud.periodictask.permissions import periodic_task_resource


logger = logging.getLogger("root")


class CollectionResources(ModelResource):

    class Meta:
        limit = 15
        always_return_data = True
        queryset = Collection.objects.all()
        resource_name = 'collection'
        auth_resources = {
            'flow': task_template_resource,
            'common_flow': common_template_resource,
            'mini_app': mini_app_resource,
            'periodic_task': periodic_task_resource,
        }
        authorization = CollectionAuthorization()
        allowed_methods = ['get', 'post', 'delete', 'put']
        filtering = {
            'id': ALL,
            'category': ALL
        }

    def get_object_list(self, request):
        query = super(CollectionResources, self).get_object_list(request)
        return query.filter(username=request.user.username)

    def obj_create(self, bundle, **kwargs):

        return super(CollectionResources, self).obj_create(bundle, username=bundle.request.user.username)

    def obj_delete_list_for_update(self, bundle, **kwargs):
        request = bundle.request
        deserialized = self.deserialize(request, request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)
        ids = []
        for obj in deserialized.get(self._meta.collection_name, []):
            collection_id = obj.get('id', None)
            if collection_id:
                ids.append(str(collection_id))
        super(CollectionResources, self).obj_delete_list_for_update(bundle, id__in=','.join(ids))

    def dehydrate_extra_info(self, bundle):
        """
        Given a bundle with an object instance, extract the information from it
        to populate the resource.
        """
        extra_info = bundle.data['extra_info']
        return json.loads(extra_info)

    def hydrate_extra_info(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        extra_info = bundle.data['extra_info']
        bundle.data['extra_info'] = json.dumps(extra_info)
        return bundle

    def dehydrate(self, bundle):
        username = bundle.request.user.username
        category = bundle.data.get('category', '')
        auth_resources = self._meta.auth_resources
        auth_resource = auth_resources.get(category, None)
        if auth_resource is None:
            return bundle

        inspect = getattr(self._meta, 'inspect', None)
        scope_id = inspect.scope_id(bundle) if inspect else None

        resources_perms = search_all_resources_authorized_actions(
            username=username,
            resource_type=auth_resource.rtype,
            auth_resource=auth_resource,
            scope_id=scope_id
        )
        obj_id = str(inspect.resource_id(bundle)) if inspect else str(json.loads(bundle.obj.extra_info)['id'])
        auth_actions = resources_perms.get(obj_id, [])
        bundle.data['auth_actions'] = auth_actions
        return bundle

    def alter_list_data_to_serialize(self, request, data):
        objects = data.get(self._meta.collection_name, False)
        auth_resources = getattr(self._meta, 'auth_resources', False)
        categories = set([item.data['category'] for item in objects]) if objects else []
        if not categories:
            return data

        operate_ids = set()
        operations = []
        resource = {}
        for category in categories:
            auth_resource = auth_resources.get(category, None)
            if auth_resource:
                resource[category] = auth_resource.base_info()
                resource_operations = auth_resource.operations
                for item in resource_operations:
                    if item['operate_id'] not in operate_ids:
                        operations.append(item)
                        operate_ids.add(item['operate_id'])

        if 'meta' not in data:
            data['meta'] = {}
        data['meta']['auth_operations'] = operations
        data['meta']['auth_resource'] = resource
        return data

    def alter_detail_data_to_serialize(self, request, data):
        auth_resources = getattr(self._meta, 'auth_resources')
        collection = data.data
        category = collection.get('category')
        if not auth_resources:
            return data

        auth_resource = auth_resources.get(category)
        if auth_resource:
            data.data['auth_operations'] = auth_resource.operations
            data.data['auth_resource'] = auth_resource.base_info()

        return data

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

import json
import logging

from tastypie.resources import ModelResource, ALL

from gcloud.contrib.collection.models import Collection
from gcloud.contrib.collection.authorization import CollectionAuthorization

logger = logging.getLogger("root")


class CollectionResources(ModelResource):

    class Meta:
        limit = 15
        always_return_data = True
        queryset = Collection.objects.all()
        resource_name = 'collection'
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

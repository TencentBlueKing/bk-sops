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

from gcloud.contrib.collection.models import Collection
from gcloud.contrib.collection.authorization import CollectionAuthorization
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import utils as iam_auth_utils


logger = logging.getLogger("root")


class CollectionResources(ModelResource):
    class Meta:
        limit = 15
        always_return_data = True
        queryset = Collection.objects.all()
        resource_name = "collection"
        authorization = CollectionAuthorization()
        allowed_methods = ["get", "post", "delete", "put"]
        filtering = {"id": ALL, "category": ALL}
        append_resource_actions = {
            IAMMeta.FLOW_RESOURCE: [
                IAMMeta.FLOW_VIEW_ACTION,
                IAMMeta.FLOW_CREATE_TASK_ACTION,
                IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
            ],
            IAMMeta.COMMON_FLOW_RESOURCE: [IAMMeta.COMMON_FLOW_VIEW_ACTION],
            IAMMeta.MINI_APP_RESOURCE: [IAMMeta.MINI_APP_VIEW_ACTION],
        }

    def get_object_list(self, request):
        query = super(CollectionResources, self).get_object_list(request)
        return query.filter(username=request.user.username)

    def obj_create(self, bundle, **kwargs):

        return super(CollectionResources, self).obj_create(bundle, username=bundle.request.user.username)

    def obj_delete_list_for_update(self, bundle, **kwargs):
        request = bundle.request
        deserialized = self.deserialize(
            request, request.body, format=request.META.get("CONTENT_TYPE", "application/json")
        )
        deserialized = self.alter_deserialized_list_data(request, deserialized)
        ids = []
        for obj in deserialized.get(self._meta.collection_name, []):
            collection_id = obj.get("id", None)
            if collection_id:
                ids.append(str(collection_id))
        super(CollectionResources, self).obj_delete_list_for_update(bundle, id__in=",".join(ids))

    def dehydrate_extra_info(self, bundle):
        """
        Given a bundle with an object instance, extract the information from it
        to populate the resource.
        """
        extra_info = bundle.data["extra_info"]
        return json.loads(extra_info)

    def hydrate_extra_info(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        extra_info = bundle.data["extra_info"]
        bundle.data["extra_info"] = json.dumps(extra_info)
        return bundle

    def alter_list_data_to_serialize(self, request, data):

        resource_id_list_map = {r_type: [] for r_type in self._meta.append_resource_actions}

        resource_allowed_actions_map = {}

        for bundle in data["objects"]:
            if bundle.obj.category in resource_id_list_map:
                resource_id_list_map[bundle.obj.category].append(bundle.data["extra_info"]["id"])

        for r_type, id_list in resource_id_list_map.items():
            resource_allowed_actions_map[r_type] = getattr(
                iam_auth_utils, "get_{}_allowed_actions_for_user".format(r_type)
            )(request.user.username, self._meta.append_resource_actions[r_type], id_list)

        for bundle in data["objects"]:
            if bundle.obj.category not in resource_allowed_actions_map:
                bundle.data["auth_actions"] = []
                continue

            resource_allowed_actions = resource_allowed_actions_map[bundle.obj.category]

            bundle.data["auth_actions"] = [
                act
                for act, allow in resource_allowed_actions.get(str(bundle.data["extra_info"]["id"]), {}).items()
                if allow
            ]

        return data

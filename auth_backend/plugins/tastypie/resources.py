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
from __future__ import absolute_import, unicode_literals

import logging
from builtins import object, str

from auth_backend.backends.utils import get_backend_from_config

backend = get_backend_from_config()

logger = logging.getLogger("root")


class BkSaaSLabeledDataResourceMixin(object):
    def alter_list_data_to_serialize(self, request, data):
        auth_resource = getattr(self._meta, "auth_resource", None)
        if auth_resource is None:
            return data
        inspect = getattr(self._meta, "inspect", None)
        get_instance = inspect.instance if inspect else lambda bundle: bundle.obj

        # set meta info
        data["meta"]["auth_operations"] = auth_resource.operations
        data["meta"]["auth_resource"] = auth_resource.base_info()

        # assemble batch-verify params
        action_ids = [act.id for act in auth_resource.actions]
        instances = [get_instance(bundle) for bundle in data["objects"]]
        verify_result = backend.batch_verify_perms(auth_resource, "user", request.user.username, action_ids, instances)

        if not verify_result["result"]:
            logger.error(
                "alter_list_data_to_serialize for resource({}) failed: {}".format(
                    auth_resource.rtype, verify_result["message"]
                )
            )

            for bundle in data["objects"]:
                bundle.data["auth_actions"] = []

            return data

        # process verify result
        passed_inst_irrelevant_actions = []
        inst_auth_actions = {}
        for verify_item in verify_result["data"]:
            # ignore verify fail action
            if not verify_item["is_pass"]:
                continue

            action_id = verify_item["action_id"]

            if not verify_item["resource_id"]:
                passed_inst_irrelevant_actions.append(action_id)
            else:
                # collect instance auth actions
                for resource in verify_item["resource_id"]:
                    if resource["resource_type"] == auth_resource.rtype:
                        rid = str(resource["resource_id"])
                        inst_auth_actions.setdefault(rid, []).append(action_id)
                        break

        # set auth actions
        for bundle in data["objects"]:
            obj_id = str(inspect.resource_id(bundle)) if inspect else str(bundle.obj.pk)
            auth_actions = inst_auth_actions.get(obj_id, [])
            auth_actions.extend(passed_inst_irrelevant_actions)
            bundle.data["auth_actions"] = auth_actions

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = data
        auth_resource = getattr(self._meta, "auth_resource", None)
        if auth_resource is None:
            return data

        resource_info = auth_resource.base_info()
        inspect = getattr(self._meta, "inspect", None)
        if not resource_info["scope_id"]:
            resource_info["scope_id"] = inspect.scope_id(data) if inspect else None
        get_instance = inspect.instance if inspect else lambda bundle: bundle.obj

        # set meta
        data.data["auth_operations"] = auth_resource.operations
        data.data["auth_resource"] = resource_info

        # assemble batch-verify params
        action_ids = [act.id for act in auth_resource.actions]
        instances = [get_instance(bundle)]
        verify_result = backend.batch_verify_perms(auth_resource, "user", request.user.username, action_ids, instances)

        if not verify_result["result"]:
            logger.error(
                "alter_detail_data_to_serialize for resource({}) failed: {}".format(
                    auth_resource.rtype, verify_result["message"]
                )
            )

            bundle.data["auth_actions"] = []

            return data

        auth_actions = []

        for verify_item in verify_result["data"]:
            # ignore verify fail action
            if not verify_item["is_pass"]:
                continue

            auth_actions.append(verify_item["action_id"])

        bundle.data["auth_actions"] = auth_actions
        return data

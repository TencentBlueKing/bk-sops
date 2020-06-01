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

from collections import OrderedDict

from . import meta


def gen_perms_apply_data(system, subject, action_to_resources_list):
    """
    根据传入的参数生成无权限交互协议数据

    action_to_resources_list 应该参照以下格式:

    [
        {
            "action": Action,
            "resources_list": [[resource1, resource2], [resource1, resource2]]
        },
        ...
    ]

    单个 action 中对应的 resources_list 必须是同类型的 Resource

    """
    data = {
        "system_id": system,
        "system_name": meta.get_system_name(system),
    }

    actions = []
    for atr in action_to_resources_list:
        action_obj = atr["action"]
        resources_list = atr["resources_list"]
        action = {
            "id": action_obj.id,
            "name": meta.get_action_name(system, action_obj.id),
        }

        # 1. aggregate resources by system and type
        system_resources_list = OrderedDict({})
        for resources in resources_list:
            system_resources = OrderedDict({})

            # 1. assemble system_resources e.g. {"system1": [r1, r2], "system2": [r3]}
            for resource in resources:
                system_resources.setdefault(resource.system, []).append(resource)

            # 2. append to system_resources_list e.g.g {"system1": [[r1, r2]], "system2": [[r3]]}
            for system_id, resources in system_resources.items():
                system_resources_list.setdefault(system_id, []).append(resources)

        related_resource_types = []
        for system_id, resources_list in system_resources_list.items():
            # get resource type from last resource in resources
            a_resource = resources_list[0][-1]
            resource_types = {
                "system_id": system_id,
                "system_name": meta.get_system_name(system_id),
                "type": a_resource.type,
                "type_name": meta.get_resource_name(system_id, a_resource.type),
            }
            instances = []

            for resources in resources_list:
                instances.append(
                    [
                        {
                            "type": resource.type,
                            "type_name": meta.get_resource_name(system_id, resource.type),
                            "id": resource.id,
                            "name": resource.attribute.get("name", "") if resource.attribute else "",
                        }
                        for resource in resources
                    ]
                )

            resource_types["instances"] = instances
            related_resource_types.append(resource_types)

        action["related_resource_types"] = related_resource_types
        actions.append(action)

    data["actions"] = actions

    return data

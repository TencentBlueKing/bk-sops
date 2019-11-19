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

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string


def get_backend_from_config():
    backend_path = settings.AUTH_BACKEND_CLS
    if not backend_path:
        raise LookupError('can not find AUTH_BACKEND_CLS in settings or AUTH_BACKEND_CLS is empty')

    try:
        backend_cls = import_string(backend_path)
    except ImportError:
        raise ImportError('can not import backend class from path: {path}'.format(path=backend_path))

    return backend_cls()


def resource_id_for(resource, instance):
    resource_id = []
    __gen_complete_id(resource, instance, resource_id)
    return resource_id


def resource_actions_for(resource, action_ids, instances, ignore_relate_instance_act=True):
    actions = []
    for action_id in action_ids:

        if resource.is_instance_related_action(action_id):
            if instances:
                actions.extend({'action_id': action_id,
                                'resource_type': resource.rtype,
                                'resource_id': resource_id_for(resource, instance)} for instance in instances)
            elif not ignore_relate_instance_act:
                actions.append({'action_id': action_id,
                                'resource_type': resource.rtype})
        else:
            actions.append({'action_id': action_id,
                            'resource_type': resource.rtype})

    return actions


def __gen_complete_id(resource, instance, id_tree):
    if resource.parent:
        parent_resource = resource.parent
        __gen_complete_id(parent_resource, resource.parent_instance(instance), id_tree)

    # bk_iam only accept str type id
    id_tree.append({'resource_type': resource.rtype, 'resource_id': str(resource.resource_id(instance))})

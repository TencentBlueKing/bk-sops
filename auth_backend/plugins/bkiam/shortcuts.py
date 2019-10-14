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

import sys

from django.conf import settings
from django.utils.module_loading import import_string

from bkiam import shortcuts
from bkiam.exceptions import PermTemplateUpsertFailedError


def upsert_perm_templates():
    perm_templates_path = getattr(settings, 'BK_IAM_PERM_TEMPLATES', None)

    if not perm_templates_path:
        return

    if not getattr(settings, 'BK_IAM_SYNC_TEMPLATES', None):
        return

    perm_templates = import_string(perm_templates_path)
    raw_templates = []

    for template in perm_templates:
        raw_template = {
            'perm_template_name': template['name'],
            'template_id': template['id'],
            'desc': template['desc'],
            'resource_types_actions': []
        }
        for resource_action in template['resource_actions']:
            for action in resource_action['actions']:
                raw_template['resource_types_actions'].append({
                    'scope_type_id': resource_action['resource'].scope_type,
                    'resource_type_id': resource_action['resource'].rtype,
                    'action_id': action.id
                })

        raw_templates.append(raw_template)

    try:
        shortcuts.upsert_perms_templates(raw_templates)
    except PermTemplateUpsertFailedError as e:
        sys.stdout.write('bk_iam perm templates upsert failed: %s' % str(e))

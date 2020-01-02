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
USER_ADDITIONAL_PROPERTY = [
    'chname',
    'company',
    'qq',
    'phone',
    'email',
    'auth_token'
]

USER_FIELDS_MAP = {
    'id': 'id',
    'username': 'username',
    'nickname': 'chname',
    'is_staff': 'is_staff',
    'date_joined': 'date_joined',
    'is_superuser': 'is_superuser'
}

CONSTRAINT_MIGRATIONS = [
    {
        'table': 'tasktmpl3_tasktemplate_collector',
        'columns': [
            {
                'origin_name': 'bkuser_id',
                'new_name': 'user_id',
                'origin_ref_table': 'account_bkuser',
                'new_ref_table': 'account_user',
            }
        ]
    },
    {
        'table': 'guardian_userobjectpermission',
        'columns': [
            {
                'origin_name': 'user_id',
                'origin_ref_table': 'account_bkuser',
                'new_ref_table': 'account_user',
            }
        ]
    },
    {
        'table': 'django_admin_log',
        'columns': [
            {
                'origin_name': 'user_id',
                'origin_ref_table': 'account_bkuser',
                'new_ref_table': 'account_user',
                'ref_field': 'id'
            }
        ]
    }
]

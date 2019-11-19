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

from django.db import migrations


def reverse_func(apps, schema_editor):
    Project = apps.get_model('core', 'Project')
    db_alias = schema_editor.connection.alias
    Project.objects.using(db_alias).all().delete()


def forward_func(apps, schema_editor):
    Project = apps.get_model('core', 'Project')
    Business = apps.get_model('core', 'Business')
    BusinessGroupMembership = apps.get_model('core', 'BusinessGroupMembership')
    db_alias = schema_editor.connection.alias

    projects = []
    active_business = Business.objects.using(db_alias).filter(status='enable')

    # query maintainers for all business
    business_group_membership = BusinessGroupMembership.objects.using(db_alias) \
        .filter(group__name__endswith='Maintainers').values('group__name',
                                                            'business__cc_id',
                                                            'group__user__username')
    biz_maintainers = {}
    for membership in business_group_membership:
        biz_maintainers.setdefault(membership['business__cc_id'], []).append(membership['group__user__username'])

    # sort maintainer list
    for cc_id in list(biz_maintainers.keys()):
        biz_maintainers[cc_id].sort()

    for business in active_business:

        projects.append(Project(
            id=business.cc_id,
            name=business.cc_name,
            time_zone=business.time_zone,
            creator='admin',
            desc='',
            from_cmdb=True,
            cmdb_biz_id=business.cc_id
        ))

    Project.objects.using(db_alias).bulk_create(projects, batch_size=5000)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_project_userdefaultproject'),
    ]

    operations = [
        migrations.RunPython(forward_func, reverse_func)
    ]

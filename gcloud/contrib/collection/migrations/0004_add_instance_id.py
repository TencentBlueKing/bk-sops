# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import unicode_literals

from django.db import migrations
import json


def load_instance_id(apps, schema_editor):
    collection_model = apps.get_model("collection", "Collection")
    for row in collection_model.objects.all():
        extra_info = json.loads(row.extra_info)
        row.instance_id = extra_info.get("id")
        row.save(update_fields=["instance_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("collection", "0003_auto_20201103_2229"),
    ]

    operations = [migrations.RunPython(load_instance_id, reverse_code=migrations.RunPython.noop)]

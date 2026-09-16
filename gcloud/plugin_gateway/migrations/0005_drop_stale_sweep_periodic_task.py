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

from django.apps import apps as global_apps
from django.db import migrations

SWEEP_TASK_PATH = "gcloud.plugin_gateway.tasks.sweep_expired_plugin_gateway_runs"


def drop_stale_sweep_periodic_task(apps, schema_editor):
    """删除 DatabaseScheduler 已落库的超时清扫周期任务。

    beat 使用 django_celery_beat 的 DatabaseScheduler，CELERYBEAT_SCHEDULE 的条目会被同步成
    PeriodicTask 记录，并且从配置里移除后不会自动清理。插件网关开关关闭后需要主动删除残留记录，
    否则 beat 仍会按库里的记录向无消费者的 open_plugin_polling 队列投递消息。
    开关开启时 beat 启动会按配置重新登记，因此这里可以无条件删除。
    """

    # django_celery_beat 属于第三方 app，这里不通过 migration 依赖引用，避免未启用 celery 时构图失败
    try:
        periodic_task_model = global_apps.get_model("django_celery_beat", "PeriodicTask")
    except LookupError:
        return

    connection = schema_editor.connection
    if periodic_task_model._meta.db_table not in connection.introspection.table_names():
        return

    periodic_task_model.objects.filter(task=SWEEP_TASK_PATH).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("plugin_gateway", "0004_remove_plugin_allow_list"),
    ]

    operations = [
        migrations.RunPython(drop_stale_sweep_periodic_task, migrations.RunPython.noop),
    ]

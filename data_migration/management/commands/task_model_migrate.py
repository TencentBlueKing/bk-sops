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

from django.core.management.base import BaseCommand

from gcloud.periodictask.models import PeriodicTaskHistory
from gcloud.taskflow3.models import TaskFlowInstance


class Command(BaseCommand):
    help = "help to migrate task data of some data from history version"

    def handle(self, *args, **options):
        # 将之前模型中template_source的business值修改成project
        print("sync template_source of task model...")
        TaskFlowInstance.objects.filter(template_source="business").update(template_source="project")
        print("sync template_source of task model finished.")

        # 将之前模型中周期任务create_info字段补上
        print("sync create_info of periodic task instances...")
        task_queryset = TaskFlowInstance.objects.filter(create_method="periodic", create_info="")
        task_ids = task_queryset.values_list("id", flat=True)
        history_data = PeriodicTaskHistory.objects.filter(flow_instance__id__in=task_ids).values_list(
            "flow_instance__id", "task__task__id"
        )
        mapping = {task_id: periodic_id for task_id, periodic_id in history_data}
        task_obj_num = len(task_queryset)
        for idx, task_obj in enumerate(task_queryset):
            if idx % 100 == 0:
                print("{}/{} periodic tasks have been updated create_info field.".format(idx, task_obj_num))
            task_obj.create_info = mapping.get(task_obj.id, "")
            task_obj.save()
        # 升级Django2.2后可直接用bulk_update
        # TaskFlowInstance.objects.bulk_update(task_queryset, ["create_info"])

        print("sync create_info of periodic task instances finished.")

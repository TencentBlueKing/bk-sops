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
import sys

from django.core.management.base import BaseCommand

from gcloud.commons.template.models import CommonTemplate
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.collection.models import Collection
from gcloud.periodictask.models import PeriodicTask
from gcloud.tasktmpl3.models import TaskTemplate


class Command(BaseCommand):
    help = "Flush expired collections."

    def handle(self, *args, **options):
        # 项目流程收藏
        sys.stdout.write("Begin to delete task template collections...\n")
        deleted_task_template_ids = TaskTemplate.objects.filter(is_deleted=True).values_list("id", flat=True)
        collections = Collection.objects.filter(category="flow", instance_id__in=deleted_task_template_ids)
        sys.stdout.write("{} task template collections to delete...\n".format(len(collections)))
        collections.delete()
        sys.stdout.write("Task template collections deleted.\n")

        # 公共流程收藏
        sys.stdout.write("Begin to delete common template collections...\n")
        deleted_common_template_ids = CommonTemplate.objects.filter(is_deleted=True).values_list("id", flat=True)
        collections = Collection.objects.filter(category="common_flow", instance_id__in=deleted_common_template_ids)
        sys.stdout.write("{} common template collections to delete...\n".format(len(collections)))
        collections.delete()
        sys.stdout.write("Common template collections deleted.\n")

        # 周期任务收藏
        sys.stdout.write("Begin to delete periodic task collections...\n")
        periodic_task_collection_ids = Collection.objects.filter(category="periodic_task").values_list(
            "instance_id", flat=True
        )
        periodic_task_ids = PeriodicTask.objects.filter(id__in=periodic_task_collection_ids).values_list(
            "id", flat=True
        )
        deleted_periodic_task_ids = list(set(periodic_task_collection_ids) - set(periodic_task_ids))
        collections = Collection.objects.filter(category="periodic_task", instance_id__in=deleted_periodic_task_ids)
        sys.stdout.write("{} periodic task collections to delete...\n".format(len(collections)))
        collections.delete()
        sys.stdout.write("Periodic task collections deleted.\n")

        # 轻应用收藏
        sys.stdout.write("Begin to delete mini_app collections...\n")
        deleted_app_maker_ids = AppMaker.objects.filter(is_deleted=True).values_list("id", flat=True)
        collections = Collection.objects.filter(category="mini_app", instance_id__in=deleted_app_maker_ids)
        sys.stdout.write("{} mini_app collections to delete...\n".format(len(collections)))
        collections.delete()
        sys.stdout.write("Mini_app collections deleted.\n")

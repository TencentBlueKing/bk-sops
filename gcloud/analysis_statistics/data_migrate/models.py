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

from django.db import models

DEFAULT_MIGRATE_NUM = 500


class MigrateLog(models.Model):

    desc = models.CharField(
        max_length=128,
        default="migrate_switch=1是启动迁移，0为停止迁移；migrate_num_once控制单次迁移量，默认为{num}。".format(num=DEFAULT_MIGRATE_NUM),
    )
    migrate_switch = models.BooleanField(verbose_name="迁移任务开关,默认为打开状态", default=True)
    migrate_num_once = models.IntegerField(verbose_name="单次数据迁移量", default=DEFAULT_MIGRATE_NUM)

    template_in_pipeline_start = models.IntegerField(verbose_name="当前轮次template迁移起点", default=1)
    component_in_template_start = models.IntegerField(verbose_name="当前轮次componet迁移起点", default=1)
    instance_in_pipeline_start = models.IntegerField(verbose_name="当前轮次instance迁移起点", default=1)
    component_execute_data_start = models.IntegerField(verbose_name="当前轮次componentExecute迁移起点", default=1)

    template_in_pipeline_migrated = models.IntegerField(verbose_name="template已迁移量", default=0)
    component_in_template_migrated = models.IntegerField(verbose_name="component已迁移量", default=0)
    instance_in_pipeline_migrated = models.IntegerField(verbose_name="instance已迁移量", default=0)
    component_execute_data_migrated = models.IntegerField(verbose_name="componentExecute已迁移量", default=0)

    template_in_pipeline_finished = models.IntegerField(verbose_name="template迁移状态", default=False)
    component_in_template_finished = models.IntegerField(verbose_name="component迁移状态", default=False)
    instance_in_pipeline_finished = models.IntegerField(verbose_name="instance迁移状态", default=False)
    component_execute_data_finished = models.IntegerField(verbose_name="componentExecute迁移状态", default=False)

    template_in_pipeline_end = models.IntegerField(verbose_name="当前轮次template迁移终点", default=DEFAULT_MIGRATE_NUM)
    component_in_template_end = models.IntegerField(verbose_name="当前轮次component迁移终点", default=DEFAULT_MIGRATE_NUM)
    instance_in_pipeline_end = models.IntegerField(verbose_name="当前轮次instance迁移终点", default=DEFAULT_MIGRATE_NUM)
    component_execute_data_end = models.IntegerField(
        verbose_name="当前轮次componentExecute迁移终点", default=DEFAULT_MIGRATE_NUM
    )

    template_in_pipeline_count = models.IntegerField(verbose_name="template数据总量", default=0)
    component_in_template_count = models.IntegerField(verbose_name="component数据总量", default=0)
    instance_in_pipeline_count = models.IntegerField(verbose_name="instance数据总量", default=0)
    component_execute_data_count = models.IntegerField(verbose_name="componentExecute数据总量", default=0)

    class Meta:
        verbose_name = "统计数据-迁移控制"

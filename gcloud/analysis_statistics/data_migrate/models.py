# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models

# 单次迁移量
MIGRATE_NUM = 500


class MigrateLog(models.Model):
    
    migrate_switch = models.BooleanField(verbose_name="迁移任务开关,默认为打开状态", default=True)
    migrate_num_once = models.IntegerField(verbose_name="单次数据迁移量,默认为{num}".format(num=MIGRATE_NUM), default=MIGRATE_NUM)

    templateInPipeline_start = models.IntegerField(verbose_name="template迁移起点", default=1)
    componentInTemplate_start = models.IntegerField(verbose_name="componet迁移起点", default=1)
    instanceInPipeline_start = models.IntegerField(verbose_name="instance迁移起点", default=1)
    componentExecuteData_start = models.IntegerField(verbose_name="componentExecute迁移起点", default=1)

    templateInPipeline_migrated = models.IntegerField(verbose_name="template已迁移量", default=0)
    componentInTemplate_migrated = models.IntegerField(verbose_name="component已迁移量", default=0)
    instanceInPipeline_migrated = models.IntegerField(verbose_name="instance已迁移量", default=0)
    componenetExecuteData_migrated = models.IntegerField(verbose_name="componentExecute已迁移量", default=0)

    templateInPipeline_finished = models.IntegerField(verbose_name="template迁移状态", default=False)
    componentInTemplate_finished = models.IntegerField(verbose_name="component迁移状态", default=False)
    instanceInPipeline_finished = models.IntegerField(verbose_name="instance迁移状态", default=False)
    componenetExecuteData_finished = models.IntegerField(verbose_name="componentExecute迁移状态", default=False)

    templateInPipeline_end = models.IntegerField(verbose_name="template迁移终点", default=MIGRATE_NUM)
    componentInTemplate_end = models.IntegerField(verbose_name="component迁移终点", default=MIGRATE_NUM)
    instanceInPipeline_end = models.IntegerField(verbose_name="instance迁移终点", default=MIGRATE_NUM)
    componenetExecuteData_end = models.IntegerField(verbose_name="componentExecute迁移终点", default=MIGRATE_NUM)

    templateInPipeline_count = models.IntegerField(verbose_name="template数据总量", default=0)
    componentInTemplate_count = models.IntegerField(verbose_name="component数据总量", default=0)
    instanceInPipeline_count = models.IntegerField(verbose_name="instance数据总量", default=0)
    componenetExecuteData_count = models.IntegerField(verbose_name="componentExecute数据总量", default=0)

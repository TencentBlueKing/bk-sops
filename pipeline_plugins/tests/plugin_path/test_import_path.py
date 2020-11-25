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

from django.test import TestCase
from django.conf import settings

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component


class PluginPathTestCase(TestCase):
    def setUp(self):
        self.assert_paths = {
            "pipeline_plugins.components.collections.sites.open.cc.replace_fault_machine.legacy": [
                "CCReplaceFaultMachineComponent",
                "CCReplaceFaultMachineService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.update_module.legacy": [
                "CCUpdateModuleComponent",
                "CCUpdateModuleService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc_plugins.v1_0": [
                "CCCreateSetComponent",
                "CCCreateSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.transfer_fault_host.legacy": [
                "CmdbTransferFaultHostComponent",
                "CmdbTransferFaultHostService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.transfer_to_idle.legacy": [
                "CCTransferHostToIdleComponent",
                "CCTransferHostToIdleService",
            ],
            "pipeline_plugins.components.collections.sites.open.nodeman.create_task.legacy": [
                "NodemanCreateTaskComponent",
                "NodemanCreateTaskService",
            ],
            "pipeline_plugins.components.collections.controller": [
                "PauseComponent",
                "PauseService",
                "SleepTimerComponent",
                "SleepTimerService",
            ],
            "pipeline_plugins.components.collections.sites.open.bk": ["NotifyComponent", "NotifyService"],
            "pipeline_plugins.components.collections.sites.open.cc.create_set.legacy": [
                "CCCreateSetComponent",
                "CCCreateSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.create_module.legacy": [
                "CCCreateModuleComponent",
                "CCCreateModuleService",
            ],
            "pipeline.components.collections.sites.{}.bk".format(settings.OPEN_VER): [
                "NotifyComponent",
                "NotifyService",
            ],
            "pipeline_plugins.components.collections.common": ["HttpComponent", "HttpRequestService"],
            "pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.v1_0": [
                "CCTransferHostModuleComponent",
                "CCTransferHostModuleService",
            ],
            "pipeline_plugins.components.collections.sites.open.bk.notify.legacy": [
                "NotifyComponent",
                "NotifyService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.transfer_host_module.legacy": [
                "CCTransferHostModuleComponent",
                "CCTransferHostModuleService",
            ],
            "pipeline_plugins.components.collections.sites.open.job": [
                "JobCronTaskComponent",
                "JobCronTaskService",
                "JobExecuteTaskComponent",
                "JobExecuteTaskService",
                "JobFastExecuteScriptComponent",
                "JobFastExecuteScriptService",
                "JobFastPushFileComponent",
                "JobFastPushFileService",
                "JobPushLocalFilesComponent",
                "JobPushLocalFilesService",
                "JobService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.transfer_host_resource.legacy": [
                "CmdbTransferHostResourceModuleComponent",
                "CmdbTransferHostResourceModuleService",
            ],
            "pipeline_plugins.components.collections.sites.{}.cc".format(settings.OPEN_VER): [
                "CCBatchDeleteSetComponent",
                "CCBatchDeleteSetService",
                "CCCreateSetComponent",
                "CCCreateSetService",
                "CCEmptySetHostsComponent",
                "CCEmptySetHostsService",
                "CCReplaceFaultMachineComponent",
                "CCReplaceFaultMachineService",
                "CCTransferHostModuleComponent",
                "CCTransferHostModuleService",
                "CCTransferHostToIdleComponent",
                "CCTransferHostToIdleService",
                "CCUpdateHostComponent",
                "CCUpdateHostService",
                "CCUpdateModuleComponent",
                "CCUpdateModuleService",
                "CCUpdateSetComponent",
                "CCUpdateSetService",
                "CCUpdateSetServiceStatusComponent",
                "CCUpdateSetServiceStatusService",
                "CmdbTransferFaultHostComponent",
                "CmdbTransferFaultHostService",
                "CmdbTransferHostResourceModuleComponent",
                "CmdbTransferHostResourceModuleService",
            ],
            "pipeline_plugins.components.collections.sites.{}.job".format(settings.OPEN_VER): [
                "JobCronTaskComponent",
                "JobCronTaskService",
                "JobExecuteTaskComponent",
                "JobExecuteTaskService",
                "JobFastExecuteScriptComponent",
                "JobFastExecuteScriptService",
                "JobFastPushFileComponent",
                "JobFastPushFileService",
                "JobPushLocalFilesComponent",
                "JobPushLocalFilesService",
                "JobService",
            ],
            "pipeline_plugins.components.collections.sites.open.job.fast_push_file.v1_0": [
                "JobFastPushFileService",
                "JobFastPushFileComponent",
            ],
            "pipeline_plugins.components.collections.sites.open.job.fast_push_file.legacy": [
                "JobFastPushFileService",
                "JobFastPushFileComponent",
            ],
            "pipeline_plugins.components.collections.sites.open.job.push_local_files.v1_0_0": [
                "JobPushLocalFilesService",
                "JobPushLocalFilesComponent",
            ],
            "pipeline_plugins.components.collections.sites.open.job.cron_task.legacy": [
                "JobCronTaskService",
                "JobCronTaskComponent",
            ],
            "pipeline_plugins.components.collections.sites.open.job.execute_task.legacy": [
                "JobExecuteTaskService",
                "JobExecuteTaskComponent",
            ],
            "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.legacy": [
                "JobFastExecuteScriptService",
                "JobFastExecuteScriptComponent",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.legacy": [
                "CCEmptySetHostsComponent",
                "CCEmptySetHostsService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.update_set.v1_0": [
                "CCUpdateSetComponent",
                "CCUpdateSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.update_set_service_status.legacy": [
                "CCUpdateSetServiceStatusComponent",
                "CCUpdateSetServiceStatusService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.update_set_service_status.v1_0": [
                "CCUpdateSetServiceStatusComponent",
                "CCUpdateSetServiceStatusService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.update_module.v1_0": [
                "CCUpdateModuleComponent",
                "CCUpdateModuleService",
            ],
            "pipeline_plugins.components.collections.sites.{}.bk".format(settings.OPEN_VER): [
                "NotifyComponent",
                "NotifyService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.v1_0": [
                "CCBatchDeleteSetComponent",
                "CCBatchDeleteSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.bk.notify.v1_0": ["NotifyComponent", "NotifyService"],
            "pipeline_plugins.components.collections.sites.open.cc.update_host.legacy": [
                "CCUpdateHostComponent",
                "CCUpdateHostService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.create_set.v2_0": [
                "CCCreateSetComponent",
                "CCCreateSetService",
            ],
            "pipeline.components.collections.common": ["HttpComponent", "HttpRequestService"],
            "pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0": [
                "CCCreateSetComponent",
                "CCCreateSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.empty_set_hosts.v1_0": [
                "CCEmptySetHostsComponent",
                "CCEmptySetHostsService",
            ],
            "pipeline_plugins.components.collections.http.v1_0": ["HttpComponent", "HttpRequestService"],
            "pipeline.components.collections.sites.{}.job".format(settings.OPEN_VER): [
                "JobCronTaskComponent",
                "JobCronTaskService",
                "JobExecuteTaskComponent",
                "JobExecuteTaskService",
                "JobFastExecuteScriptComponent",
                "JobFastExecuteScriptService",
                "JobFastPushFileComponent",
                "JobFastPushFileService",
                "JobPushLocalFilesComponent",
                "JobPushLocalFilesService",
                "JobService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.batch_delete_set.legacy": [
                "CCBatchDeleteSetComponent",
                "CCBatchDeleteSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc": [
                "CCBatchDeleteSetComponent",
                "CCBatchDeleteSetService",
                "CCCreateSetComponent",
                "CCCreateSetService",
                "CCEmptySetHostsComponent",
                "CCEmptySetHostsService",
                "CCReplaceFaultMachineComponent",
                "CCReplaceFaultMachineService",
                "CCTransferHostModuleComponent",
                "CCTransferHostModuleService",
                "CCTransferHostToIdleComponent",
                "CCTransferHostToIdleService",
                "CCUpdateHostComponent",
                "CCUpdateHostService",
                "CCUpdateModuleComponent",
                "CCUpdateModuleService",
                "CCUpdateSetComponent",
                "CCUpdateSetService",
                "CCUpdateSetServiceStatusComponent",
                "CCUpdateSetServiceStatusService",
                "CmdbTransferFaultHostComponent",
                "CmdbTransferFaultHostService",
                "CmdbTransferHostResourceModuleComponent",
                "CmdbTransferHostResourceModuleService",
            ],
            "pipeline_plugins.components.collections.sites.open.cc.update_set.legacy": [
                "CCUpdateSetComponent",
                "CCUpdateSetService",
            ],
            "pipeline_plugins.components.collections.sites.open.nodeman.create_task.v2_0": [
                "NodemanCreateTaskComponent",
                "NodemanCreateTaskService",
            ],
            "pipeline.components.collections.sites.{}.cc".format(settings.OPEN_VER): [
                "CCBatchDeleteSetComponent",
                "CCBatchDeleteSetService",
                "CCCreateSetComponent",
                "CCCreateSetService",
                "CCEmptySetHostsComponent",
                "CCEmptySetHostsService",
                "CCReplaceFaultMachineComponent",
                "CCReplaceFaultMachineService",
                "CCTransferHostModuleComponent",
                "CCTransferHostModuleService",
                "CCTransferHostToIdleComponent",
                "CCTransferHostToIdleService",
                "CCUpdateHostComponent",
                "CCUpdateHostService",
                "CCUpdateModuleComponent",
                "CCUpdateModuleService",
                "CCUpdateSetComponent",
                "CCUpdateSetService",
                "CCUpdateSetServiceStatusComponent",
                "CCUpdateSetServiceStatusService",
                "CmdbTransferFaultHostComponent",
                "CmdbTransferFaultHostService",
                "CmdbTransferHostResourceModuleComponent",
                "CmdbTransferHostResourceModuleService",
            ],
            "pipeline.components.collections.controller": [
                "PauseComponent",
                "PauseService",
                "SleepTimerComponent",
                "SleepTimerService",
            ],
        }

    def test_import_path(self):
        for path, cls_list in self.assert_paths.items():
            mod = sys.modules[path]
            for clz_name in cls_list:
                clz = getattr(mod, clz_name)
                self.assertTrue(issubclass(clz, Service) or issubclass(clz, Component))

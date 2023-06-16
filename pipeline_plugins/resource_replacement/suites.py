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

import logging
import typing

from pipeline_plugins.components.collections.sites.open.cc.base import (
    cc_get_name_id_from_combine_value,
)

from . import base

logger = logging.getLogger("root")


class CCHostCustomPropertyChangeSuite(base.CmdbSuite):
    CODE = "cc_host_custom_property_change"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "cc_ip_list" in component["data"]:
            self.process_ip_list_str(node_id, component["data"]["cc_ip_list"])


class CCCreateSetSuite(base.CmdbSuite):
    CODE = "cc_create_set"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])
        if "cc_set_parent_select" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_set_parent_select"])
        if "cc_set_parent_select_topo" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_set_parent_select_topo"])
        if "cc_set_parent_select_text" in dict(component["data"]):
            self.process_topo_select_text(node_id, component["data"]["cc_set_parent_select_text"])


class CCCreateModuleSuite(base.CmdbSuite):
    CODE = "cc_create_module"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])
        if "cc_set_select_topo" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_set_select_topo"])
        if "cc_set_select_text" in component["data"]:
            self.process_topo_select_text(node_id, component["data"]["cc_set_select_text"])

        if "cc_module_infos_template" not in component["data"]:
            return

        attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(
            component["data"]["cc_module_infos_template"]
        )
        if not isinstance(attr_data["value"], list):
            return

        for template_info in attr_data["value"]:
            # 避免引用变量导致的解析失败
            try:
                name, inst_id = cc_get_name_id_from_combine_value(template_info["cc_service_template"])
                template_info["cc_service_template"] = f"{name}_{inst_id + self.suite_meta.offset}"
            except Exception:
                continue


class CCCreateSetBySetTemplateSuite(CCCreateSetSuite):
    CODE = "cc_create_set_by_template"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        super().do(node_id, component)

        if "cc_set_template" not in component["data"]:
            return

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(component["data"]["cc_set_template"])
        except ValueError:
            return

        if not isinstance(attr_data["value"], int):
            return

        attr_data["value"] = attr_data["value"] + self.suite_meta.offset


class CCUpdateModuleSuite(base.CmdbSuite):
    CODE = "cc_update_module"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])
        if "cc_module_select" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_module_select"])
        if "cc_module_select_topo" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_module_select_topo"])
        if "cc_module_select_text" in component["data"]:
            self.process_topo_select_text(node_id, component["data"]["cc_module_select_text"])


class CCEmptySetHostsSuite(base.CmdbSuite):
    CODE = "cc_empty_set_hosts"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])
        if "cc_set_select" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_set_select"])
        if "cc_set_select_topo" in component["data"]:
            self.process_topo_select(node_id, component["data"]["cc_set_select_topo"])
        if "cc_set_select_text" in component["data"]:
            self.process_topo_select_text(node_id, component["data"]["cc_set_select_text"])


class CCBatchDeleteSetSuite(CCEmptySetHostsSuite):
    CODE = "cc_batch_delete_set"
    TYPE = "component"


class CCUpdateSetSuite(CCEmptySetHostsSuite):
    CODE = "cc_update_set"
    TYPE = "component"


class CCUpdateSetServiceStatusSuite(CCEmptySetHostsSuite):
    CODE = "cc_update_set_service_status"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        super().do(node_id, component)

        if "set_list" not in component["data"]:
            return

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(component["data"]["set_list"])
        except ValueError:
            return

        if not isinstance(attr_data["value"], str):
            return

        set_new_str_ids: typing.List[str] = []
        try:
            for set_str_id in attr_data["value"].split(","):
                set_new_str_ids.append(str(int(set_str_id) + self.suite_meta.offset))
        except Exception:
            return

        attr_data["value"] = ",".join(set_new_str_ids)


class CCVarCmdbSetAllocationSuite(base.CmdbSuite):
    CODE = "set_allocation"
    TYPE = "var"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        config: typing.Dict[str, typing.Any] = component["value"]["config"]

        try:
            if config.get("set_template_id"):
                config["set_template_id"] = self.to_new_topo_select(config["set_template_id"])
        except Exception:
            pass

        try:
            for host_resource in config.get("host_resources") or []:
                host_resource["id"] = self.to_new_topo_select(host_resource["id"])
        except Exception:
            pass

        try:
            for module_detail in config.get("module_detail") or []:
                module_detail["id"] = module_detail["id"] + self.suite_meta.offset
        except Exception:
            pass


class CCVarIpPickerVariableSuite(base.CmdbSuite):
    CODE = "ip"
    TYPE = "var"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        new_var_ip_tree: typing.List[str] = []
        try:
            for topo_select in component["value"].get("var_ip_tree") or []:
                new_var_ip_tree.append(self.to_new_topo_select(topo_select))
        except Exception:
            pass

        if new_var_ip_tree:
            component["value"]["var_ip_tree"] = new_var_ip_tree

        try:
            component["value"]["var_ip_custom_value"] = self.to_new_ip_list_str_or_raise(
                component["value"]["var_ip_custom_value"]
            )
        except Exception:
            pass


class CCVarCmdbIpSelectorSuite(base.CmdbSuite):
    CODE = "ip_selector"
    TYPE = "var"

    def to_new_conditions(self, conditions: typing.List[typing.Dict[str, typing.Union[str, typing.List[str]]]]):
        for cond in conditions:
            if cond["field"] == "biz":
                cond["value"] = [
                    self.biz_old_name__new_name_map.get(biz_old_name, biz_old_name) for biz_old_name in cond["value"]
                ]
            elif cond["field"] == "host":
                try:
                    cond["value"] = [self.to_new_ip_list_str_or_raise(ip) for ip in cond["value"]]
                except Exception:
                    pass

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        for topo in component["value"].get("topo") or []:
            topo["bk_inst_id"] = topo["bk_inst_id"] + self.suite_meta.offset

        for host in component["value"].get("ip") or []:
            host["bk_host_id"] = host["bk_host_id"] + self.suite_meta.offset
            host["bk_cloud_id"] = self.to_new_cloud_id(host["bk_cloud_id"])
            if "cloud" in host:
                for cloud in host["cloud"]:
                    cloud["id"] = str(self.to_new_cloud_id(int(cloud["id"])))

        self.to_new_conditions(component["value"].get("filters") or [])
        self.to_new_conditions(component["value"].get("excludes") or [])


class CCVarCmdbIpFilterSuite(base.CmdbSuite):
    CODE = "ip_filter"
    TYPE = "var"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        try:
            component["value"]["origin_ips"] = self.to_new_ip_list_str_or_raise(component["value"]["origin_ips"])
        except Exception:
            pass


class CCVarSetModuleIpSelectorSuite(base.CmdbSuite):
    CODE = "set_module_ip_selector"
    TYPE = "var"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        try:
            component["value"]["var_ip_custom_value"] = self.to_new_ip_list_str_or_raise(
                component["value"]["var_ip_custom_value"]
            )
        except Exception:
            pass


class CCVarSetModuleSelectorSuite(base.CmdbSuite):
    CODE = "set_module_selector"
    TYPE = "var"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        try:
            component["value"]["bk_set_id"] = component["value"]["bk_set_id"] + self.suite_meta.offset
        except Exception:
            pass

        try:
            new_module_ids: typing.List[int] = []
            for module_id in component["value"]["bk_module_id"] or []:
                new_module_ids.append(module_id + self.suite_meta.offset)
            if new_module_ids:
                component["value"]["bk_module_id"] = new_module_ids
        except Exception:
            pass


class JobLocalContentUploadSuite(base.JobSuite):
    CODE = "job_local_content_upload"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "job_ip_list" in component["data"]:
            self.process_ip_list_str(node_id, component["data"]["job_ip_list"])


class JobPushLocalFilesSuite(base.JobSuite):
    CODE = "job_push_local_files"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])
        if "job_target_ip_list" in component["data"]:
            self.process_ip_list_str(node_id, component["data"]["job_target_ip_list"])


class JobFastPushFileSuite(JobLocalContentUploadSuite):
    CODE = "job_fast_push_file"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        super().do(node_id, component)

        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])

        self.to_new_ip_form(component, "job_source_files", "ip")
        self.to_new_ip_form(component, "job_dispatch_attr", "job_ip_list")


class JobFastExecuteScriptSuite(JobLocalContentUploadSuite):
    CODE = "job_fast_execute_script"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        super().do(node_id, component)

        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])


class JobCronTaskSuite(base.JobSuite):
    CODE = "job_cron_task"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])

        self.to_new_job_id(component, key="job_cron_job_id", resource_type="cron_job_id", source_data_type=int)


class JobExecuteTaskSuite(base.JobSuite):

    CODE = "job_execute_task"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])

        self.to_new_job_id(component, key="job_task_id", resource_type="task_plan_id", source_data_type=int)

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(component["data"]["job_global_var"])

            task_plan_variable_ids: typing.List[int] = [
                job_global_var["id"] for job_global_var in attr_data["value"] or []
            ]
            task_plan_variable_id_map: typing.Dict[int, int] = self.db_helper.fetch_resource_id_map(
                resource_type="task_plan_variable_id", source_data=task_plan_variable_ids, source_data_type=int
            )

            for job_global_var in attr_data["value"]:
                job_global_var["id"] = task_plan_variable_id_map.get(job_global_var["id"], job_global_var["id"])
                # IP 替换
                if job_global_var.get("category") == 3:
                    job_global_var["value"] = self.to_new_ip_list_str_or_raise(job_global_var["value"])

        except Exception:
            pass


class JobAllBizJobFastPushFileSuite(base.JobSuite):

    CODE = "all_biz_job_fast_push_file"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        self.to_new_cmdb_id_form(component, "job_dispatch_attr", "bk_cloud_id")
        self.to_new_cmdb_id_form(component, "job_source_files", "bk_cloud_id")


class JobAllBizJobFastExecuteScriptSuite(base.JobSuite):

    CODE = "all_biz_job_fast_execute_script"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        self.to_new_cmdb_id_form(component, "job_target_ip_table", "bk_cloud_id")


class JobAllBizJobExecuteJobPlanSuite(base.JobSuite):

    CODE = "all_biz_execute_job_plan"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):

        if "all_biz_job_config" not in component["data"]:
            return

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(
                component["data"]["all_biz_job_config"]
            )
        except ValueError:
            return

        task_template_id_map: typing.Dict[int, int] = self.db_helper.fetch_resource_id_map(
            resource_type="task_template_id", source_data=[attr_data["value"]["job_template_id"]], source_data_type=int
        )
        attr_data["value"]["job_template_id"] = task_template_id_map.get(
            attr_data["value"]["job_template_id"], attr_data["value"]["job_template_id"]
        )

        task_plan_id_map: typing.Dict[int, int] = self.db_helper.fetch_resource_id_map(
            resource_type="task_plan_id", source_data=[attr_data["value"]["job_plan_id"]], source_data_type=int
        )
        attr_data["value"]["job_plan_id"] = task_plan_id_map.get(
            attr_data["value"]["job_plan_id"], attr_data["value"]["job_plan_id"]
        )

        task_plan_variable_ids: typing.List[int] = [
            job_global_var["id"] for job_global_var in attr_data["value"].get("job_global_var") or []
        ]
        task_plan_variable_id_map: typing.Dict[int, int] = self.db_helper.fetch_resource_id_map(
            resource_type="task_plan_variable_id", source_data=task_plan_variable_ids, source_data_type=int
        )

        for job_global_var in attr_data["value"].get("job_global_var") or []:
            job_global_var["id"] = task_plan_variable_id_map.get(job_global_var["id"], job_global_var["id"])
            # IP 替换
            if job_global_var.get("category") == 3:
                job_global_var["value"] = self.to_new_ip_list_str_or_raise(job_global_var["value"])


class NodemanPluginOperateSuite(base.CmdbSuite):
    CODE = "nodeman_plugin_operate"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "biz_cc_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["biz_cc_id"])

        try:
            nodeman_host_info_attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(
                component["data"]["nodeman_host_info"]
            )
            nodeman_host_info_attr_data["value"]["nodeman_bk_cloud_id"] = self.to_new_cloud_id(
                nodeman_host_info_attr_data["value"]["nodeman_bk_cloud_id"]
            )
        except Exception:
            pass


class NodemanCreateTaskSuite(base.CmdbSuite):
    CODE = "nodeman_create_task"
    TYPE = "component"

    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        if "bk_biz_id" in component["data"]:
            self.process_cc_id(node_id, component["data"]["bk_biz_id"])

        try:
            nodeman_op_target_attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(
                component["data"]["nodeman_op_target"]
            )
            nodeman_op_target_attr_data["value"]["nodeman_bk_cloud_id"] = self.to_new_cloud_id(
                nodeman_op_target_attr_data["value"]["nodeman_bk_cloud_id"]
            )
        except Exception:
            pass

        try:
            nodeman_op_info_attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(
                component["data"]["nodeman_op_info"]
            )
            for host in nodeman_op_info_attr_data["value"]["nodeman_hosts"]:
                host["nodeman_bk_cloud_id"] = self.to_new_cloud_id(host["nodeman_bk_cloud_id"])
        except Exception:
            pass


SUITES = [
    CCHostCustomPropertyChangeSuite,
    CCCreateSetSuite,
    CCCreateModuleSuite,
    CCCreateSetBySetTemplateSuite,
    CCUpdateModuleSuite,
    CCEmptySetHostsSuite,
    CCBatchDeleteSetSuite,
    CCUpdateSetSuite,
    CCUpdateSetServiceStatusSuite,
    CCVarCmdbSetAllocationSuite,
    CCVarIpPickerVariableSuite,
    CCVarCmdbIpSelectorSuite,
    CCVarCmdbIpFilterSuite,
    CCVarSetModuleIpSelectorSuite,
    CCVarSetModuleSelectorSuite,
    JobLocalContentUploadSuite,
    JobPushLocalFilesSuite,
    JobFastPushFileSuite,
    JobFastExecuteScriptSuite,
    JobCronTaskSuite,
    JobExecuteTaskSuite,
    JobAllBizJobFastPushFileSuite,
    JobAllBizJobFastExecuteScriptSuite,
    JobAllBizJobExecuteJobPlanSuite,
    NodemanPluginOperateSuite,
    NodemanCreateTaskSuite,
]

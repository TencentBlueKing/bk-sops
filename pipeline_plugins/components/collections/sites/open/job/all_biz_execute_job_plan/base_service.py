# -*- coding: utf-8 -*-
import re
from copy import deepcopy
from functools import partial

from django.utils import translation
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.io import ArrayItemSchema, IntItemSchema, ObjectItemSchema, StringItemSchema

from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils import crypto
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.jobv3_cloud.shortcuts import get_client_by_username
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.job import Jobv3Service
from pipeline_plugins.components.collections.sites.open.job.ipv6_base import GetJobTargetServerMixin
from pipeline_plugins.components.query.sites.open.job import JOBV3_VAR_CATEGORY_IP, JOBV3_VAR_CATEGORY_PASSWORD
from pipeline_plugins.components.utils import (
    get_job_instance_url,
    get_node_callback_url,
    has_biz_set,
    is_cipher_structure,
    loose_strip,
    parse_passwd_value,
    plat_ip_reg,
)

__group_name__ = _("作业平台(JOB)")

job_handle_api_error = partial(handle_api_error, __group_name__)

plat_reg = re.compile(r"(\d+:)")


class BaseAllBizJobExecuteJobPlanService(Jobv3Service, GetJobTargetServerMixin):
    need_get_sops_var = True

    biz_scope_type = JobBizScopeType.BIZ_SET.value

    def inputs_format(self):
        return [
            self.InputItem(
                name=_("业务 ID"),
                key="all_biz_cc_id",
                type="string",
                schema=StringItemSchema(description=_("当前操作所属的 CMDB 业务 ID")),
            ),
            self.InputItem(
                name=_("作业模板 ID"),
                key="job_template_id",
                type="string",
                schema=StringItemSchema(description=_("作业模板 ID")),
            ),
            self.InputItem(
                name=_("执行方案 ID"),
                key="job_plan_id",
                type="string",
                schema=StringItemSchema(description=_("执行方案 ID")),
            ),
            self.InputItem(
                name=_("全局变量"),
                key="job_global_var",
                type="array",
                schema=ArrayItemSchema(
                    description=_("作业方案执行所需的全局变量列表"),
                    item_schema=ObjectItemSchema(
                        description=_("全局变量"),
                        property_schemas={
                            "type": IntItemSchema(
                                description=_("变量类型，字符串(1) 命名空间(2) IP(3) 密码(4) 数组(5)")
                            ),
                            "name": StringItemSchema(description=_("变量名")),
                            "value": StringItemSchema(description=_("变量值")),
                        },
                    ),
                ),
            ),
        ]

    def outputs_format(self):
        return super(BaseAllBizJobExecuteJobPlanService, self).outputs_format() + [
            self.OutputItem(
                name=_("JOB全局变量"),
                key="log_outputs",
                type="object",
                schema=ObjectItemSchema(
                    description=_("输出日志中提取的全局变量"),
                    property_schemas={
                        "name": StringItemSchema(description=_("全局变量名称")),
                        "value": StringItemSchema(description=_("全局变量值")),
                    },
                ),
            )
        ]

    def get_ip_list(self, val):
        """
        在IP_V6环境下, 直接传入字符串即可
        @param val:
        @return:
        """
        if settings.ENABLE_IPV6:
            return val
        plat_ip = [match.group() for match in plat_ip_reg.finditer(val)]
        ip_list = [{"ip": _ip.split(":")[1], "bk_cloud_id": _ip.split(":")[0]} for _ip in plat_ip]
        return ip_list

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        client = get_client_by_username(executor, stage=settings.BK_APIGW_STAGE_NAME)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        config_data = data.get_one_of_inputs("all_biz_job_config")
        biz_cc_id = config_data.get("all_biz_cc_id")
        supplier_account = supplier_account_for_business(biz_cc_id)
        is_tagged_ip = config_data.get("is_tagged_ip", False)
        data.inputs.biz_cc_id = biz_cc_id
        data.inputs.is_tagged_ip = is_tagged_ip
        original_global_var = deepcopy(config_data.get("job_global_var")) or []
        global_var_list = []

        if not has_biz_set(tenant_id, int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value

        for _value in original_global_var:

            if is_cipher_structure(_value["value"]):
                # 只有当变量值符合密码结构，才需要尝试解析密码变量
                try:
                    val = loose_strip(crypto.decrypt(parse_passwd_value(_value["value"])))
                except Exception:
                    self.logger.exception(
                        "[job_execute_task_base] failed to decrypt value -> {value}, use plaintext".format(
                            value=_value["value"]
                        )
                    )
                    val = loose_strip(_value["value"])
            else:
                val = loose_strip(_value["value"])

            if _value["type"] == JOBV3_VAR_CATEGORY_IP:

                ip_list = self.get_ip_list(val)
                result, server = self.get_target_server_biz_set(
                    tenant_id,
                    executor,
                    ip_list,
                    supplier_account=supplier_account,
                    logger_handle=self.logger,
                    need_build_ip=False,
                )

                if not result:
                    data.outputs.ex_data = "ip查询失败, 请检查ip配置是否正确，ip_list={}".format(ip_list)
                    return False

                if result:
                    global_var_list.append({"id": _value["id"], "server": server})
            # 密文变量在没有修改的情况下不加入全局变量，避免脱敏字符串作为正式值进行作业执行逻辑
            elif _value.get("category") == JOBV3_VAR_CATEGORY_PASSWORD and val == "******":
                continue
            else:
                global_var_list.append({"id": _value["id"], "value": val})

        job_kwargs = {
            "bk_scope_type": self.biz_scope_type,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "job_plan_id": config_data.get("job_plan_id"),
            "global_var_list": global_var_list,
            "callback_url": get_node_callback_url(self.root_pipeline_id, self.id, getattr(self, "version", "")),
        }

        job_result = client.api.execute_job_plan(job_kwargs, headers={"X-Bk-Tenant-Id": tenant_id})
        self.logger.info("job_result: {result}, job_kwargs: {kwargs}".format(result=job_result, kwargs=job_kwargs))
        if job_result["result"]:
            job_instance_id = job_result["data"]["job_instance_id"]
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result["data"]["job_instance_name"]
            data.outputs.client = client
            data.outputs.biz_cc_id = biz_cc_id
            return True
        else:
            message = job_handle_api_error("jobv3.execute_job_plan", job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        config_data = data.get_one_of_inputs("all_biz_job_config")
        biz_cc_id = int(config_data.get("all_biz_cc_id"))
        tenant_id = parent_data.get_one_of_inputs("tenant_id")
        if not has_biz_set(tenant_id, int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value
        return super().schedule(data, parent_data, callback_data)

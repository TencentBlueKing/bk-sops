# -*- coding: utf-8 -*-
import re
from copy import deepcopy
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.utils.handlers import handle_api_error
from pipeline_plugins.components.collections.sites.open.job import Jobv3Service
from pipeline_plugins.components.utils import (
    get_job_instance_url,
    get_node_callback_url,
    loose_strip,
    plat_ip_reg,
    has_biz_set,
)
from pipeline_plugins.components.query.sites.open.job import JOBV3_VAR_CATEGORY_IP

__group_name__ = _("作业平台(JOB)")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)

plat_reg = re.compile(r"(\d+:)")


class BaseAllBizJobExecuteJobPlanService(Jobv3Service):
    need_get_sops_var = True

    biz_scope_type = JobBizScopeType.BIZ_SET.value

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs("executor")
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs("language"):
            setattr(client, "language", parent_data.get_one_of_inputs("language"))
            translation.activate(parent_data.get_one_of_inputs("language"))

        config_data = data.get_one_of_inputs("all_biz_job_config")
        biz_cc_id = config_data.get("all_biz_cc_id")
        is_tagged_ip = config_data.get("is_tagged_ip", False)
        data.inputs.biz_cc_id = biz_cc_id
        data.inputs.is_tagged_ip = is_tagged_ip
        original_global_var = deepcopy(config_data.get("job_global_var")) or []
        global_var_list = []

        if not has_biz_set(int(biz_cc_id)):
            self.biz_scope_type = JobBizScopeType.BIZ.value

        for _value in original_global_var:
            # 3-IP
            val = loose_strip(_value["value"])
            if _value["type"] == JOBV3_VAR_CATEGORY_IP:

                plat_ip = [match.group() for match in plat_ip_reg.finditer(val)]
                ip_list = [{"ip": _ip.split(":")[1], "bk_cloud_id": _ip.split(":")[0]} for _ip in plat_ip]

                plats = plat_reg.findall(val)
                if len(ip_list) != len(plats):
                    data.outputs.ex_data = _("IP 校验失败，请确认输入的 IP {} 是否合法".format(val))
                    return False

                if ip_list:
                    global_var_list.append({"id": _value["id"], "server": {"ip_list": ip_list}})
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

        job_result = client.jobv3.execute_job_plan(job_kwargs)
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

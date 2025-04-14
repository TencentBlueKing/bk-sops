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
import time

from django.http import JsonResponse
from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from api.utils.request import batch_request
from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from gcloud.iam_auth.utils import check_and_raise_raw_auth_fail_exception
from gcloud.utils.cmdb import get_business_set_host
from gcloud.utils.handlers import handle_api_error
from packages.bkapi.jobv3_cloud.shortcuts import get_client_by_username
from pipeline_plugins.components.collections.sites.open.cc.ipv6_utils import format_host_with_ipv6

logger = logging.getLogger("root")

JOB_VAR_CATEGORY_CLOUD = 1
JOB_VAR_CATEGORY_CONTEXT = 2
JOB_VAR_CATEGORY_PASSWORD = 4
JOB_VAR_CATEGORY_GLOBAL_VARS = {JOB_VAR_CATEGORY_CLOUD, JOB_VAR_CATEGORY_CONTEXT, JOB_VAR_CATEGORY_PASSWORD}
JOB_VAR_CATEGORY_IP = 3
TEN_MINUTES_MILLISECONDS = 600000  # 十分钟的毫秒级时间戳

JOBV3_VAR_CATEGORY_STRING = 1
JOBV3_VAR_CATEGORY_NAMESPACE = 2
JOBV3_VAR_CATEGORY_IP = 3
JOBV3_VAR_CATEGORY_PASSWORD = 4
JOBV3_VAR_CATEGORY_ARRAY = 5
JOBV3_VAR_CATEGORY_GLOBAL_VARS = {
    JOBV3_VAR_CATEGORY_STRING,
    JOBV3_VAR_CATEGORY_NAMESPACE,
    JOBV3_VAR_CATEGORY_PASSWORD,
    JOBV3_VAR_CATEGORY_ARRAY,
}


def _job_get_scripts_data(request, biz_cc_id=None):
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    source_type = request.GET.get("type")
    script_type = request.GET.get("script_type")

    if biz_cc_id is None or source_type == "public":
        kwargs = {"script_language": script_type or 0}
        func = client.api.get_public_script_list
    else:
        kwargs = {
            "bk_scope_type": JobBizScopeType.BIZ.value,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "script_language": script_type or 0,
        }
        func = client.api.get_script_list

    script_list = batch_request(
        func=func,
        params=kwargs,
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
        check_iam_auth_fail=True,
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )

    return script_list


def job_get_script_name_list(request, biz_cc_id):
    script_list = _job_get_scripts_data(request, biz_cc_id)
    script_names = []
    for script in script_list:
        if script.get("online_script_version_id"):
            script_names.append({"text": script["name"], "value": script["name"]})
    return JsonResponse({"result": True, "data": script_names})


def job_get_public_script_name_list(request):
    script_list = _job_get_scripts_data(request)
    script_names = []
    for script in script_list:
        if script.get("online_script_version_id"):
            script_names.append({"text": script["name"], "value": script["name"]})
    return JsonResponse({"result": True, "data": script_names})


def job_get_script_list(request, biz_cc_id):
    """
    查询业务脚本列表
    :param request:
    :param biz_cc_id:
    :return:
    """
    value_field = request.GET.get("value_field") or "id"

    # 查询脚本列表
    script_list = _job_get_scripts_data(request, biz_cc_id)
    script_dict = {}
    for script in script_list:
        if isinstance(script[value_field], int):
            script_dict.setdefault(script["name"], []).append(script[value_field])

    version_data = []
    for name, version in list(script_dict.items()):
        version_data.append({"text": name, "value": max(version)})

    return JsonResponse({"result": True, "data": version_data})


def job_get_script_by_script_version(request, biz_cc_id):
    """
    根据script_version获取业务
    :param request:
    :param biz_cc_id:
    :return:
    """
    script_version = request.GET.get("script_version")
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)

    kwargs = {
        "bk_scope_type": JobBizScopeType.BIZ.value,
        "bk_scope_id": str(biz_cc_id),
        "bk_biz_id": biz_cc_id,
        "id": script_version,
    }
    result = client.api.get_script_version_detail(kwargs, headers={"X-Bk-Tenant-Id": request.user.tenant_id})
    if not result["result"]:
        check_and_raise_raw_auth_fail_exception(result)
        return JsonResponse(result)
    script_name = result["data"].get("name") or ""
    return JsonResponse({"result": True, "data": {"script_name": script_name}})


def job_get_job_tasks_by_biz(request, biz_cc_id):
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    plan_list = batch_request(
        func=client.api.get_job_plan_list,
        params={"bk_scope_type": JobBizScopeType.BIZ.value, "bk_scope_id": str(biz_cc_id), "bk_biz_id": biz_cc_id},
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
        check_iam_auth_fail=True,
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )
    task_list = []
    for task in plan_list:
        task_list.append({"value": task["id"], "text": task["name"]})
    return JsonResponse({"result": True, "data": task_list})


def job_get_job_task_detail(request, biz_cc_id, task_id):
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    tenant_id = request.user.tenant_id
    job_result = client.api.get_job_plan_detail(
        {
            "bk_scope_type": JobBizScopeType.BIZ.value,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "job_plan_id": task_id,
        },
        headers={"X-Bk-Tenant-Id": tenant_id},
    )

    if not job_result["result"]:
        message = _(
            f"请求执行方案失败: 查询作业平台(JOB)的作业模板详情[app_id={biz_cc_id}]接口jobv3.get_job_plan_detail. "
            f"返回失败: {job_result['message']}. 请重试, 如持续失败请联系管理员处理 | job_get_job_task_detail"
        )
        check_and_raise_raw_auth_fail_exception(job_result, message)

        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    job_step_type_name = {1: _("脚本"), 2: _("文件"), 4: "SQL"}
    task_detail = job_result["data"]
    global_var = []
    steps = []
    if not task_detail:
        message = _(f"请求执行方案失败: 请求作业平台执行方案详情返回数据为空: {job_result}. 请重试, 如持续失败请联系管理员处理 | job_get_job_task_detail")
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    global_var_list = task_detail.get("global_var_list") or []
    for var in global_var_list:
        # 1-字符串, 2-IP, 3-索引数组, 4-关联数组
        if not var.get("used", True):
            continue
        if var["type"] in JOB_VAR_CATEGORY_GLOBAL_VARS:
            value = var.get("value", "")
        elif var["type"] == JOB_VAR_CATEGORY_IP:
            if settings.ENABLE_IPV6:
                bk_host_ids = [int(ip_item["bk_host_id"]) for ip_item in var.get("server", {}).get("ip_list") or []]
                hosts = get_business_set_host(
                    tenant_id,
                    request.user.username,
                    host_fields=["bk_host_id", "bk_host_innerip", "bk_host_innerip_v6", "bk_cloud_id"],
                    ip_list=bk_host_ids,
                    filter_field="bk_host_id",
                )
                value = ",".join([format_host_with_ipv6(host, with_cloud=True) for host in hosts])
            else:
                value = ",".join(
                    [
                        "{plat_id}:{ip}".format(plat_id=ip_item["bk_cloud_id"], ip=ip_item["ip"])
                        for ip_item in var.get("server", {}).get("ip_list") or []
                    ]
                )
        else:
            message = _(f"执行历史请求失败: 请求[作业平台]执行历史列表发生异常: 未知类型变量: {var} | job_get_job_task_detail")
            logger.warning(message)
            continue

        global_var.append(
            {
                "id": var["id"],
                # 全局变量类型：1:云参, 2:上下文参数，3:IPs
                "category": var.get("type", 1),
                "name": var["name"],
                "value": value,
                "description": var["description"],
            }
        )
    for info in task_detail.get("step_list", []):
        script_info = info["script_info"] or {}
        # 1-执行脚本, 2-传文件, 4-传SQL
        steps.append(
            {
                "stepId": info["id"],
                "name": info["name"],
                "scriptParams": script_info.get("script_param", ""),
                "account": script_info.get("account", {}).get("id", ""),
                "ipList": "",
                "type": info["type"],
                "type_name": job_step_type_name.get(info["type"], info["type"]),
            }
        )
    return JsonResponse({"result": True, "data": {"global_var": global_var, "steps": steps}})


def job_get_instance_detail(request, biz_cc_id, task_id):
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    log_kwargs = {
        "bk_scope_type": bk_scope_type,
        "bk_scope_id": str(biz_cc_id),
        "bk_biz_id": biz_cc_id,
        "job_instance_id": task_id,
    }
    job_result = client.api.get_job_instance_ip_log(log_kwargs, headers={"X-Bk-Tenant-Id": request.user.tenant_id})
    if not job_result["result"]:
        message = _(
            f"执行历史请求失败: 查询作业平台(JOB)的作业模板[app_id={biz_cc_id}]接口job.get_task. "
            f"异常消息: {job_result['message']} | job_get_instance_detail"
        )
        check_and_raise_raw_auth_fail_exception(job_result, message)
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    ip_details = {}
    for step in job_result["data"]:
        for step_result in step["step_results"]:
            for ip_log in step_result["ip_logs"]:
                detail = ip_details.setdefault(ip_log["ip"], {})

                detail.setdefault("log", []).extend(
                    ["step: {}\n".format(step["step_instance_id"]), ip_log["log_content"]]
                )
                detail["exit_code"] = ip_log["exit_code"]

    data = []
    for ip, detail in ip_details.items():
        data.append({"ip": ip, "log": "".join(detail["log"]), "exit_code": detail["exit_code"]})

    return JsonResponse({"result": True, "data": data})


def jobv3_get_job_template_list(request, biz_cc_id):
    """
    根据业务ID查询作业模版列表
    @param request:
    @param biz_cc_id: 业务 ID
    @return:
    """
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    template_list = batch_request(
        func=client.api.get_job_template_list,
        params={"bk_scope_type": bk_scope_type, "bk_scope_id": str(biz_cc_id), "bk_biz_id": biz_cc_id},
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
        check_iam_auth_fail=True,
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )

    data = []
    for template in template_list:
        data.append({"value": template["id"], "text": template["name"]})
    return JsonResponse({"result": True, "data": data})


def jobv3_get_job_plan_list(request, biz_cc_id, job_template_id):
    """
    查询执行方案列表
    @param request:
    @param biz_cc_id: 业务 ID
    @param job_template_id: 作业模版 ID
    @return:
    """
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    plan_list = batch_request(
        func=client.api.get_job_plan_list,
        params={
            "bk_scope_type": bk_scope_type,
            "bk_scope_id": str(biz_cc_id),
            "bk_biz_id": biz_cc_id,
            "job_template_id": job_template_id,
        },
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
        check_iam_auth_fail=True,
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )

    data = []
    for plan in plan_list:
        data.append({"value": plan["id"], "text": plan["name"]})
    return JsonResponse({"result": True, "data": data})


def jobv3_get_job_plan_detail(request, biz_cc_id, job_plan_id):
    """
    根据作业执行方案 ID 查询作业执行方案详情
    @param request:
    @param biz_cc_id: 业务 ID
    @param job_plan_id: 作业执行方案 ID
    @return:
    """
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    tenant_id = request.user.tenant_id
    kwargs = {
        "bk_scope_type": bk_scope_type,
        "bk_scope_id": str(biz_cc_id),
        "bk_biz_id": biz_cc_id,
        "job_plan_id": job_plan_id,
    }

    jobv3_result = client.api.get_job_plan_detail(kwargs, headers={"X-Bk-Tenant-Id": tenant_id})
    if not jobv3_result["result"]:
        check_and_raise_raw_auth_fail_exception(jobv3_result)
        message = handle_api_error("jobv3", "get_job_plan_detail", kwargs, jobv3_result)
        logger.error(message)
        result = {"result": False, "message": message}
        return JsonResponse(result)

    plan_detail = jobv3_result["data"]
    global_var = []
    if not plan_detail:
        message = _(f"请求执行方案失败: 请求作业平台执行方案详情返回数据为空: {jobv3_result}. 请重试, 如持续失败请联系管理员处理 | jobv3_get_job_plan_detail")
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    for var in plan_detail.get("global_var_list") or []:
        # 1-字符串, 2-命名空间, 3-IP, 4-密码, 5-数组
        if var["type"] in JOBV3_VAR_CATEGORY_GLOBAL_VARS:
            value = var.get("value", "")
        elif var["type"] == JOBV3_VAR_CATEGORY_IP:
            if settings.ENABLE_IPV6:
                bk_host_ids = [int(ip_item["bk_host_id"]) for ip_item in var.get("server", {}).get("ip_list") or []]
                hosts = get_business_set_host(
                    tenant_id,
                    request.user.username,
                    host_fields=["bk_host_id", "bk_host_innerip", "bk_host_innerip_v6", "bk_cloud_id"],
                    ip_list=bk_host_ids,
                    filter_field="bk_host_id",
                )
                value = ",".join([format_host_with_ipv6(host, with_cloud=True) for host in hosts])
            else:
                value = ",".join(
                    [
                        "{plat_id}:{ip}".format(plat_id=ip_item["bk_cloud_id"], ip=ip_item["ip"])
                        for ip_item in var.get("server", {}).get("ip_list") or []
                    ]
                )
        else:
            message = _(f"执行历史请求失败: 请求[作业平台]执行历史列表发生异常: 未知类型变量: {var} | jobv3_get_job_plan_detail")
            logger.error(message)
            result = {"result": False, "message": message}
            return JsonResponse(result)

        global_var.append(
            {
                "id": var["id"],
                "type": var.get("type", 1),
                "name": var["name"],
                "value": value,
                "description": var["description"],
            }
        )

    return JsonResponse({"result": True, "data": global_var})


def jobv3_get_instance_list(request, biz_cc_id, type, status):
    username = request.user.username
    client = get_client_by_username(username, stage=settings.BK_APIGW_STAGE_NAME)
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    job_kwargs = {
        "bk_scope_type": bk_scope_type,
        "bk_scope_id": str(biz_cc_id),
        "bk_biz_id": biz_cc_id,
        "create_time_end": int(round(time.time() * 1000)) + TEN_MINUTES_MILLISECONDS * 1,
        "create_time_start": int(round(time.time() * 1000)) - TEN_MINUTES_MILLISECONDS * 1,  # 取一天前到一天后这段时间的历史
        "operator": username,
        "status": int(status),
        "type": int(type),
    }
    job_result = client.api.get_job_instance_list(job_kwargs, headers={"X-Bk-Tenant-Id": request.user.tenant_id})
    if not job_result["result"]:
        message = _(
            f"请求执行方案失败: 查询作业平台(JOB)的作业模板[app_id={biz_cc_id}]接口jobv3.get_job_instance_list."
            f"返回失败: {job_result['message']}. 请重试, 如持续失败请联系管理员处理 | jobv3_get_instance_list"
        )

        check_and_raise_raw_auth_fail_exception(job_result, message)
        logger.error(message)
        return JsonResponse({"result": False, "message": message})
    result_data = job_result["data"]["data"]
    if not result_data:
        return JsonResponse({"result": True, "data": []})
    data = [{"text": job["name"], "value": job["job_instance_id"]} for job in result_data]
    return JsonResponse({"result": True, "data": data})


def get_job_account_list(request, biz_cc_id):
    bk_scope_type = request.GET.get("bk_scope_type", JobBizScopeType.BIZ.value)
    job_kwargs = {"bk_scope_id": biz_cc_id, "bk_scope_type": bk_scope_type, "category": 1}
    client = get_client_by_username(request.user.username, stage=settings.BK_APIGW_STAGE_NAME)
    account_list = batch_request(
        client.api.get_account_list,
        job_kwargs,
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        limit=500,
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
        check_iam_auth_fail=True,
        headers={"X-Bk-Tenant-Id": request.user.tenant_id},
    )

    if not account_list:
        return JsonResponse({"result": True, "data": []})

    data = [{"text": account["alias"], "value": account["alias"]} for account in account_list]
    return JsonResponse({"result": True, "data": data})


job_urlpatterns = [
    re_path(r"^job_get_script_list/(?P<biz_cc_id>\d+)/$", job_get_script_list),
    re_path(r"^get_job_account_list/(?P<biz_cc_id>\d+)/$", get_job_account_list),
    re_path(r"^job_get_script_name_list/(?P<biz_cc_id>\d+)/$", job_get_script_name_list),
    re_path(r"^job_get_public_script_name_list/$", job_get_public_script_name_list),
    re_path(r"^job_get_script_by_script_version/(?P<biz_cc_id>\d+)/$", job_get_script_by_script_version),
    re_path(r"^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$", job_get_job_tasks_by_biz),
    re_path(
        r"^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$",
        job_get_job_task_detail,
    ),
    re_path(r"^job_get_instance_detail/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$", job_get_instance_detail),
    # jobv3接口
    re_path(r"^jobv3_get_job_template_list/(?P<biz_cc_id>\d+)/$", jobv3_get_job_template_list),
    re_path(r"^jobv3_get_job_plan_list/(?P<biz_cc_id>\d+)/(?P<job_template_id>\d+)/$", jobv3_get_job_plan_list),
    re_path(r"^jobv3_get_job_plan_detail/(?P<biz_cc_id>\d+)/(?P<job_plan_id>\d+)/$", jobv3_get_job_plan_detail),
    re_path(r"^jobv3_get_instance_list/(?P<biz_cc_id>\d+)/(?P<type>\d+)/(?P<status>\d+)/$", jobv3_get_instance_list),
]

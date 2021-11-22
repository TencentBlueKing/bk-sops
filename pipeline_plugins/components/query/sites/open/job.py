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

import logging
import time

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url

from api.utils.request import batch_request
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE
from iam.exceptions import RawAuthFailedException

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

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
    client = get_client_by_user(request.user.username)
    source_type = request.GET.get("type")
    script_type = request.GET.get("script_type")

    if source_type == "public":
        kwargs = None
        script_result = client.job.get_public_script_list()
        api_name = "job.get_public_script_list"
    else:
        kwargs = {
            "bk_biz_id": biz_cc_id,
            "is_public": False,
            "script_type": script_type or 0,
        }
        script_result = client.job.get_script_list(kwargs)
        api_name = "job.get_script_list"

    if not script_result["result"]:
        message = handle_api_error("job", api_name, kwargs, script_result)
        logger.error(message)
        result = {"result": False, "message": message}
        return result

    return script_result


def job_get_script_name_list(request, biz_cc_id):
    script_result = _job_get_scripts_data(request, biz_cc_id)
    if not script_result["result"]:
        return JsonResponse(script_result)
    script_names = []
    for script in script_result["data"]["data"]:
        script_names.append({"text": script["name"], "value": script["name"]})
    return JsonResponse({"result": True, "data": script_names})


def job_get_public_script_name_list(request):
    script_result = _job_get_scripts_data(request)
    if not script_result["result"]:
        return JsonResponse(script_result)
    script_names = []
    for script in script_result["data"]["data"]:
        script_names.append({"text": script["name"], "value": script["name"]})
    return JsonResponse({"result": True, "data": script_names})


def job_get_script_list(request, biz_cc_id):
    """
    查询业务脚本列表
    :param request:
    :param biz_cc_id:
    :return:
    """
    # 查询脚本列表
    script_result = _job_get_scripts_data(request, biz_cc_id)
    if not script_result["result"]:
        return JsonResponse(script_result)
    script_dict = {}
    for script in script_result["data"]["data"]:
        script_dict.setdefault(script["name"], []).append(script["id"])

    version_data = []
    for name, version in list(script_dict.items()):
        version_data.append({"text": name, "value": max(version)})

    return JsonResponse({"result": True, "data": version_data})


def job_get_own_db_account_list(request, biz_cc_id):
    """
    查询用户有权限的DB帐号列表
    :param biz_cc_id:
    :param request:
    :return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": biz_cc_id}
    job_result = client.job.get_own_db_account_list(kwargs)

    if not job_result["result"]:
        message = handle_api_error("job", "get_own_db_account_list", kwargs, job_result)
        logger.error(message)
        result = {"result": False, "message": message}
        return JsonResponse(result)

    data = [{"text": item["db_alias"], "value": item["db_account_id"]} for item in job_result["data"]]

    return JsonResponse({"result": True, "data": data})


def job_get_job_tasks_by_biz(request, biz_cc_id):
    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_list({"bk_biz_id": biz_cc_id})
    if not job_result["result"]:
        message = _("查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (biz_cc_id, job_result["message"],)

        if job_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=job_result.get("permission", {}))

        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)
    task_list = []
    for task in job_result["data"]:
        task_list.append({"value": task["bk_job_id"], "text": task["name"]})
    return JsonResponse({"result": True, "data": task_list})


def job_get_job_task_detail(request, biz_cc_id, task_id):
    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_detail({"bk_biz_id": biz_cc_id, "bk_job_id": task_id})
    if not job_result["result"]:

        message = _("查询作业平台(JOB)的作业模板详情[app_id=%s]接口job.get_task_detail返回失败: %s") % (biz_cc_id, job_result["message"],)

        if job_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=job_result.get("permission", {}))

        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    job_step_type_name = {1: _("脚本"), 2: _("文件"), 4: "SQL"}
    task_detail = job_result["data"]
    global_var = []
    steps = []
    if not task_detail:
        message = "请求作业平台执行方案详情返回数据为空: {}".format(job_result)
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    for var in task_detail.get("global_vars", []):
        # 1-字符串, 2-IP, 3-索引数组, 4-关联数组
        if var["category"] in JOB_VAR_CATEGORY_GLOBAL_VARS:
            value = var.get("value", "")
        elif var["category"] == JOB_VAR_CATEGORY_IP:
            value = ",".join(
                [
                    "{plat_id}:{ip}".format(plat_id=ip_item["bk_cloud_id"], ip=ip_item["ip"])
                    for ip_item in var.get("ip_list", [])
                ]
            )
        else:
            logger.warning("unknow type var: {}".format(var))
            continue

        global_var.append(
            {
                "id": var["id"],
                # 全局变量类型：1:云参, 2:上下文参数，3:IPs
                "category": var.get("category", 1),
                "name": var["name"],
                "value": value,
                "description": var["description"],
            }
        )
    for info in task_detail.get("steps", []):
        # 1-执行脚本, 2-传文件, 4-传SQL
        steps.append(
            {
                "stepId": info["step_id"],
                "name": info["name"],
                "scriptParams": info.get("script_param", ""),
                "account": info.get("account", ""),
                "ipList": "",
                "type": info["type"],
                "type_name": job_step_type_name.get(info["type"], info["type"]),
            }
        )
    return JsonResponse({"result": True, "data": {"global_var": global_var, "steps": steps}})


def job_get_instance_detail(request, biz_cc_id, task_id):
    client = get_client_by_user(request.user.username)
    log_kwargs = {"bk_biz_id": biz_cc_id, "job_instance_id": task_id}
    job_result = client.job.get_job_instance_log(log_kwargs)
    if not job_result["result"]:
        message = _("查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (biz_cc_id, job_result["message"])

        if job_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=job_result.get("permission", []))

        logger.error(message)

    if not job_result["result"]:
        return JsonResponse(
            {"result": False, "message": "job instance log fetch error: {}".format(job_result["message"])}
        )

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
    client = get_client_by_user(request.user.username)
    template_list = batch_request(
        func=client.jobv3.get_job_template_list,
        params={"bk_biz_id": biz_cc_id},
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
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
    client = get_client_by_user(request.user.username)
    plan_list = batch_request(
        func=client.jobv3.get_job_plan_list,
        params={"bk_biz_id": biz_cc_id, "job_template_id": job_template_id},
        get_data=lambda x: x["data"]["data"],
        get_count=lambda x: x["data"]["total"],
        page_param={"cur_page_param": "start", "page_size_param": "length"},
        is_page_merge=True,
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
    client = get_client_by_user(request.user.username)
    kwargs = {"bk_biz_id": biz_cc_id, "job_plan_id": job_plan_id}

    jobv3_result = client.jobv3.get_job_plan_detail(kwargs)
    if not jobv3_result["result"]:
        message = handle_api_error("jobv3", "get_job_plan_detail", kwargs, jobv3_result)
        logger.error(message)
        result = {"result": False, "message": message}
        return JsonResponse(result)

    plan_detail = jobv3_result["data"]
    global_var = []
    if not plan_detail:
        message = _("请求作业平台执行方案详情返回数据为空: {}").format(jobv3_result)
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    for var in plan_detail.get("global_var_list") or []:
        # 1-字符串, 2-命名空间, 3-IP, 4-密码, 5-数组
        if var["type"] in JOBV3_VAR_CATEGORY_GLOBAL_VARS:
            value = var.get("value", "")
        elif var["type"] == JOBV3_VAR_CATEGORY_IP:
            value = ",".join(
                [
                    "{plat_id}:{ip}".format(plat_id=ip_item["bk_cloud_id"], ip=ip_item["ip"])
                    for ip_item in var.get("server", {}).get("ip_list") or []
                ]
            )
        else:
            message = "unknow type var: {}".format(var)
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


def job_get_instance_list(request, biz_cc_id, type, status):
    username = request.user.username
    client = get_client_by_user(username)

    job_kwargs = {
        "bk_biz_id": biz_cc_id,
        "create_time_end": int(round(time.time() * 1000)) + TEN_MINUTES_MILLISECONDS * 1,
        "create_time_start": int(round(time.time() * 1000)) - TEN_MINUTES_MILLISECONDS * 1,  # 取一天前到一天后这段时间的历史
        "operator": username,
        "status": int(status),
        "type": int(type),
    }
    job_result = client.jobv3.get_job_instance_list(job_kwargs)
    if not job_result["result"]:
        message = _("查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_job_instance_list返回失败: %s") % (
            biz_cc_id,
            job_result["message"],
        )

        if job_result.get("code", 0) == HTTP_AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise RawAuthFailedException(permissions=job_result.get("permission", []))
        logger.error(message)
        return JsonResponse(
            {"result": False, "message": "job instance list fetch error: {}".format(job_result["message"])}
        )
    result_data = job_result["data"]["data"]
    if not result_data:
        return JsonResponse({"result": True, "data": []})
    data = [{"text": job["name"], "value": job["job_instance_id"]} for job in result_data]
    return JsonResponse({"result": True, "data": data})


job_urlpatterns = [
    url(r"^job_get_script_list/(?P<biz_cc_id>\d+)/$", job_get_script_list),
    url(r"^job_get_script_name_list/(?P<biz_cc_id>\d+)/$", job_get_script_name_list),
    url(r"^job_get_public_script_name_list/$", job_get_public_script_name_list),
    url(r"^job_get_own_db_account_list/(?P<biz_cc_id>\d+)/$", job_get_own_db_account_list,),
    url(r"^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$", job_get_job_tasks_by_biz),
    url(r"^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$", job_get_job_task_detail,),
    url(r"^job_get_instance_detail/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$", job_get_instance_detail),
    # jobv3接口
    url(r"^jobv3_get_job_template_list/(?P<biz_cc_id>\d+)/$", jobv3_get_job_template_list),
    url(r"^jobv3_get_job_plan_list/(?P<biz_cc_id>\d+)/(?P<job_template_id>\d+)/$", jobv3_get_job_plan_list),
    url(r"^jobv3_get_job_plan_detail/(?P<biz_cc_id>\d+)/(?P<job_plan_id>\d+)/$", jobv3_get_job_plan_detail),
    url(r"^job_get_instance_list/(?P<biz_cc_id>\d+)/(?P<type>\d+)/(?P<status>\d+)/$", job_get_instance_list),
]

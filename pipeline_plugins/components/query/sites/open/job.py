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
import logging

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url

from auth_backend.constants import AUTH_FORBIDDEN_CODE
from auth_backend.exceptions import AuthFailedException

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

JOB_VAR_CATEGORY_CLOUD = 1
JOB_VAR_CATEGORY_CONTEXT = 2
JOB_VAR_CATEGORY_GLOBAL_VARS = {JOB_VAR_CATEGORY_CLOUD, JOB_VAR_CATEGORY_CONTEXT}
JOB_VAR_CATEGORY_IP = 3


def job_get_script_list(request, biz_cc_id):
    """
    查询业务脚本列表
    :param request:
    :param biz_cc_id:
    :return:
    """
    # 查询脚本列表
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
        return JsonResponse(result)

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

        if job_result.get("code", 0) == AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise AuthFailedException(permissions=job_result.get("permission", []))

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

        if job_result.get("code", 0) == AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise AuthFailedException(permissions=job_result.get("permission", []))

        logger.error(message)
        result = {"result": False, "data": [], "message": message}
        return JsonResponse(result)

    job_step_type_name = {1: _("脚本"), 2: _("文件"), 4: "SQL"}
    task_detail = job_result["data"]
    global_var = []
    steps = []
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


job_urlpatterns = [
    url(r"^job_get_script_list/(?P<biz_cc_id>\d+)/$", job_get_script_list),
    url(r"^job_get_own_db_account_list/(?P<biz_cc_id>\d+)/$", job_get_own_db_account_list,),
    url(r"^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$", job_get_job_tasks_by_biz),
    url(r"^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$", job_get_job_task_detail,),
]

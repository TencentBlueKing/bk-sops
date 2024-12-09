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
import traceback

from django.http import JsonResponse
from django.urls import re_path
from django.utils.translation import ugettext_lazy as _
from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed

from files.factory import BartenderFactory, ManagerFactory
from files.models import UploadTicket
from gcloud.conf import settings
from gcloud.core.models import EnvironmentVariables
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def _check_and_get_file_manager():
    file_manager_type = EnvironmentVariables.objects.get_var("BKAPP_FILE_MANAGER_TYPE")
    if not file_manager_type:
        return False, _("File Manager 未配置，请联系管理员进行配置")

    try:
        file_manager = ManagerFactory.get_manager(manager_type=file_manager_type)
    except Exception as e:
        logger.error(
            "[FILE_UPLOAD]can not get file manager for type: {}\n err: {}".format(
                file_manager_type, traceback.format_exc()
            )
        )
        return False, str(e)
    return True, file_manager


def file_upload(request):
    """
    @summary: 本地文件上传
    @param request:
    @return:
    """

    project_id = request.META["HTTP_APP_PROJECTID"]
    iam = get_iam_client()
    subject = Subject("user", request.user.username)
    action = Action(IAMMeta.PROJECT_VIEW_ACTION)
    resources = res_factory.resources_for_project(project_id)
    allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources, cache=True)

    ticket = request.META.get("HTTP_UPLOAD_TICKET", "")
    ok, err = UploadTicket.objects.check_ticket(ticket)
    if not ok:
        message = _(f"文件上传失败: 上传信息校验失败, 请重试, 如持续失败可联系管理员处理. {err} | file_upload")
        logger.error(message)
        response = JsonResponse({"result": False, "message": message})
        response.status_code = 400
        return response

    ok, data = _check_and_get_file_manager()
    if not ok:
        return JsonResponse({"result": False, "message": data})
    file_manager = data
    logger.info("[FILE_UPLOAD]file_upload POST: {}".format(request.POST))

    bartender = BartenderFactory.get_bartender(manager_type=file_manager.type, manager=file_manager)

    kwargs = {"specific_username": settings.SYSTEM_USE_API_ACCOUNT}

    result = bartender.process_request(request, **kwargs)

    if result["result"] is True:
        bartender.post_handle_upload_process(data=result["tag"], username=request.user.username)
    return JsonResponse(result, status=result.pop("code", 200))


def apply_upload_ticket(request):

    ticket = UploadTicket.objects.apply(request.user.username, request.META.get("REMOTE_ADDR", ""))

    return JsonResponse({"result": True, "data": {"ticket": ticket.code}})


def get_repo_temporary_upload_url(request):
    bk_biz_id = request.GET.get("bk_biz_id")
    name = request.GET.get("name")
    shims = request.GET.get("shims", "frontend_upload")

    if not str(bk_biz_id) or not str(name):
        message = _(
            "文件上传失败: 业务ID和业务名称都应该提供.请重试, 如持续失败可联系管理员处理.  | get_repo_temporary_upload_url"
        )
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    ok, data = _check_and_get_file_manager()
    if not ok:
        return JsonResponse({"result": False, "message": data})
    file_manager = data
    return JsonResponse(file_manager.generate_temporary_url(bk_biz_id=bk_biz_id, name=name, shims=shims))


file_upload_urlpatterns = [
    re_path(r"^file_upload/$", file_upload),
    re_path(r"^apply_upload_ticket/$", apply_upload_ticket),
    re_path(r"^get_repo_temporary_upload_url/$", get_repo_temporary_upload_url),
]

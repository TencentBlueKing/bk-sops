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
import traceback

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt

from files.models import UploadTicket
from files.factory import ManagerFactory, BartenderFactory

from gcloud.conf import settings
from gcloud.core.models import EnvironmentVariables

logger = logging.getLogger("root")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@login_exempt
@csrf_exempt
def file_upload(request):
    """
    @summary: 本地文件上传
    @param request:
    @return:
    """

    ticket = request.META.get("HTTP_UPLOAD_TICKET", "")
    ok, err = UploadTicket.objects.check_ticket(ticket)
    if not ok:
        response = JsonResponse({"result": False, "message": "upload ticket check error: {}".format(err)})
        response.status_code = 400
        return response

    file_manager_type = EnvironmentVariables.objects.get_var("BKAPP_FILE_MANAGER_TYPE")
    if not file_manager_type:
        return JsonResponse({"result": False, "message": _("File Manager 未配置，请联系管理员进行配置")})

    try:
        file_manager = ManagerFactory.get_manager(manager_type=file_manager_type)
    except Exception as e:
        logger.error(
            "[FILE_UPLOAD]can not get file manager for type: {}\n err: {}".format(
                file_manager_type, traceback.format_exc()
            )
        )
        return JsonResponse({"result": False, "message": str(e)})

    logger.info("[FILE_UPLOAD]file_upload POST: {}".format(request.POST))

    bartender = BartenderFactory.get_bartender(manager_type=file_manager_type, manager=file_manager)

    return bartender.process_request(request)


def apply_upload_ticket(request):

    ticket = UploadTicket.objects.apply(request.user.username, request.META.get("REMOTE_ADDR", ""))

    return JsonResponse({"result": True, "data": {"ticket": ticket.code}})


file_upload_urlpatterns = [
    url(r"^file_upload/$", file_upload),
    url(r"^apply_upload_ticket/$", apply_upload_ticket),
]

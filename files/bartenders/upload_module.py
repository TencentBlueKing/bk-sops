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

import re
import logging
import traceback

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

from .base import UploadRequestBartender

logger = logging.getLogger("root")

INVALID_CHAR_REGEX = re.compile('[\u4e00-\u9fa5\\/:*?"<>|,]')


class UploadModuleBartender(UploadRequestBartender):
    def process_request(self, request):
        file_name = request.POST.get("file_name")
        file_path = request.POST.get("file_local_path")
        source_ip = request.POST.get("file_locate_ip")

        if not file_name:
            logger.error("[FILE_UPLOAD]invalid file_name: {}".format(file_name))
            response = JsonResponse({"result": False, "message": "invalid file_name"})
            response.status_code = 400
            return response

        if INVALID_CHAR_REGEX.findall(file_name):
            message = _('文件上传失败，文件名不能包含中文和\\/:*?"<>|等特殊字符')
            logger.error("[FILE_UPLOAD]invalid file_name: {}".format(message))
            response = JsonResponse({"result": False, "message": message})
            response.status_code = 400
            return response

        if not file_path:
            logger.error("[FILE_UPLOAD]invalid file_path: {}".format(file_path))
            response = JsonResponse({"result": False, "message": "invalid file_path"})
            response.status_code = 400
            return response

        if not source_ip:
            logger.error("[FILE_UPLOAD]invalid source_ip: {}".format(source_ip))
            response = JsonResponse({"result": False, "message": "invalid source_ip"})
            response.status_code = 400
            return response

        try:
            file_tag = self.manager.save(name=file_name, content=None, source_ip=source_ip, file_path=file_path)
        except Exception:
            logger.error("[FILE_UPLOAD]file upload save err: {}".format(traceback.format_exc()))
            response = JsonResponse({"result": False, "message": _("文件上传归档失败，请联系管理员")})
            response.status_code = 500
            return response

        logger.info("[FILE_UPLOAD] will return: {}".format(file_tag))
        return JsonResponse({"result": True, "tag": file_tag})

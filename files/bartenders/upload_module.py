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
import re
import logging
import traceback

from django.utils.translation import ugettext_lazy as _

from .base import UploadRequestBartender

logger = logging.getLogger("root")

INVALID_CHAR_REGEX = re.compile('[\\/:*?"<>|,]')


class UploadModuleBartender(UploadRequestBartender):
    def process_request(self, request, *args, **kwargs):
        file_name = request.POST.get("file_name")
        file_path = request.POST.get("file_local_path")
        source_ip = request.POST.get("file_locate_ip")
        file_local_md5 = request.POST.get("file_local_md5")

        if not file_name:
            message = _(f"文件上传失败: 文件名[{file_name}]不符合要求, 请修改后重试 | process_request")
            logger.error(message)
            return {"result": False, "message": message, "code": 400}

        if INVALID_CHAR_REGEX.findall(file_name):
            message = _('文件上传失败: 文件名不能包含\\/:*?"<>|等特殊字符 | process_request')
            logger.error(message)
            return {"result": False, "message": message, "code": 400}

        if not file_path:
            message = _(f"文件上传失败: 文件路径[{file_path}]不符合要求, 请修改后重试 | process_request")
            logger.error(message)
            return {"result": False, "message": message, "code": 400}

        if not source_ip:
            logger.error("[FILE_UPLOAD]invalid source_ip: {}".format(source_ip))
            return {"result": False, "message": "invalid source_ip", "code": 400}

        try:
            file_tag = self.manager.save(name=file_name, content=None, source_ip=source_ip, file_path=file_path)
        except Exception as e:
            message = _(f"文件上传失败: 文件归档失败请重试, 如持续失败可联系管理员处理, {traceback.format_exc()} | process_request")
            logger.error(message)
            return {"result": False, "message": message + f":{e}", "code": 500}

        logger.info("[FILE_UPLOAD] will return: {}".format(file_tag))
        return {"result": True, "tag": file_tag, "md5": file_local_md5, "code": 200}

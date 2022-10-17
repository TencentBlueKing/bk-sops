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
import hashlib

from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("root")

INVALID_CHAR_REGEX = re.compile('[\\/:*?"<>|,]')


def common_process_request(request, manager, *args, **kwargs):
    file_obj = request.FILES["file"]
    project_id = request.META["HTTP_APP_PROJECTID"]
    file_name = file_obj.name
    file_size = file_obj.size

    if not project_id:
        return {"result": False, "message": "invalid project_id: {}".format(project_id), "code": 400}

    # 文件名不能包含中文， 文件大小不能大于 2G
    if file_size > 2048 * 1024 * 1024:
        return {"result": False, "message": _("文件上传失败， 文件大小超过2G"), "code": 400}

    if INVALID_CHAR_REGEX.findall(file_name):
        return {"result": False, "message": _('文件上传失败，文件名不能包含\\/:*?"<>|等特殊字符'), "code": 400}

    shims = "plugins_upload/job_push_local_files/{}".format(project_id)
    kwargs = {
        "project_id": int(project_id),
        "username": kwargs.get("specific_username") or request.user.username,
    }

    # 计算文件md5
    file_local_md5 = hashlib.md5(file_obj.read()).hexdigest()

    try:
        file_tag = manager.save(name=file_name, content=file_obj, shims=shims, **kwargs)
    except Exception as e:
        logger.error("file upload save err: {}".format(traceback.format_exc()))
        return {"result": False, "message": _("文件上传归档失败，请联系管理员") + f":{e}", "code": 500}

    return {"result": True, "tag": file_tag, "md5": file_local_md5, "code": 200}

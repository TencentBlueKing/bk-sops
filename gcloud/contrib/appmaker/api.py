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

import jsonschema
import magic
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET

from gcloud.conf import settings
from gcloud.contrib.analysis.analyse_items import app_maker
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.contrib.appmaker.schema import APP_MAKER_PARAMS_SCHEMA
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.iam_auth import IAMMeta
from gcloud.utils.strings import check_and_rename_params

logger = logging.getLogger("root")


def save(request, project_id):
    """
    @summary: 创建或编辑app maker
    @param:
            id: id  判断是新建还是编辑
            name:　名称
            desc: 简介
            template_id: 模板ID
            template_scheme_id: 执行方案ID
    """

    try:
        params = request.POST.dict()
        jsonschema.validate(params, APP_MAKER_PARAMS_SCHEMA)
    except jsonschema.ValidationError as e:
        logger.error("APP_MAKER_PARAMS_SCHEMA raise error: %s" % e)
        message = _(f"轻应用保存失败: 保存轻应用接口参数校验失败, {e} | appmaker save")
        logger.error(message)
        return JsonResponse({"result": False, "message": message})

    logo_obj = request.FILES.get("logo")
    if logo_obj:
        valid_mime = {"image/png", "image/jpg", "image/jpeg"}
        is_png_or_jpg = logo_obj.content_type in valid_mime
        if not is_png_or_jpg:
            message = _("轻应用保存失败: 非法的图片格式, 请使用不超过100KB的JPG / PNG 图片作为应用LOGO | appmaker save")
            logger.error(message)
            return JsonResponse({"result": False, "message": message})
        file_size = logo_obj.size
        # LOGO大小不能大于 100K
        if file_size > 100 * 1024:
            message = _("轻应用保存失败: 非法的图片大小, 请使用不超过100KB 的 JPG / PNG 图片作为应用LOGO | appmaker save")
            logger.error(message)
            return JsonResponse({"result": False, "message": message})
        logo_content = logo_obj.read()
        real_mime = magic.from_buffer(logo_content, mime=True)
        if real_mime not in valid_mime:
            message = _("轻应用保存失败: 请使用不超过100KB 的 JPG / PNG 图片作为应用LOGO | appmaker save")
            logger.error(message)
            return JsonResponse({"result": False, "message": message})
    else:
        logo_content = None

    params.update({"username": request.user.username, "logo_content": logo_content})
    # 初始化描述
    if not params.get("desc"):
        params.update({"desc": "Standard OPS  Mini-App"})

    if settings.IS_LOCAL:
        params["link_prefix"] = "%s/appmaker/" % request.get_host()
        fake = True
    else:
        params["link_prefix"] = "%sappmaker/" % settings.APP_HOST
        fake = False

    result, data = AppMaker.objects.save_app_maker(project_id, request.user.tenant_id, params, fake)
    if not result:
        return JsonResponse({"result": False, "message": data})

    bk_audit_add_event(
        username=request.user.username,
        action_id=IAMMeta.MINI_APP_EDIT_ACTION if params.get("id") else IAMMeta.FLOW_CREATE_MINI_APP_ACTION,
        resource_id=IAMMeta.MINI_APP_RESOURCE,
        instance=data,
    )

    data = {
        "id": data.id,
        "code": data.code,
        "logo_url": data.logo_url,
    }
    return JsonResponse({"result": True, "data": data})


@require_GET
def get_appmaker_count(request, project_id):
    group_by = request.GET.get("group_by", "category")
    result_dict = check_and_rename_params({}, group_by)
    if not result_dict["success"]:
        return JsonResponse({"result": False, "message": result_dict["content"]})
    filters = {"is_deleted": False, "project_id": project_id}
    success, content = app_maker.dispatch(result_dict["group_by"], filters)
    if not success:
        return JsonResponse({"result": False, "message": content})
    return JsonResponse({"result": True, "data": content})

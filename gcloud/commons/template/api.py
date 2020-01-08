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

import base64
import hashlib
import logging
import traceback

import ujson as json
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from guardian.shortcuts import (
    get_groups_with_perms,
    get_users_with_perms,
)

from gcloud.commons.template.forms import TemplateImportForm
from gcloud.conf import settings
from gcloud.exceptions import FlowExportError
from gcloud.commons.template.constants import PermNm
from gcloud.commons.template.models import (
    CommonTemplate,
    CommonTmplPerm,
)
from gcloud.commons.template.utils import (
    assign_tmpl_perms,
    assign_tmpl_perms_user,
    read_template_data_file,
)
from gcloud.core.decorators import (
    check_user_perm_of_business,
    check_is_superuser,
)
from gcloud.core.roles import ALL_ROLES
from gcloud.core.utils import convert_group_name, time_now_str

logger = logging.getLogger('root')


@require_GET
def form(request):
    template_id = request.GET.get('template_id')
    version = request.GET.get('version')
    try:
        template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)
    except CommonTemplate.DoesNotExist:
        return HttpResponseForbidden()
    ctx = {
        'form': template.get_form(version),
        'outputs': template.get_outputs(version),
        'version': version or template.version
    }
    return JsonResponse(ctx)


@require_POST
@check_is_superuser()
def export_templates(request):
    data = json.loads(request.body)
    template_id_list = data['template_id_list']

    if not isinstance(template_id_list, list):
        return JsonResponse({'result': False, 'message': 'invalid template_id_list'})

    if not template_id_list:
        return JsonResponse({'result': False, 'message': 'template_id_list can not be empty'})

    # wash
    try:
        templates_data = json.loads(json.dumps(
            CommonTemplate.objects.export_templates(template_id_list), sort_keys=True
        ))
    except CommonTemplate.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'Invalid template id list'
        })
    except FlowExportError as e:
        return JsonResponse({
            'result': False,
            'message': e.message
        })

    digest = hashlib.md5(json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).hexdigest()

    file_data = base64.b64encode(json.dumps({
        'template_data': templates_data,
        'digest': digest
    }, sort_keys=True))
    filename = 'bk_sops_%s_%s.dat' % ('common', time_now_str())
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['mimetype'] = 'application/octet-stream'
    response['Content-Type'] = 'application/octet-stream'
    response.write(file_data)
    return response


@require_POST
@check_is_superuser()
def import_templates(request):
    f = request.FILES.get('data_file', None)
    form_data = TemplateImportForm(request.POST)
    if not form_data.is_valid():
        return JsonResponse({
            'result': False,
            'message': form_data.errors
        })
    override = form_data.clean()['override']

    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    templates_data = r['data']['template_data']

    try:
        result = CommonTemplate.objects.import_templates(templates_data, override)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        return JsonResponse({
            'result': False,
            'message': 'invalid flow data or error occur, please contact administrator'
        })

    return JsonResponse(result)


@require_POST
@check_is_superuser()
def check_before_import(request):
    f = request.FILES.get('data_file', None)
    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    check_info = CommonTemplate.objects.import_operation_check(r['data']['template_data'])
    return JsonResponse({
        'result': True,
        'data': check_info
    })


@require_GET
@check_user_perm_of_business('view_business')
def get_perms(request):
    """
    @summary: 暴露给业务的接口，业务人员获取自己业务下的权限
    @param request:
    @return:
    """
    template_id = request.GET.get('template_id')
    biz_cc_id = str(request.GET.get('biz_cc_id'))

    try:
        CommonTemplate.objects.get(pk=template_id, is_deleted=False)
    except CommonTemplate.DoesNotExist:
        return HttpResponseForbidden()
    template_perm, _ = CommonTmplPerm.objects.get_or_create(common_template_id=template_id,
                                                            biz_cc_id=biz_cc_id)
    data = {perm: [] for perm in PermNm.PERM_LIST}
    common_perm_list = ['common_%s' % perm for perm in PermNm.PERM_LIST]
    index = len('common_')
    # 获取有权限的分组列表
    groups = get_groups_with_perms(template_perm, attach_perms=True)
    for group, perm_list in groups.items():
        for perm in perm_list:
            if perm in common_perm_list:
                data[perm[index:]].append({
                    "show_name": group.name.split("\x00")[-1]
                })
    # 获取有权限的人员列表(单独按人员角色授权，而不是按分组授权)
    users = get_users_with_perms(template_perm, attach_perms=True, with_group_users=False)
    for user, perm_list in users.items():
        for perm in perm_list:
            if perm in common_perm_list:
                data[perm[index:]].append({
                    "show_name": user.username
                })
    ctx = {
        'result': True,
        'data': data,
        'message': 'success'
    }
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_business('manage_business')
def save_perms(request):
    """
    @summary: 暴露给业务的接口，业务管理员保存自己业务下的权限
    @param request:
    @return:
    """
    template_id = request.POST.get('template_id')
    biz_cc_id = str(request.POST.get('biz_cc_id'))

    try:
        CommonTemplate.objects.get(pk=template_id, is_deleted=False)
    except CommonTemplate.DoesNotExist:
        return HttpResponseForbidden()
    template_perm, _ = CommonTmplPerm.objects.get_or_create(common_template_id=template_id,
                                                            biz_cc_id=biz_cc_id)
    user_model = get_user_model()
    for perm in PermNm.PERM_LIST:
        group_name_list = []
        user_name_list = []
        for data in json.loads(request.POST.get(perm, '[]')):
            if data in ALL_ROLES:
                group_name = convert_group_name(biz_cc_id, data)
                group_name_list.append(group_name)
            else:
                user_name_list.append(data)
        group_set = Group.objects.filter(name__in=group_name_list)
        assign_tmpl_perms(['common_%s' % perm], group_set, template_perm)
        user_set = user_model.objects.filter(username__in=user_name_list)
        assign_tmpl_perms_user(['common_%s' % perm], user_set, template_perm)
    ctx = {
        'result': True,
        'data': {},
        'message': 'success'
    }
    return JsonResponse(ctx)

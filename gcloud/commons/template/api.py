# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
from auth_backend.plugins.shortcuts import (
    batch_verify_or_raise_auth_failed,
    verify_or_return_insufficient_perms
)

from gcloud.commons.template.forms import TemplateImportForm
from gcloud.conf import settings
from gcloud.exceptions import FlowExportError
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.utils import read_template_data_file
from gcloud.commons.template.permissions import common_template_resource
from gcloud.core.utils import time_now_str

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


@require_GET
def export_templates(request):
    try:
        template_id_list = json.loads(request.GET.get('template_id_list'))
    except Exception:
        return JsonResponse({'result': False, 'message': 'invalid template_id_list'})

    if not isinstance(template_id_list, list):
        return JsonResponse({'result': False, 'message': 'invalid template_id_list'})

    templates = CommonTemplate.objects.filter(id__in=template_id_list, is_deleted=False)
    perms_tuples = [(common_template_resource, [common_template_resource.actions.view.id], t) for t in templates]
    batch_verify_or_raise_auth_failed(principal_type='user',
                                      principal_id=request.user.username,
                                      perms_tuples=perms_tuples)

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

    # check again and authenticate
    check_info = CommonTemplate.objects.import_operation_check(templates_data)
    perms_tuples = []
    if override:
        if check_info['new_template']:
            perms_tuples.append((common_template_resource, [common_template_resource.actions.create.id], None))

        if check_info['override_template']:
            templates_id = [template_info['id'] for template_info in check_info['override_template']]
            templates = CommonTemplate.objects.filter(id__in=templates_id, is_deleted=False)
            for template in templates:
                perms_tuples.append((common_template_resource, [common_template_resource.actions.edit.id], template))
    else:
        perms_tuples.append((common_template_resource, [common_template_resource.actions.create.id], None))

    batch_verify_or_raise_auth_failed(principal_type='user',
                                      principal_id=request.user.username,
                                      perms_tuples=perms_tuples)

    try:
        result = CommonTemplate.objects.import_templates(templates_data, override, request.user.username)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        return JsonResponse({
            'result': False,
            'message': 'invalid flow data or error occur, please contact administrator'
        })

    return JsonResponse(result)


@require_POST
def check_before_import(request):
    f = request.FILES.get('data_file', None)
    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    check_info = CommonTemplate.objects.import_operation_check(r['data']['template_data'])

    perms_tuples = [(common_template_resource, [common_template_resource.actions.create.id], None)]
    if check_info['override_template']:
        templates_id = [template_info['id'] for template_info in check_info['override_template']]
        templates = CommonTemplate.objects.filter(id__in=templates_id, is_deleted=False)
        for template in templates:
            perms_tuples.append((common_template_resource, [common_template_resource.actions.edit.id], template))
    permissions = verify_or_return_insufficient_perms(principal_type='user',
                                                      principal_id=request.user.username,
                                                      perms_tuples=perms_tuples)

    return JsonResponse({
        'result': True,
        'data': check_info,
        'permission': permissions
    })

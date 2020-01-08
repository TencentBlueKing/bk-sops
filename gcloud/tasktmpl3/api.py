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

import hashlib
import base64
import logging
import traceback

import ujson as json
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from guardian.shortcuts import (
    get_groups_with_perms,
    get_users_with_perms,
)

from gcloud.conf import settings
from gcloud.exceptions import FlowExportError
from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.roles import ALL_ROLES
from gcloud.core.utils import convert_group_name, time_now_str, check_and_rename_params
from gcloud.commons.template.constants import PermNm
from gcloud.commons.template.utils import (
    assign_tmpl_perms,
    assign_tmpl_perms_user,
    read_template_data_file
)
from gcloud.commons.template.forms import TemplateImportForm
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger('root')

VAR_ID_MAP = 'var_id_map'


@require_GET
def form(request, biz_cc_id):
    template_id = request.GET.get('template_id')
    version = request.GET.get('version')
    try:
        template = TaskTemplate.objects.get(pk=template_id,
                                            business__cc_id=biz_cc_id,
                                            is_deleted=False)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    ctx = {
        'form': template.get_form(version),
        'outputs': template.get_outputs(version),
        'version': version or template.version
    }
    return JsonResponse(ctx)


@require_POST
def collect(request, biz_cc_id):
    template_id = request.POST.get('template_id')
    template_list = json.loads(request.POST.get('template_list', '[]'))

    if template_id:
        method = request.POST.get('method', 'add')
        try:
            template = TaskTemplate.objects.get(pk=template_id,
                                                business__cc_id=biz_cc_id,
                                                is_deleted=False)
        except TaskTemplate.DoesNotExist:
            return HttpResponseForbidden()
        ctx = template.user_collect(request.user.username, method)
        return JsonResponse(ctx)

    if template_list:
        if len(template_list) > 10:
            return JsonResponse({'result': False, 'message': u"template list must not larger than 10"})
        user_model = get_user_model()
        user = user_model.objects.get(username=request.user.username)
        try:
            template = TaskTemplate.objects.filter(pk__in=template_list,
                                                   business__cc_id=biz_cc_id,
                                                   is_deleted=False)
            collected_template = user.tasktemplate_set.filter(business__cc_id=biz_cc_id)
            user.tasktemplate_set.remove(*collected_template)
            user.tasktemplate_set.add(*template)
        except Exception as e:
            message = u"collect template error: %s" % e
            ctx = {'result': False, 'message': message}
        else:
            ctx = {'result': True, 'data': ''}
        return JsonResponse(ctx)
    else:
        try:
            user_model = get_user_model()
            user = user_model.objects.get(username=request.user.username)
            collected_template = user.tasktemplate_set.filter(business__cc_id=biz_cc_id)
            user.tasktemplate_set.remove(*collected_template)
        except Exception as e:
            message = u"collect template error: %s" % e
            ctx = {'result': False, 'message': message}
        else:
            ctx = {'result': True, 'data': ''}
        return JsonResponse(ctx)


@require_GET
def get_perms(request, biz_cc_id):
    template_id = request.GET.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id,
                                            business__cc_id=biz_cc_id,
                                            is_deleted=False)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    data = {perm: [] for perm in PermNm.PERM_LIST}
    # 获取有权限的分组列表
    groups = get_groups_with_perms(template, attach_perms=True)
    for group, perm_list in groups.items():
        for perm in perm_list:
            if perm in PermNm.PERM_LIST:
                data[perm].append({
                    "show_name": group.name.split("\x00")[-1]
                })
    # 获取有权限的人员列表(单独按人员角色授权，而不是按分组授权)
    users = get_users_with_perms(template, attach_perms=True, with_group_users=False)
    for user, perm_list in users.items():
        for perm in perm_list:
            if perm in PermNm.PERM_LIST:
                data[perm].append({
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
def save_perms(request, biz_cc_id):
    template_id = request.POST.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id,
                                            business__cc_id=biz_cc_id,
                                            is_deleted=False)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
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
        assign_tmpl_perms([perm], group_set, template)
        user_set = user_model.objects.filter(username__in=user_name_list)
        assign_tmpl_perms_user([perm], user_set, template)
    ctx = {
        'result': True,
        'data': {},
        'message': 'success'
    }
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_business('manage_business')
def export_templates(request, biz_cc_id):
    data = json.loads(request.body)
    template_id_list = data['template_id_list']

    if not isinstance(template_id_list, list):
        return JsonResponse({'result': False, 'message': 'invalid template_id_list'})

    if not template_id_list:
        return JsonResponse({'result': False, 'message': 'template_id_list can not be empty'})

    # wash
    try:
        templates_data = json.loads(json.dumps(
            TaskTemplate.objects.export_templates(template_id_list, biz_cc_id), sort_keys=True
        ))
    except TaskTemplate.DoesNotExist:
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
    filename = 'bk_sops_%s_%s.dat' % (biz_cc_id, time_now_str())
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['mimetype'] = 'application/octet-stream'
    response['Content-Type'] = 'application/octet-stream'
    response.write(file_data)
    return response


@require_POST
@check_user_perm_of_business('manage_business')
def import_templates(request, biz_cc_id):
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
        result = TaskTemplate.objects.import_templates(templates_data, override, biz_cc_id)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        return JsonResponse({
            'result': False,
            'message': 'invalid flow data or error occur, please contact administrator'
        })

    return JsonResponse(result)


@require_POST
@check_user_perm_of_business('manage_business')
def check_before_import(request, biz_cc_id):
    f = request.FILES.get('data_file', None)
    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    check_info = TaskTemplate.objects.import_operation_check(r['data']['template_data'], biz_cc_id)
    return JsonResponse({
        'result': True,
        'data': check_info
    })


def job_id_map_convert(origin_id_maps):
    new_id_map = {}
    for id_map in origin_id_maps:
        _map = {'id': int(id_map['new_job_id']),
                VAR_ID_MAP: {}}

        for var_id_map in id_map['global_var_id_mapping']:
            _map[VAR_ID_MAP][int(var_id_map['original_id'])] = int(var_id_map['new_id'])

        new_id_map[int(id_map['original_job_id'])] = _map

    return new_id_map


def replace_job_relate_id_in_templates_data(job_id_map, templates_data):
    for template in templates_data['pipeline_template_data']['template'].values():

        # for each act in template
        for act in filter(lambda act: act['type'] == 'ServiceActivity', template['tree']['activities'].values()):
            act_comp = act['component']
            constants = template['tree']['constants']

            # try to replace job id
            if act_comp['code'] == 'job_execute_task':
                origin_job_id = act_comp['data']['job_task_id']['value']
                id_map = job_id_map.get(origin_job_id, {})

                # replace job id
                act_comp['data']['job_task_id']['value'] = id_map.get('id', origin_job_id)

                # replace global vars id
                if act_comp['data']['job_global_var']['hook']:
                    constant_key = act_comp['data']['job_global_var']['value']
                    for var in constants[constant_key]['value']:
                        if 'id' in var:
                            var['id'] = id_map.get(VAR_ID_MAP, {}).get(var['id'], var['id'])
                else:
                    for var in act_comp['data']['job_global_var']['value']:
                        if 'id' in var:
                            var['id'] = id_map.get(VAR_ID_MAP, {}).get(var['id'], var['id'])


@require_POST
@check_user_perm_of_business('manage_business')
def import_preset_template_and_replace_job_id(request, biz_cc_id):
    f = request.FILES.get('data_file', None)
    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    job_id_map_json = request.POST.get('job_id_map', None)

    if job_id_map_json is None:
        return JsonResponse({
            'result': False,
            'message': 'job_id_map can not be None'
        })

    # replace str to int
    try:
        job_id_map = json.loads(job_id_map_json)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'job_id_map is not a valid json string'
        })

    job_id_map = job_id_map_convert(job_id_map)

    # replace job id
    templates_data = r['data']['template_data']

    # for each template
    replace_job_relate_id_in_templates_data(job_id_map, templates_data)

    try:
        result = TaskTemplate.objects.import_templates(templates_data, False, biz_cc_id)
    except Exception as e:
        logger.error(traceback.format_exc(e))
        return JsonResponse({
            'result': False,
            'message': 'invalid flow data or error occur, please contact administrator'
        })

    return JsonResponse(result)


def replace_all_templates_tree_node_id(request):
    """
    @summary：清理脏数据
    @param request:
    @return:
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    total, success = TaskTemplate.objects.replace_all_template_tree_node_id()
    return JsonResponse({
        'result': True,
        'data': {
            'total': total,
            'success': success
        }
    })


@require_GET
def get_template_count(request, biz_cc_id):
    group_by = request.GET.get('group_by', 'category')
    result_dict = check_and_rename_params('{}', group_by)
    if not result_dict['success']:
        return JsonResponse({'result': False, 'message': result_dict['content']})
    filters = {'is_deleted': False, 'business__cc_id': biz_cc_id}
    success, content = TaskTemplate.objects.extend_classified_count(result_dict['group_by'], filters)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})


@require_GET
def get_collect_template(request, biz_cc_id):
    username = request.user.username
    success, content = TaskTemplate.objects.get_collect_template(biz_cc_id, username)
    if not success:
        return JsonResponse({'result': False, 'message': content})
    return JsonResponse({'result': True, 'data': content})

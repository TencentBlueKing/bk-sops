# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import ujson as json
import hashlib
import base64

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from guardian.shortcuts import (get_groups_with_perms,
                                get_users_with_perms)

from gcloud.core.constant import TASK_CATEGORY, TASK_FLOW_TYPE, NOTIFY_TYPE
from gcloud.core.decorators import check_user_perm_of_business
from gcloud.core.roles import ALL_ROLES
from gcloud.core.utils import convert_group_name
from gcloud.tasktmpl3.utils import (assign_tmpl_perms,
                                    assign_tmpl_perms_user,
                                    get_notify_group_by_biz_core)
from gcloud.tasktmpl3.forms import TemplateImportForm
from gcloud.tasktmpl3.models import (TaskTemplate,
                                     CREATE_TASK_PERM_NAME,
                                     FILL_PARAMS_PERM_NAME,
                                     EXECUTE_TASK_PERM_NAME)
from gcloud.tasktmpl3.exceptions import TaskTemplateExportError


@require_GET
def form(request, biz_cc_id):
    template_id = request.GET.get('template_id')
    version = request.GET.get('version')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    ctx = {
        'form': template.get_form(version),
        'outputs': template.get_outputs(),
        'version': version or template.version
    }
    return JsonResponse(ctx)


@require_POST
def collect(request, biz_cc_id):
    template_id = request.POST.get('template_id')
    template_list = json.loads(request.POST.get('template_list', '[]'))
    if template_list:
        if len(template_list) > 10:
            return JsonResponse({'result': False, 'message': u"template list must not larger than 10"})
        user_model = get_user_model()
        user = user_model.objects.get(username=request.user.username)
        try:
            template = TaskTemplate.objects.filter(pk__in=template_list, business__cc_id=biz_cc_id)
            collected_template = user.tasktemplate_set.filter(business__cc_id=biz_cc_id)
            user.tasktemplate_set.remove(*collected_template)
            user.tasktemplate_set.add(*template)
        except Exception as e:
            message = u"collect template error: %s" % e
            ctx = {'result': False, 'message': message}
        else:
            ctx = {'result': True, 'data': ''}
    else:
        method = request.POST.get('method', 'add')
        try:
            template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
        except TaskTemplate.DoesNotExist:
            return HttpResponseForbidden()
        ctx = template.user_collect(request.user.username, method)
    return JsonResponse(ctx)


@require_GET
def get_perms(request, biz_cc_id):
    template_id = request.GET.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    all_perms = [CREATE_TASK_PERM_NAME, FILL_PARAMS_PERM_NAME, EXECUTE_TASK_PERM_NAME]
    data = {('%s_groups' % perm): [] for perm in all_perms}
    # 获取有权限的分组列表
    groups = get_groups_with_perms(template, attach_perms=True)
    for group, perm_list in groups.items():
        for perm in perm_list:
            data['%s_groups' % perm].append({
                "show_name": group.name.split("\x00")[-1]
            })
    # 获取有权限的人员列表(单独按人员角色授权，而不是按分组授权)
    users = get_users_with_perms(template, attach_perms=True, with_group_users=False)
    for user, perm_list in users.items():
        for perm in perm_list:
            data['%s_groups' % perm].append({
                "show_name": user.username
            })
    ctx = {
        'result': True,
        'data': data
    }
    return JsonResponse(ctx)


@require_POST
@check_user_perm_of_business('manage_business')
def save_perms(request, biz_cc_id):
    template_id = request.POST.get('template_id')
    try:
        template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
    except TaskTemplate.DoesNotExist:
        return HttpResponseForbidden()
    user_model = get_user_model()
    for perm in [CREATE_TASK_PERM_NAME, FILL_PARAMS_PERM_NAME, EXECUTE_TASK_PERM_NAME]:
        group_name_list = []
        user_name_list = []
        for data in json.loads(request.POST.get(perm, '[]')):
            if data in ALL_ROLES:
                group_name = convert_group_name(biz_cc_id, data)
                group_name_list.append(group_name)
            else:
                user_name_list.append(data)
        group_set = Group.objects.filter(name__in=group_name_list)
        assign_tmpl_perms(request, [perm], group_set, template)
        user_set = user_model.objects.filter(username__in=user_name_list)
        assign_tmpl_perms_user(request, [perm], user_set, template)
    ctx = {
        'result': True,
        'data': '',
    }
    return JsonResponse(ctx)


@require_GET
def get_business_basic_info(request, biz_cc_id):
    """
    @summary: 获取业务基本配置信息
    @param request:
    @param biz_cc_id:
    @return:
    """
    # 类型数据来源
    task_categories = []
    for item in TASK_CATEGORY:
        task_categories.append({
            'value': item[0],
            'name': item[1]
        })
    # 模板流程来源
    flow_type_list = []
    for item in TASK_FLOW_TYPE:
        flow_type_list.append({
            'value': item[0],
            'name': item[1]
        })

    # 出错通知人员分组
    notify_group = get_notify_group_by_biz_core(biz_cc_id)

    # 出错通知方式来源
    notify_type_list = []
    for item in NOTIFY_TYPE:
        notify_type_list.append({
            'value': item[0],
            'name': item[1]
        })

    ctx = {
        "task_categories": task_categories,
        "flow_type_list": flow_type_list,
        "notify_group": notify_group,
        "notify_type_list": notify_type_list,
    }
    return JsonResponse(ctx, safe=False)


@require_GET
@check_user_perm_of_business('manage_business')
def export_templates(request, biz_cc_id):
    try:
        template_id_list = json.loads(request.GET.get('template_id_list'))
    except:
        return JsonResponse({'result': False, 'message': 'invalid template_id_list'})

    if not isinstance(template_id_list, list):
        return JsonResponse({'result': False, 'message': 'invalid template_id_list'})

    # wash
    try:
        templates_data = json.loads(json.dumps(TaskTemplate.objects.export_templates(template_id_list, biz_cc_id),
                                               sort_keys=True))
    except TaskTemplate.DoesNotExist:
        return JsonResponse({
            'result': False,
            'message': 'Invalid template id list'
        })
    except TaskTemplateExportError as e:
        return JsonResponse({
            'result': False,
            'message': e.message
        })

    digest = hashlib.md5(json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).hexdigest()

    file_data = base64.b64encode(json.dumps({
        'template_data': templates_data,
        'digest': digest
    }, sort_keys=True))
    filename = 'bk_sops_%s_%s.dat' % (biz_cc_id, timezone.now())
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    response['mimetype'] = 'application/octet-stream'
    response['Content-Type'] = 'application/octet-stream'
    response.write(file_data)
    return response


def read_template_data_file(f):
    if not f:
        return {
            'result': False,
            'message': 'Upload template dat file please.'
        }

    content = f.read()
    try:
        file_data = json.loads(base64.b64decode(content))
    except:
        return {
            'result': False,
            'message': 'File is corrupt'
        }

    # check the validation of file
    templates_data = file_data['template_data']
    digest = hashlib.md5(json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).hexdigest()

    is_data_valid = (digest == file_data['digest'])
    if not is_data_valid:
        return {
            'result': False,
            'message': 'Invalid template data'
        }

    return {
        'result': True,
        'data': file_data
    }


@require_POST
@check_user_perm_of_business('manage_business')
def import_templates(request, biz_cc_id):
    f = request.FILES.get('data_file', None)
    form = TemplateImportForm(request.POST)
    if not form.is_valid():
        return JsonResponse({
            'result': False,
            'message': form.errors
        })
    override = form.clean()['override']

    r = read_template_data_file(f)
    if not r['result']:
        return JsonResponse(r)

    templates_data = r['data']['template_data']

    result = TaskTemplate.objects.import_templates(templates_data, override, biz_cc_id)

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


def replace_all_templates_tree_node_id(request):
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

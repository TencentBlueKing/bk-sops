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

import re
import logging
import traceback

from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url

from auth_backend.constants import AUTH_FORBIDDEN_CODE
from auth_backend.exceptions import AuthFailedException

from pipeline_plugins.base.utils.inject import (
    supplier_account_inject,
    supplier_id_inject
)
from pipeline_plugins.cmdb_ip_picker.query import (
    cmdb_search_host,
    cmdb_search_topo_tree,
    cmdb_get_mainline_object_topo
)

from files.factory import ManagerFactory

from gcloud.conf import settings
from gcloud.utils.handlers import handle_api_error
from gcloud.exceptions import APIError
from gcloud.core.models import Project, EnvironmentVariables
from gcloud.core.utils import get_user_business_list

logger = logging.getLogger('root')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

JOB_VAR_TYPE_STR = 1
JOB_VAR_TYPE_IP = 2
JOB_VAR_TYPE_INDEX_ARRAY = 3
JOB_VAR_TYPE_ARRAY = 4
INVALID_CHAR_REGEX = re.compile('[\u4e00-\u9fa5\\/:*?"<>|,]')


@supplier_account_inject
def cc_search_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {
        'bk_obj_id': obj_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_object_attribute', kwargs, cc_result)
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    obj_property = []
    for item in cc_result['data']:
        if item['editable']:
            obj_property.append({
                'value': item['bk_property_id'],
                'text': item['bk_property_name']
            })

    return JsonResponse({'result': True, 'data': obj_property})


@supplier_account_inject
def cc_search_create_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    client = get_client_by_user(request.user.username)
    kwargs = {
        'bk_obj_id': obj_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_object_attribute', kwargs, cc_result)
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    obj_property = []
    for item in cc_result['data']:
        if item['editable']:
            prop_dict = {
                'tag_code': item['bk_property_id'],
                'type': "input",
                'attrs': {
                    'name': item['bk_property_name'],
                    'editable': 'true',
                },
            }
            if item['bk_property_id'] in ['bk_set_name']:
                prop_dict["attrs"]["validation"] = [
                    {
                        "type": "required"
                    }
                ]
            obj_property.append(prop_dict)

    return JsonResponse({'result': True, 'data': obj_property})


def cc_format_topo_data(data, obj_id, category):
    """
    @summary: 格式化拓扑数据
    @param obj_id set or module
    @param category prev(获取obj_id上一层级拓扑) or normal (获取obj_id层级拓扑) or picker(ip选择器拓扑)
    @return 拓扑数据列表
    """
    tree_data = []
    for item in data:
        tree_item = {
            'id': "%s_%s" % (item['bk_obj_id'], item['bk_inst_id']),
            'label': item['bk_inst_name']
        }
        if category == "prev":
            if item['bk_obj_id'] != obj_id:
                tree_data.append(tree_item)
                if 'child' in item:
                    tree_item['children'] = cc_format_topo_data(item['child'], obj_id, category)
        else:
            if item['bk_obj_id'] == obj_id:
                tree_data.append(tree_item)
            elif 'child' in item:
                tree_item['children'] = cc_format_topo_data(item['child'], obj_id, category)
                tree_data.append(tree_item)

    return tree_data


@supplier_account_inject
def cc_search_topo(request, obj_id, category, biz_cc_id, supplier_account):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {
        'bk_biz_id': biz_cc_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_biz_inst_topo', kwargs, cc_result)
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    if category in ["normal", "prev"]:
        cc_topo = cc_format_topo_data(cc_result['data'], obj_id, category)
    else:
        cc_topo = []

    return JsonResponse({'result': True, 'data': cc_topo})


def job_get_script_list(request, biz_cc_id):
    """
    查询业务脚本列表
    :param request:
    :param biz_cc_id:
    :return:
    """
    # 查询脚本列表
    client = get_client_by_user(request.user.username)
    source_type = request.GET.get('type')
    script_type = request.GET.get('script_type')

    if source_type == 'public':
        kwargs = None
        script_result = client.job.get_public_script_list()
        api_name = 'job.get_public_script_list'
    else:
        kwargs = {
            'bk_biz_id': biz_cc_id,
            'is_public': False,
            'script_type': script_type or 0,
        }
        script_result = client.job.get_script_list(kwargs)
        api_name = 'job.get_script_list'

    if not script_result['result']:
        message = handle_api_error('job', api_name, kwargs, script_result)
        logger.error(message)
        result = {
            'result': False,
            'message': message
        }
        return JsonResponse(result)

    script_dict = {}
    for script in script_result['data']['data']:
        script_dict.setdefault(script['name'], []).append(script['id'])

    version_data = []
    for name, version in list(script_dict.items()):
        version_data.append({
            "text": name,
            "value": max(version)
        })

    return JsonResponse({'result': True, 'data': version_data})


def job_get_own_db_account_list(request, biz_cc_id):
    """
    查询用户有权限的DB帐号列表
    :param biz_cc_id:
    :param request:
    :return:
    """
    client = get_client_by_user(request.user.username)
    kwargs = {
        'bk_biz_id': biz_cc_id
    }
    job_result = client.job.get_own_db_account_list(kwargs)

    if not job_result['result']:
        message = handle_api_error('job', 'get_own_db_account_list', kwargs, job_result)
        logger.error(message)
        result = {
            'result': False,
            'message': message
        }
        return JsonResponse(result)

    data = [{'text': item['db_alias'], 'value': item['db_account_id']} for item in job_result['data']]

    return JsonResponse({'result': True, 'data': data})


def job_get_job_tasks_by_biz(request, biz_cc_id):
    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_list({'bk_biz_id': biz_cc_id})
    if not job_result['result']:
        message = _("查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (
            biz_cc_id, job_result['message'])

        if job_result.get('code', 0) == AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise AuthFailedException(permissions=job_result.get('permission', []))

        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)
    task_list = []
    for task in job_result['data']:
        task_list.append({
            'value': task['bk_job_id'],
            'text': task['name'],
        })
    return JsonResponse({'result': True, 'data': task_list})


def job_get_job_task_detail(request, biz_cc_id, task_id):
    client = get_client_by_user(request.user.username)
    job_result = client.job.get_job_detail({'bk_biz_id': biz_cc_id,
                                            'bk_job_id': task_id})
    if not job_result['result']:

        message = _("查询作业平台(JOB)的作业模板详情[app_id=%s]接口job.get_task_detail返回失败: %s") % (
            biz_cc_id, job_result['message'])

        if job_result.get('code', 0) == AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise AuthFailedException(permissions=job_result.get('permission', []))

        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    job_step_type_name = {
        1: _("脚本"),
        2: _("文件"),
        4: "SQL"
    }
    task_detail = job_result['data']
    global_var = []
    steps = []
    for var in task_detail.get('global_vars', []):
        # 1-字符串, 2-IP, 3-索引数组, 4-关联数组
        if var['type'] in [JOB_VAR_TYPE_STR, JOB_VAR_TYPE_INDEX_ARRAY, JOB_VAR_TYPE_ARRAY]:
            value = var.get('value', '')
        else:
            value = ','.join(
                ['{plat_id}:{ip}'.format(plat_id=ip_item['bk_cloud_id'], ip=ip_item['ip'])
                 for ip_item in var.get('ip_list', [])]
            )
        global_var.append({
            'id': var['id'],
            # 全局变量类型：1:云参, 2:上下文参数，3:IP
            'category': var.get('category', 1),
            'name': var['name'],
            'type': var['type'],
            'value': value,
            'description': var['description']
        })
    for info in task_detail.get('steps', []):
        # 1-执行脚本, 2-传文件, 4-传SQL
        steps.append({
            'stepId': info['step_id'],
            'name': info['name'],
            'scriptParams': info.get('script_param', ''),
            'account': info.get('account', ''),
            'ipList': '',
            'type': info['type'],
            'type_name': job_step_type_name.get(info['type'], info['type'])
        })
    return JsonResponse({'result': True, 'data': {'global_var': global_var, 'steps': steps}})


@supplier_account_inject
def cc_search_topo_tree(request, project_id, supplier_account):
    project = Project.objects.get(id=project_id)
    if project.from_cmdb:
        return cmdb_search_topo_tree(request, project.bk_biz_id, supplier_account)
    else:
        ctx = {
            'result': False,
            'message': 'cannot search topo tree by project which is not from CMDB',
            'data': {},
            'code': -1
        }
        return JsonResponse(ctx)


@supplier_account_inject
@supplier_id_inject
def cc_search_host(request, project_id, supplier_account, supplier_id):
    project = Project.objects.get(id=project_id)
    if project.from_cmdb:
        return cmdb_search_host(request, project.bk_biz_id, supplier_account, supplier_id)
    else:
        ctx = {
            'result': False,
            'message': 'cannot search host by project which is not from CMDB',
            'data': {},
            'code': -1
        }
        return JsonResponse(ctx)


@supplier_account_inject
def cc_get_mainline_object_topo(request, project_id, supplier_account):
    project = Project.objects.get(id=project_id)
    if project.from_cmdb:
        return cmdb_get_mainline_object_topo(request, project.bk_biz_id, supplier_account)
    else:
        ctx = {
            'result': False,
            'message': 'cannot search mainline object topo by project which is not from CMDB',
            'data': {},
            'code': -1
        }
        return JsonResponse(ctx)


def cc_get_business(request):
    try:
        business = get_user_business_list(username=request.user.username)
    except APIError as e:
        message = 'an error occurred when fetch user business: %s' % traceback.format_exc()

        if e.result and e.result.get('code', 0) == AUTH_FORBIDDEN_CODE:
            logger.warning(message)
            raise AuthFailedException(permissions=e.result.get('permission', []))

        logger.error(message)
        return JsonResponse({
            'result': False,
            'message': 'fetch business list failed, please contact administrator'
        })

    data = []
    for biz in business:
        # archive data filter
        if biz.get('bk_data_status') != 'disabled':
            data.append({
                'text': biz['bk_biz_name'],
                'value': int(biz['bk_biz_id'])
            })

    return JsonResponse({
        'result': True,
        'data': data
    })


def file_upload(request, project_id):
    """
    @summary: 本地文件上传
    @param request:
    @param project_id:
    @return:
    """

    file_manager_type = EnvironmentVariables.objects.get_var('BKAPP_FILE_MANAGER_TYPE')
    if not file_manager_type:
        return JsonResponse({
            'result': False,
            'message': _("File Manager 未配置，请联系管理员进行配置")
        })

    try:
        file_manager = ManagerFactory.get_manager(manager_type=file_manager_type)
    except Exception as e:
        logger.error('can not get file manager for type: {}\n err: {}'.format(
            file_manager_type,
            traceback.format_exc()
        ))
        return JsonResponse({'result': False, 'message': str(e)})

    file_obj = request.FILES['file']
    file_name = file_obj.name
    file_size = file_obj.size
    # 文件名不能包含中文， 文件大小不能大于 2G
    if file_size > 2048 * 1024 * 1024:
        message = _("文件上传失败， 文件大小超过2G")
        response = JsonResponse({'result': False, 'message': message})
        response.status_code = 400
        return response

    if INVALID_CHAR_REGEX.findall(file_name):
        message = _("文件上传失败，文件名不能包含中文和\\/:*?\"<>|等特殊字符")
        response = JsonResponse({'result': False, 'message': message})
        response.status_code = 400
        return response

    shims = 'plugins_upload/job_push_local_files/{}'.format(project_id)

    try:
        file_tag = file_manager.save(name=file_name, content=file_obj, shims=shims)
    except Exception:
        logger.error('file upload save err: {}'.format(traceback.format_exc()))
        return JsonResponse({'result': False, 'message': _("文件上传归档失败，请联系管理员")})

    return JsonResponse({
        'result': True,
        'tag': file_tag
    })


urlpatterns = [
    url(r'^cc_search_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$', cc_search_object_attribute),
    url(r'^cc_search_create_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$', cc_search_create_object_attribute),
    url(r'^cc_search_topo/(?P<obj_id>\w+)/(?P<category>\w+)/(?P<biz_cc_id>\d+)/$', cc_search_topo),
    url(r'^job_get_script_list/(?P<biz_cc_id>\d+)/$', job_get_script_list),
    url(r'^job_get_own_db_account_list/(?P<biz_cc_id>\d+)/$', job_get_own_db_account_list),
    url(r'^file_upload/(?P<project_id>\d+)/$', file_upload),
    url(r'^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$', job_get_job_tasks_by_biz),
    url(r'^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$', job_get_job_task_detail),

    # IP selector
    url(r'^cc_search_topo_tree/(?P<project_id>\d+)/$', cc_search_topo_tree),
    url(r'^cc_search_host/(?P<project_id>\d+)/$', cc_search_host),
    url(r'^cc_get_mainline_object_topo/(?P<project_id>\d+)/$', cc_get_mainline_object_topo),

    url(r'^cc_get_business_list/$', cc_get_business),
]

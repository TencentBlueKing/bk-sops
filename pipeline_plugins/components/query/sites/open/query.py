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
import os
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf.urls import url

from pipeline_plugins.components.utils import (
    cc_get_inner_ip_by_module_id,
    supplier_account_inject,
    handle_api_error,
    supplier_id_inject
)
from pipeline_plugins.cmdb_ip_picker.query import (
    cmdb_search_host,
    cmdb_search_topo_tree,
    cmdb_get_mainline_object_topo
)

logger = logging.getLogger('root')
get_client_by_request = settings.ESB_GET_CLIENT_BY_REQUEST

JOB_VAR_TYPE_STR = 1
JOB_VAR_TYPE_IP = 2
JOB_VAR_TYPE_INDEX_ARRAY = 3
JOB_VAR_TYPE_ARRAY = 4
CHINESE_REGEX = re.compile(u'[\u4e00-\u9fa5\\/:*?"<>|,]')


@supplier_account_inject
def cc_search_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'bk_obj_id': obj_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_object_attribute', kwargs, cc_result['message'])
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
    client = get_client_by_request(request)
    kwargs = {
        'bk_obj_id': obj_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_object_attribute', kwargs, cc_result['message'])
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
                if item.get('child'):
                    tree_item['children'] = cc_format_topo_data(item['child'], obj_id, category)
        else:
            if item['bk_obj_id'] == obj_id:
                tree_data.append(tree_item)
            elif item.get('child'):
                tree_item['children'] = cc_format_topo_data(item['child'], obj_id, category)
                tree_data.append(tree_item)

    return tree_data


def cc_format_module_hosts(username, biz_cc_id, module_id_list, supplier_account):
    module_host_list = cc_get_inner_ip_by_module_id(username, biz_cc_id, module_id_list, supplier_account)
    module_host_dict = {}
    for item in module_host_list:
        for module in item['module']:
            if module_host_dict.get('module_%s' % module['bk_module_id']):
                module_host_dict['module_%s' % module['bk_module_id']].append({
                    'id': '%s_%s' % (module['bk_module_id'], item['host']['bk_host_innerip']),
                    'label': item['host']['bk_host_innerip']
                })
            else:
                module_host_dict['module_%s' % module['bk_module_id']] = [{
                    'id': '%s_%s' % (module['bk_module_id'], item['host']['bk_host_innerip']),
                    'label': item['host']['bk_host_innerip']
                }]
    return module_host_dict


@supplier_account_inject
def cc_search_topo(request, obj_id, category, biz_cc_id, supplier_account):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'bk_biz_id': biz_cc_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_biz_inst_topo', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    if category in ["normal", "prev", "picker"]:
        cc_topo = cc_format_topo_data(cc_result['data'], obj_id, category)
    else:
        cc_topo = []

    return JsonResponse({'result': True, 'data': cc_topo})


@supplier_account_inject
def cc_get_host_by_module_id(request, biz_cc_id, supplier_account):
    """
    查询模块对应主机
    :param request:
    :param biz_cc_id:
    :return:
    """
    select_module_id = request.GET.getlist('query', [])
    # 查询module对应的主机
    module_hosts = cc_format_module_hosts(request.user.username, biz_cc_id, map(lambda x: int(x), select_module_id),
                                          supplier_account)

    for del_id in (set(module_hosts.keys()) - set(map(lambda x: 'module_%s' % x, select_module_id))):
        del module_hosts[del_id]

    return JsonResponse({'result': True if module_hosts else False, 'data': module_hosts})


def job_get_script_list(request, biz_cc_id):
    """
    查询业务脚本列表
    :param request:
    :param biz_cc_id:
    :return:
    """
    # 查询脚本列表
    client = get_client_by_request(request)
    script_type = request.GET.get('type')
    kwargs = {
        'bk_biz_id': biz_cc_id,
        'is_public': True if script_type == 'public' else False
    }
    script_result = client.job.get_script_list(kwargs)

    if not script_result['result']:
        message = handle_api_error('cc', 'job.get_script_list', kwargs, script_result['message'])
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
    for name, version in script_dict.items():
        version_data.append({
            "text": name,
            "value": max(version)
        })

    return JsonResponse({'result': True, 'data': version_data})


def file_upload(request, biz_cc_id):
    """
    @summary: 本地文件上传
    @param request:
    @param biz_cc_id:
    @return:
    """
    try:
        file_obj = request.FILES['file']
        file_name = file_obj.name
        file_size = file_obj.size
        # 文件名不能包含中文， 文件大小不能大于500M
        if file_size > 500 * 1024 * 1024:
            message = _(u"文件上传失败， 文件大小超过500M")
            response = JsonResponse({'result': False, 'message': message})
            response.status_code = 400
            return response

        if CHINESE_REGEX.findall(file_name):
            message = _(u"文件上传失败，文件名不能包含中文和\\/:*?\"<>|等特殊字符")
            response = JsonResponse({'result': False, 'message': message})
            response.status_code = 400
            return response

        file_content = file_obj.read()

        if not isinstance(biz_cc_id, int):
            return JsonResponse({
                'result': False,
                'message': _(u"非法业务 ID")
            })

        now_str = timezone.datetime.now().strftime('%Y%m%d%H%M%S')
        bk_path = os.path.join(settings.BASE_DIR,
                               'USERRES',
                               'bkupload',
                               str(biz_cc_id),
                               now_str)
        logger.info(u"/components/query/file_upload file path: %s" % bk_path)

        if not os.path.exists(bk_path):
            os.makedirs(bk_path)

        with open(r'%s%s' % (bk_path, file_name), 'w') as file_obj:
            file_obj.write(file_content)

        result = {
            'result': True,
            'time_str': now_str,
            'name': file_name,
            'size': file_size,
        }
        return JsonResponse(result)

    except Exception as e:
        logger.error(u"/components/query/file_upload exception, error=%s" % e)
        message = _(u"文件上传失败，路径不合法或者程序异常")
        response = JsonResponse({'result': False, 'message': message})
        response.status_code = 400
        return response


def job_get_job_tasks_by_biz(request, biz_cc_id):
    client = get_client_by_request(request)
    job_result = client.job.get_job_list({'bk_biz_id': biz_cc_id})
    if not job_result['result']:
        message = _(u"查询作业平台(JOB)的作业模板[app_id=%s]接口job.get_task返回失败: %s") % (
            biz_cc_id, job_result['message'])
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
    client = get_client_by_request(request)
    job_result = client.job.get_job_detail({'bk_biz_id': biz_cc_id,
                                            'bk_job_id': task_id})
    if not job_result['result']:
        message = _(u"查询作业平台(JOB)的作业模板详情[app_id=%s]接口job.get_task_detail返回失败: %s") % (
            biz_cc_id, job_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    job_step_type_name = {
        1: _(u"脚本"),
        2: _(u"文件"),
        4: u"SQL"
    }
    task_detail = job_result['data']
    global_var = []
    steps = []
    for var in task_detail.get('global_vars', []):
        # 1-字符串, 2-IP, 3-索引数组, 4-关联数组
        if var['type'] in [JOB_VAR_TYPE_STR, JOB_VAR_TYPE_IP, JOB_VAR_TYPE_ARRAY]:
            value = var.get('value', '')
        else:
            value = ['{plat_id}:{ip}'.format(plat_id=ip_item['bk_cloud_id'], ip=ip_item['ip'])
                     for ip_item in var.get('ip_list', [])]
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
def cc_search_topo_tree(request, biz_cc_id, supplier_account):
    return cmdb_search_topo_tree(request, biz_cc_id, supplier_account)


@supplier_account_inject
@supplier_id_inject
def cc_search_host(request, biz_cc_id, supplier_account, supplier_id):
    return cmdb_search_host(request, biz_cc_id, supplier_account, supplier_id)


@supplier_account_inject
def cc_get_mainline_object_topo(request, biz_cc_id, supplier_account):
    return cmdb_get_mainline_object_topo(request, biz_cc_id, supplier_account)


urlpatterns = [
    url(r'^cc_search_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$', cc_search_object_attribute),
    url(r'^cc_search_create_object_attribute/(?P<obj_id>\w+)/(?P<biz_cc_id>\d+)/$', cc_search_create_object_attribute),
    url(r'^cc_search_topo/(?P<obj_id>\w+)/(?P<category>\w+)/(?P<biz_cc_id>\d+)/$', cc_search_topo),
    url(r'^cc_get_host_by_module_id/(?P<biz_cc_id>\d+)/$', cc_get_host_by_module_id),
    url(r'^job_get_script_list/(?P<biz_cc_id>\d+)/$', job_get_script_list),
    url(r'^file_upload/(?P<biz_cc_id>\d+)/$', file_upload),
    url(r'^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$', job_get_job_tasks_by_biz),
    url(r'^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$', job_get_job_task_detail),
    url(r'^cc_search_topo_tree/(?P<biz_cc_id>\d+)/$', cc_search_topo_tree),
    url(r'^cc_search_host/(?P<biz_cc_id>\d+)/$', cc_search_host),
    url(r'^cc_get_mainline_object_topo/(?P<biz_cc_id>\d+)/$', cc_get_mainline_object_topo),
]

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

import requests
import json

from django.http import HttpResponse
from django.http.response import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _

from pipeline.utils.uniqid import node_uniqid, line_uniqid

from gcloud.conf import settings
from gcloud.core.models import Business
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.sites.utils import draw_pipeline_automatic

ENV_TYPE = {
    1: _(u"测试"),
    2: _(u"体验"),
    3: _(u"正式")
}

SERVICE_TYPE = {
    0: _(u"关闭"),
    1: _(u"开放")
}

# v2 atom id : v3 component code
component_code_v2_to_v3 = {
    'requests': 'bk_http_request',
    'job_execute_task': 'job_execute_task',
    'job_fast_execute_script': 'job_fast_execute_script',
    'job_fast_push_file': 'job_fast_push_file',
    'timer_countdown': 'sleep_timer',
    'pause': 'pause_node',
    'cchost_replace': 'cc_replace_fault_machine',
    'ccupdate_host_module': 'cc_transfer_host_module',
    'ccupdate_custom_property': 'cc_update_host',
    'ccdelete_set': 'cc_batch_delete_set',
    'ccreset_set': 'cc_empty_set_hosts',
    'ccbiz_status': 'cc_update_set_service_status',
    'ccmodify_set_property': 'cc_update_set',
    'ccupdate_module_property': 'cc_update_module',
    'ccadd_set': 'cc_create_set',
    'timer_eta': 'sleep_timer',
}

var_type_v2_to_v3 = {
    'simple_input_tag': 'input',
    'simple_textarea_tag': 'textarea',
    'simple_datetime_tag': 'datetime',
    'kendo_numeric_integer': 'int',
    'kendo_numeric_float': 'input',
    'var_ip_picker': 'ip'
}

source_tag_from_v2 = {
    'requests': {
        'requests_url': 'bk_http_request.bk_http_request_url',
        'requests_body': 'bk_http_request.bk_http_request_body',
        'requests_method': 'bk_http_request.bk_http_request_method',
    },
    'job_execute_task': {
        'job_execute_tasks': 'job_execute_task.job_task_id',
        'job_global_var': 'job_execute_task.job_global_var',
    },
    'job_fast_execute_script': {
        'job_script_type': 'job_fast_execute_script.job_script_type',
        'job_script_content': 'job_fast_execute_script.job_content',
        'job_script_param': 'job_fast_execute_script.job_script_param',
        'job_script_timeout': 'job_fast_execute_script.job_script_timeout',
        'job_ip_list': 'job_fast_execute_script.job_ip_list',
        'job_script_account': 'job_fast_execute_script.job_account',
    },
    'job_fast_push_file': {
        'job_source_files': 'job_fast_push_file.job_source_files',
        'job_target_ip': 'job_fast_push_file.job_ip_list',
        'job_account': 'job_fast_push_file.job_account',
        'job_target_path': 'job_fast_push_file.job_target_path',
    },
    'timer_countdown': {
        'timer_datetime_input': 'sleep_timer.bk_timing',
    },
    'cchost_replace': {
        'cc_replace_host_info': 'cc_replace_fault_machine.cc_host_replace_detail',
        'fault_ip': 'cc_replace_fault_machine.cc_fault_ip',
    },
    'ccupdate_host_module': {
        'cc_host_ip': 'cc_transfer_host_module.cc_host_ip',
        'cc_module': 'cc_transfer_host_module.cc_module_select',
        'cc_plat_id': '',
    },
    'ccupdate_custom_property': {
        'cc_custom_property': 'cc_update_host.cc_host_property',
        'cc_property_val': 'cc_update_host.cc_host_prop_value',
        'cc_inner_ip': 'cc_update_host.cc_host_ip',
    },
    'ccdelete_set': {
        'cc_set_names': 'cc_batch_delete_set.cc_set_select',
    },
    'ccreset_set': {
        'cc_set_name': 'cc_empty_set_hosts.cc_set_select',
    },
    'ccbiz_status': {
        'cc_set_names': 'cc_update_set_service_status.cc_set_select',
        'cc_service_type': 'cc_update_set_service_status.cc_set_status',
    },
    'ccmodify_set_property': {
        'cc_old_set_name': '',
        'cc_new_set_name': '',
        'cc_env_type': '',
        'cc_service_type': '',
        'cc_capacity': '',
        'cc_des': '',
    },
    'ccupdate_module_property': {
        'cc_module_list': '',
    },
    'ccadd_set': {
        'cc_set_name': '',
        'cc_env_type': '',
        'cc_service_type': '',
        'cc_capacity': '',
        'cc_des': '',
    },
    'timer_eta': {
        'timer_time_input': 'sleep_timer.bk_timing',
    },
}


def import_v2(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    result = import_template_data()
    if not result['result']:
        message = u"获取 v2 模板信息失败，请重试"
    else:
        message = u"恭喜您成功迁移{success}个模板,失败{failure}个{message}，请返回标准运维任务流程页面并刷新查看数据".format(
            success=result['data']['success'],
            failure=result['data']['failure']['num'],
            message=result['data']['failure']['message'].format(
                tag_code=",".join(result['data']['failure']['tag_code'])
            ) if result['data']['failure']['num'] else ""
        )
    return HttpResponse(message)


def import_template_data():
    data_url = getattr(settings, 'V2_DATA_URL', None)
    if not data_url:
        data_url = '%s/o/gcloud/template/export/' % settings.BK_PAAS_INNER_HOST

    response = requests.post(
        data_url,
        data=json.dumps({"key": "___export___v2___template___"}),
        headers={"Content-Type": "application/json"},
        verify=False
    )
    resp_data = json.loads(response.content)

    if not response.ok or not resp_data['result']:
        return {'result': False, 'data': 0}

    data_list = resp_data['data']
    template_list = []
    failure_dict = {
        'num': 0,
        'tag_code': [],
        'message': u"tag_code:{tag_code}不支持迁移"
    }
    for tmpl in data_list[::-1]:
        default_user = 'admin'
        default_company = 'admin'
        business, __ = Business.objects.get_or_create(
            cc_id=tmpl['biz_cc_id'],
            cc_name=tmpl['biz_cc_name'],
            defaults={
                'cc_owner': default_user,
                'cc_company': default_company,
            }
        )

        stage_data = json.loads(tmpl['stage_data'])
        param_data = json.loads(tmpl['parameters'])

        # 判断是否存在不支持迁移的tag_code，如果存在则跳过此模板
        import_flag = True
        for stage in stage_data:
            for step in stage['steps']:
                if step['tag_code'] not in component_code_v2_to_v3:
                    import_flag = False
                    failure_dict['num'] += 1
                    failure_dict['tag_code'].append(step['tag_code'])
                    break
            if not import_flag:
                break
        if not import_flag:
            continue

        pipeline_tree = convert_stage_and_params_from_v2_to_v3(stage_data, param_data, tmpl['biz_cc_id'])

        pipeline_template_kwargs = {
            'name': tmpl['name'],
            'creator': tmpl['creator'],
            'pipeline_tree': pipeline_tree,
            'description': '',
        }

        pipeline_template = TaskTemplate.objects.create_pipeline_template(**pipeline_template_kwargs)
        pipeline_template.editor = tmpl['editor']
        pipeline_template.create_time = tmpl['create_time']
        pipeline_template.edit_time = tmpl['edit_time']
        pipeline_template.save()

        default_notify_receiver = json.loads(tmpl['default_notify_receiver'])
        notify_receivers = {
            "receiver_group": default_notify_receiver['notify_group'],
            "more_receiver": default_notify_receiver['other_notify_receiver']
        }

        template_list.append(
            TaskTemplate(
                business=business,
                category=tmpl['category'],
                pipeline_template=pipeline_template,
                notify_type=tmpl['default_notify_type'],
                notify_receivers=json.dumps(notify_receivers),
                time_out=tmpl['default_time_out_notify_time']
            )
        )

    TaskTemplate.objects.bulk_create(template_list)
    return {'result': True, 'data': {"success": len(template_list), "failure": failure_dict}}


def convert_stage_and_params_from_v2_to_v3(stage_data, params, biz_cc_id):
    step_2_tag = get_step_tagcode(stage_data)
    constants = convert_params_from_v2_to_v3(params, step_2_tag)

    pipeline_tree = {
        'start_event': {
            'id': node_uniqid(),
            'incoming': '',
            'outgoing': '',
            'type': 'EmptyStartEvent',
            'name': '',
        },
        'end_event': {
            'id': node_uniqid(),
            'incoming': '',
            'outgoing': '',
            'type': 'EmptyEndEvent',
            'name': '',
        },
        'activities': {},
        'gateways': {},
        'flows': {},
        'constants': constants,
        'outputs': []
    }
    last_node = pipeline_tree['start_event']

    for stage in stage_data:
        is_parallel = stage.get('is_parallel')
        step_data = stage['steps']
        stage_name = stage['stage_name']

        if is_parallel:
            flow = {
                'id': line_uniqid(),
                'source': last_node['id'],
                'target': '',
                'is_default': False,
            }
            last_node['outgoing'] = flow['id']

            parallel_gateway = {
                'id': node_uniqid(),
                'incoming': flow['id'],
                'outgoing': [],
                'type': 'ParallelGateway',
                'name': '',
            }
            flow['target'] = parallel_gateway['id']
            converge_gateway = {
                'id': node_uniqid(),
                'incoming': [],
                'outgoing': '',
                'type': 'ConvergeGateway',
                'name': '',
            }

            pipeline_tree['gateways'].update({
                parallel_gateway['id']: parallel_gateway,
                converge_gateway['id']: converge_gateway,
            })
            pipeline_tree['flows'].update({
                flow['id']: flow
            })

            last_node = parallel_gateway

        for step in step_data:
            activity = convert_atom_from_v2_step_to_v3_act(step, constants, biz_cc_id, stage_name)
            flow = {
                'id': line_uniqid(),
                'source': last_node['id'],
                'target': activity['id'],
                'is_default': False,
            }
            activity['incoming'] = flow['id']

            if is_parallel:
                parallel_gateway['outgoing'].append(flow['id'])

                flow2 = {
                    'id': line_uniqid(),
                    'source': activity['id'],
                    'target': converge_gateway['id'],
                    'is_default': False,
                }
                converge_gateway['incoming'].append(flow2['id'])
                activity['outgoing'] = flow2['id']

                pipeline_tree['flows'].update({
                    flow['id']: flow,
                    flow2['id']: flow2,
                })
            else:
                last_node['outgoing'] = flow['id']
                last_node = activity

                pipeline_tree['flows'].update({
                    flow['id']: flow
                })

            pipeline_tree['activities'].update({
                activity['id']: activity
            })

        if is_parallel:
            last_node = converge_gateway

    flow = {
        'id': line_uniqid(),
        'source': last_node['id'],
        'target': pipeline_tree['end_event']['id'],
        'is_default': False,
    }
    pipeline_tree['flows'].update({
        flow['id']: flow
    })
    last_node['outgoing'] = flow['id']
    pipeline_tree['end_event']['incoming'] = flow['id']

    return draw_pipeline_automatic(pipeline_tree)


def get_step_tagcode(stage_data):
    step_2_tag = {}
    for stage in stage_data:
        for step in stage['steps']:
            step_2_tag[step['step_id']] = step['tag_code']
    return step_2_tag


def convert_params_from_v2_to_v3(params, step_2_tag):
    constants = {}
    for index, param in enumerate(params):
        key = param['key']
        source_tag = ''
        custom_type = ''
        source_type = ''
        source_info = {}
        value = ''
        hook = False

        if param['source'] == 'from_steps':
            v2_tag_code = param['tag_data']['tag_code']
            value = param['tag_data']['data'][v2_tag_code]['value']
            first_origin_step_id = param['origin'][0]['step_id']
            source_tag = source_tag_from_v2[step_2_tag[first_origin_step_id]][v2_tag_code]
            source_type = 'component_inputs'

        elif param['source'] == 'manual':
            v2_tag_code = param['tag_data']['tag_code']
            custom_type = var_type_v2_to_v3[v2_tag_code]
            if v2_tag_code == 'var_ip_picker':
                source_tag = 'var_ip_picker.ip_picker'
                var_ip_method = param['tag_data']['data']['var_ip_method']['value']['value']
                if var_ip_method == 'custom':
                    value = {
                        "var_ip_method": "custom",
                        "var_ip_custom_value": param['tag_data']['data']['var_ip_custom_value']['value'],
                        "var_ip_tree": []
                    }
                elif var_ip_method == "select":
                    value = {
                        "var_ip_method": "tree",
                        "var_ip_custom_value": "",
                        "var_ip_tree": [_value['value'] for _value in
                                        param['tag_data']['data']['var_ip_select_module']['value']],
                    }
                else:
                    value = {
                        "var_ip_method": "tree",
                        "var_ip_tree": [],
                        "var_ip_custom_value": "",
                    }
            else:
                value = param['tag_data']['data'][v2_tag_code]['value']
            source_type = 'custom'

        constants.update({
            key: {
                'name': param['name'],
                'key': key,
                'value': value,
                'index': index,
                'is_meta': False,
                'custom_type': custom_type,
                'source_tag': source_tag,
                'source_info': source_info,
                'show_type': param['show_type'],
                'source_type': source_type,
                'validation': param['validation'],
                'hook': hook,
                'desc': param['desc']
            }
        })
    return constants


# v2 tag_code : v3 tag code
tag_v2_to_v3 = {
    'requests': {
        'requests_url': 'bk_http_request_url',
        'requests_method': 'bk_http_request_method',
        'requests_body': 'bk_http_request_body'
    },
    'job_execute_task': {
        'job_execute_tasks': 'job_task_id',
        'job_global_var': 'job_global_var',
        'job_execute_task_steps': ''
    },
    'job_fast_execute_script': {
        'job_script_type': 'job_script_type',
        'job_script_content': 'job_content',
        'job_script_param': 'job_script_param',
        'job_script_timeout': 'job_script_timeout',
        'job_ip_list': 'job_ip_list',
        'job_script_account': 'job_account',
    },
    'job_fast_push_file': {
        'job_source_files': 'job_source_files',
        'job_target_ip': 'job_ip_list',
        'job_account': 'job_account',
        'job_target_path': 'job_target_path',
    },
    'timer_countdown': {
        'timer_datetime_input': 'bk_timing'
    },
    'cchost_replace': {
        'cc_replace_host_info': 'cc_host_replace_detail',
    },
    'ccupdate_host_module': {
        'cc_host_ip': 'cc_host_ip',
        'cc_module': 'cc_module_select',
        'cc_plat_id': '',
    },
    'ccupdate_custom_property': {
        'cc_custom_property': 'cc_host_property',
        'cc_property_val': 'cc_host_prop_value',
        'cc_inner_ip': 'cc_host_ip',
        'cc_plat_id': '',
    },
    'ccdelete_set': {
        'cc_set_names': 'cc_set_select',
    },
    'ccreset_set': {
        'cc_set_name': 'cc_set_select',
    },
    'ccmodify_set_property': {
        'cc_old_set_name': '',
        'cc_new_set_name': '',
        'cc_env_type': '',
        'cc_service_type': '',
        'cc_capacity': '',
        'cc_des': '',
    },
    'ccupdate_module_property': {
        'cc_module_list': '',
    },
    'ccadd_set': {
        'cc_set_name': '',
        'cc_env_type': '',
        'cc_service_type': '',
        'cc_capacity': '',
        'cc_des': '',
    },
    'ccbiz_status': {
        'cc_set_names': 'cc_set_select',
        'cc_service_type': 'cc_set_status',
    },
    'timer_eta': {
        'timer_time_input': 'bk_timing',
    },
}


def convert_atom_from_v2_step_to_v3_act(step, constants, biz_cc_id, stage_name):
    act_id = node_uniqid()
    v3_act = {
        'id': act_id,
        'incoming': '',
        'outgoing': '',
        'name': step['step_name'],
        'error_ignorable': bool(step['is_ignore']),
        'optional': bool(step['is_adjust']),
        'type': 'ServiceActivity',
        'loop': 1,
        'stage_name': stage_name,
        'component': {
            'code': '',
            'data': {}
        }
    }

    tag_code = step['tag_code']
    component_code = component_code_v2_to_v3.get(tag_code)
    if not component_code:
        raise Exception("unknown tag code: %s" % tag_code)

    data = step['tag_data']['data']
    tag_data = {}
    mount_constant(act_id, tag_code, data, constants)

    if tag_code in ['requests', 'job_fast_execute_script', 'job_fast_push_file', 'timer_countdown', 'cchost_replace',
                    'job_execute_task', 'ccupdate_custom_property', 'ccupdate_host_module', 'ccdelete_set',
                    'ccreset_set',
                    'timer_eta']:
        for key, val in data.items():
            hook = True if val['hook'] == 'on' else False

            tmp_val = val['value']

            # select数据适配
            if key in ['job_execute_tasks', 'cc_custom_property']:
                tmp_val = val['value']['value']

            # datatable数据适配
            elif key == "job_source_files":
                tmp_val = []
                for item in val['value']:
                    tmp_val.append({
                        'ip': item.get('ip'),
                        'account': item.get('account'),
                        'files': item.get('file')
                    })
            elif key == "cc_replace_host_info":
                tmp_val = []
                for item in val['value']:
                    tmp_val.append({
                        'cc_fault_ip': item.get('fault_ip'),
                        'cc_new_ip': item.get('replace_ip')
                    })

            # tree类型数据适配
            elif key == "cc_module":
                tmp_val = [int(val['value']['value'])]

            # tree类型需要置为空的key
            elif key in ['cc_set_names', 'cc_set_name']:
                tmp_val = []

            if hook:
                tag_val = val['constant']
                constants[tag_val]['value'] = tmp_val

                # 需要过滤掉的数据
                if key in ["cc_plat_id"]:
                    del constants['${%s}' % key]
                    continue
            else:
                tag_val = tmp_val

            tag_data[tag_v2_to_v3[tag_code][key]] = {
                'hook': hook,
                'value': tag_val
            }

    # 缺失数据填充
    if tag_code == 'ccupdate_host_module':
        tag_data['cc_is_increment'] = {
            'hook': False,
            'value': ""
        }
    if tag_code == 'ccmodify_set_property':
        tag_data.update({
            'cc_set_select': {
                'hook': False,
                'value': []
            },
            'cc_set_property': {
                'hook': False,
                'value': ""
            },
            'cc_set_prop_value': {
                'hook': False,
                'value': ""
            }
        })
    if tag_code == 'ccupdate_module_property':
        tag_data.update({
            'cc_module_select': {
                'hook': False,
                'value': []
            },
            'cc_module_property': {
                'hook': False,
                'value': ""
            },
            'cc_module_prop_value': {
                'hook': False,
                'value': ""
            }
        })
    if tag_code == 'ccadd_set':
        cc_set_info = {
            'hook': False,
            'value': [{}, ]
        }
        for key, val in data.items():
            if key == 'cc_set_name':
                cc_set_info['value'][0]['bk_set_name'] = val['value']
            elif key == 'cc_env_type':
                cc_set_info['value'][0]['bk_set_env'] = str(ENV_TYPE[val['value']])
            elif key == 'cc_service_type':
                cc_set_info['value'][0]['bk_service_status'] = str(SERVICE_TYPE[val['value']])
            elif key == 'cc_capacity':
                cc_set_info['value'][0]['bk_capacity'] = val['value']
            else:
                cc_set_info['value'][0]['bk_set_desc'] = val['value']
        tag_data.update({
            'cc_set_parent_select': {
                'hook': False,
                'value': [biz_cc_id]
            },
            'cc_set_info': cc_set_info
        })
    if tag_code == "ccbiz_status":
        for key, val in data.items():
            hook = True if val['hook'] == 'on' else False
            tmp_val = val['value']

            # tree类型需要置为空的key
            if key == 'cc_set_names':
                tmp_val = []
            elif key == 'cc_service_type':
                tmp_val = str(val['value'])
                if val['value'] == '0':
                    tmp_val = "2"

            if hook:
                tag_val = val['constant']
                constants[tag_val]['value'] = tmp_val
            else:
                tag_val = tmp_val

            tag_data[tag_v2_to_v3[tag_code][key]] = {
                'hook': hook,
                'value': tag_val
            }

    # TODO another tag

    v3_act['component']['code'] = component_code
    v3_act['component']['data'] = tag_data
    return v3_act


def mount_constant(act_id, tag_code, data, constants):
    for key, val in data.items():
        if val['hook'] == 'on':
            constants[val['constant']]['source_info'].update({
                act_id: [tag_v2_to_v3[tag_code][key]]})

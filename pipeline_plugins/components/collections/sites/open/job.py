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

# 作业平台任务状态参照表
TASK_RESULT = [
    (0, u'状态未知'),
    (1, u'未执行'),
    (2, u'正在执行'),
    (3, u'执行成功'),
    (4, u'执行失败'),
    (5, u'跳过'),
    (6, u'忽略错误'),
    (7, u'等待用户'),
    (8, u'手动结束'),
    (9, u'状态异常'),
    (10, u'步骤强制终止中'),
    (11, u'步骤强制终止成功'),
    (12, u'步骤强制终止失败'),
    (-1, u'接口调用失败'),
]
"""

import base64
import logging

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from gcloud.conf.default_settings import ESB_GET_CLIENT_BY_USER as get_client_by_user

from pipeline.conf import settings
from pipeline_plugins.components.utils import cc_get_ips_info_by_str, get_job_instance_url, get_node_callback_url
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

# 作业状态码: 1.未执行; 2.正在执行; 3.执行成功; 4.执行失败; 5.跳过; 6.忽略错误; 7.等待用户; 8.手动结束;
# 9.状态异常; 10.步骤强制终止中; 11.步骤强制终止成功; 12.步骤强制终止失败
JOB_SUCCESS = {3}
JOB_VAR_TYPE_IP = 2

__group_name__ = _(u"作业平台(JOB)")
__group_icon__ = '%scomponents/icons/job.png' % settings.STATIC_URL

LOGGER = logging.getLogger('celery')


class JobService(Service):
    __need_schedule__ = True

    # interval = StaticIntervalGenerator(5)

    def execute(self, data, parent_data):
        pass

    def schedule(self, data, parent_data, callback_data=None):

        job_instance_id = callback_data.get('job_instance_id', None)
        status = callback_data.get('status', None)
        client = data.outputs.client
        # step_instances = callback_data.get('step_instances', None)

        if not job_instance_id or not status:
            data.outputs.ex_data = "invalid callback_data, job_instance_id: %s, status: %s" % (job_instance_id, status)
            self.finish_schedule()
            return False

        if status in JOB_SUCCESS:

            # 全局变量重载
            global_var_result = client.job.get_job_instance_global_var_value({
                "bk_biz_id": parent_data.get_one_of_inputs('biz_cc_id'),
                "job_instance_id": job_instance_id
            })

            if not global_var_result['result']:
                data.set_outputs('ex_data', global_var_result['message'])
                self.finish_schedule()
                return False

            global_var_list = global_var_result['data'].get('job_instance_var_values', [])
            if global_var_list:
                for global_var in global_var_list[-1]['step_instance_var_values']:
                    if global_var['category'] != JOB_VAR_TYPE_IP:
                        data.set_outputs(global_var['name'], global_var['value'])

            self.finish_schedule()
            return True
        else:
            data.set_outputs('ex_data', {
                'exception_msg': _(
                    u"任务执行失败，<a href='%s' target='_blank'>前往作业平台(JOB)查看详情</a>"
                ) % data.outputs.job_inst_url,
                'task_inst_id': job_instance_id,
                'show_ip_log': True
            })
            self.finish_schedule()
            return False

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'JOB任务ID'), key='job_inst_id', type='int'),
            self.OutputItem(name=_(u'JOB任务链接'), key='job_inst_url', type='str')
        ]


class JobExecuteTaskService(JobService):
    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        original_global_var = data.get_one_of_inputs('job_global_var')
        global_vars = []
        for _value in original_global_var:
            # 1-字符串，2-IP
            if _value['type'] == 2:
                var_ip = cc_get_ips_info_by_str(
                    username=executor,
                    biz_cc_id=biz_cc_id,
                    ip_str=_value['value'],
                    use_cache=False)
                ip_list = [{'ip': _ip['InnerIP'], 'bk_cloud_id': _ip['Source']} for _ip in var_ip['ip_result']]
                global_vars.append({
                    'name': _value['name'],
                    'ip_list': ip_list,
                })
            else:
                global_vars.append({
                    'name': _value['name'],
                    'value': str(_value['value']).strip(),
                })

        job_kwargs = {
            'bk_biz_id': biz_cc_id,
            'bk_job_id': data.get_one_of_inputs('job_task_id'),
            'global_vars': global_vars,
            'bk_callback_url': get_node_callback_url(self.id)
        }

        job_result = client.job.execute_job(job_kwargs)
        LOGGER.info('job_result: {result}, job_kwargs: {kwargs}'.format(result=job_result, kwargs=job_kwargs))
        if job_result['result']:
            job_instance_id = job_result['data']['job_instance_id']
            data.outputs.job_inst_url = get_job_instance_url(parent_data.inputs.biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result['data']['job_instance_name']
            data.outputs.client = client
            return True
        else:
            data.outputs.ex_data = job_result['message']
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobExecuteTaskService, self).schedule(data, parent_data, callback_data)

    def outputs_format(self):
        return super(JobExecuteTaskService, self).outputs_format()


class JobExecuteTaskComponent(Component):
    name = _(u'执行作业')
    code = 'job_execute_task'
    bound_service = JobExecuteTaskService
    form = '%scomponents/atoms/sites/%s/job/job_execute_task.js' % (settings.STATIC_URL, settings.RUN_VER)


class JobFastPushFileService(JobService):
    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        original_source_files = data.get_one_of_inputs('job_source_files', [])
        file_source = []
        for item in original_source_files:
            ip_info = cc_get_ips_info_by_str(
                username=executor,
                biz_cc_id=biz_cc_id,
                ip_str=item['ip'],
                use_cache=False)
            file_source.append({
                'files': str(item['files']).strip().split("\n"),
                'ip_list': [{
                    'ip': _ip['InnerIP'],
                    'bk_cloud_id': _ip['Source']
                } for _ip in ip_info['ip_result']],
                'account': str(item['account']).strip(),
            })

        original_ip_list = data.get_one_of_inputs('job_ip_list')
        ip_info = cc_get_ips_info_by_str(executor, biz_cc_id, original_ip_list)
        ip_list = [{'ip': _ip['InnerIP'], 'bk_cloud_id': _ip['Source']}
                   for _ip in ip_info['ip_result']]

        job_kwargs = {
            'bk_biz_id': biz_cc_id,
            'file_source': file_source,
            'ip_list': ip_list,
            'account': data.get_one_of_inputs('job_account'),
            'file_target_path': data.get_one_of_inputs('job_target_path'),
            'bk_callback_url': get_node_callback_url(self.id)
        }

        job_result = client.job.fast_push_file(job_kwargs)
        LOGGER.info('job_result: {result}, job_kwargs: {kwargs}'.format(result=job_result, kwargs=job_kwargs))
        if job_result['result']:
            job_instance_id = job_result['data']['job_instance_id']
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result['data']['job_instance_name']
            data.outputs.job_inst_url = get_job_instance_url(parent_data.inputs.biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            data.outputs.ex_data = job_result['message']
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobFastPushFileService, self).schedule(data, parent_data, callback_data)

    def outputs_format(self):
        return super(JobFastPushFileService, self).outputs_format()


class JobFastPushFileComponent(Component):
    name = _(u'快速分发文件')
    code = 'job_fast_push_file'
    bound_service = JobFastPushFileService
    form = '%scomponents/atoms/job/job_fast_push_file.js' % settings.STATIC_URL


class JobFastExecuteScriptService(JobService):
    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        original_ip_list = data.get_one_of_inputs('job_ip_list')
        ip_info = cc_get_ips_info_by_str(
            username=executor,
            biz_cc_id=biz_cc_id,
            ip_str=original_ip_list,
            use_cache=False)
        ip_list = [{'ip': _ip['InnerIP'], 'bk_cloud_id': _ip['Source']}
                   for _ip in ip_info['ip_result']]

        job_kwargs = {
            'bk_biz_id': biz_cc_id,
            'script_timeout': data.get_one_of_inputs('job_script_timeout'),
            'account': data.get_one_of_inputs('job_account'),
            'ip_list': ip_list,
            'bk_callback_url': get_node_callback_url(self.id)
        }

        script_param = data.get_one_of_inputs('job_script_param')
        if script_param:
            job_kwargs.update({
                'script_param': base64.b64encode(script_param.encode('utf-8'))
            })

        script_source = data.get_one_of_inputs('job_script_source')
        if script_source in ["general", "public"]:
            job_kwargs.update({
                "script_id": data.get_one_of_inputs('job_script_list_%s' % script_source)
            })
        else:
            job_kwargs.update({
                'script_type': data.get_one_of_inputs('job_script_type'),
                'script_content': base64.b64encode(data.get_one_of_inputs('job_content').encode('utf-8')),
            })

        job_result = client.job.fast_execute_script(job_kwargs)
        LOGGER.info('job_result: {result}, job_kwargs: {kwargs}'.format(result=job_result, kwargs=job_kwargs))
        if job_result['result']:
            job_instance_id = job_result['data']['job_instance_id']
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result['data']['job_instance_name']
            data.outputs.job_inst_url = get_job_instance_url(parent_data.inputs.biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            data.outputs.ex_data = '%s, invalid ip: %s' % (job_result['message'], ','.join(ip_info['invalid_ip']))
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobFastExecuteScriptService, self).schedule(data, parent_data, callback_data)

    def outputs_format(self):
        return super(JobFastExecuteScriptService, self).outputs_format()


class JobFastExecuteScriptComponent(Component):
    name = _(u'快速执行脚本')
    code = 'job_fast_execute_script'
    bound_service = JobFastExecuteScriptService
    form = '%scomponents/atoms/job/job_fast_execute_script.js' % settings.STATIC_URL

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
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

from django.utils.translation import ugettext_lazy as _

from blueapps.utils.esbclient import get_client_by_user

from pipeline.conf import settings
from pipeline.components.utils import cc_get_ips_info_by_str
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component

JOB_SUCCESS = [3, 11]
JOB_APP_CODE = 'bk_job'
__group_name__ = _(u"作业平台(JOB)")
__group_icon__ = '%scomponents/icons/job.png' % settings.STATIC_URL


class JobService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def execute(self, data, parent_data):
        pass

    def schedule(self, data, parent_data, callback_data=None):
        task_inst_id = data.get_one_of_outputs('job_inst_id')
        client = data.get_one_of_outputs('client')

        job_inst_url = '%s?taskInstanceList&appId=%s#taskInstanceId=%s' % (
            settings.BK_JOB_HOST,
            parent_data.get_one_of_inputs('biz_cc_id'),
            task_inst_id,
        )
        data.set_outputs('job_inst_url', job_inst_url)

        job_kwargs = {
            'task_instance_id': task_inst_id,
        }
        job_result = client.job.get_task_result(job_kwargs)
        if not job_result['result']:
            data.set_outputs('ex_data', job_result['message'])
            self.finish_schedule()
            return False
        # 任务执行结束
        job_data = job_result['data']
        if job_data['isFinished']:
            # 执行成功
            if job_data['taskInstance'].get('status', 0) in JOB_SUCCESS:
                data.set_outputs('data', job_data)
                self.finish_schedule()
                return True
            # 执行失败
            else:
                data.set_outputs('ex_data', _(u"任务执行失败，<a href='%s' target='_blank'>"
                                              u"前往作业平台(JOB)查看详情</a>") % job_inst_url,
                                 )
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
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))

        original_global_var = data.get_one_of_inputs('job_global_var')
        global_var = []
        for _value in original_global_var:
            # 1-字符串，2-IP
            if _value['type'] == 2:
                var_ip = cc_get_ips_info_by_str(
                    executor,
                    biz_cc_id,
                    _value['value'])
                ip_list = ['%s:%s' % (_ip['Source'], _ip['InnerIP'])
                           for _ip in var_ip['ip_result']]
                global_var.append({
                    'id': _value['id'],
                    'name': _value['name'],
                    'ipList': ','.join(ip_list),
                })
            else:
                global_var.append({
                    'id': _value['id'],
                    'name': _value['name'],
                    'value': _value['value'].strip(),
                })

        job_kwargs = {
            'app_id': biz_cc_id,
            'task_id': data.get_one_of_inputs('job_task_id'),
            'global_var': global_var,
        }

        job_result = client.job.execute_task_ext(job_kwargs)
        if job_result['result']:
            data.set_outputs('job_inst_id', job_result['data']['taskInstanceId'])
            data.set_outputs('job_inst_name', job_result['data']['taskInstanceName'])
            data.set_outputs('client', client)
            return True
        else:
            data.set_outputs('ex_data', job_result['message'])
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
        if parent_data.get_one_of_inputs('language'):
            setattr(self, 'language', parent_data.get_one_of_inputs('language'))

        original_source_files = data.get_one_of_inputs('job_source_files', [])
        file_source = []
        for item in original_source_files:
            ip_info = cc_get_ips_info_by_str(executor, biz_cc_id, item['ip'])
            file_source.append({
                'file': item['files'].strip(),
                'ip_list': [{
                    'ip': _ip['InnerIP'],
                    'source': _ip['Source']
                } for _ip in ip_info['ip_result']],
                'account': item['account'].strip(),
            })

        original_ip_list = data.get_one_of_inputs('job_ip_list')
        ip_info = cc_get_ips_info_by_str(executor, biz_cc_id, original_ip_list)
        ip_list = [{'ip': _ip['InnerIP'], 'source': _ip['Source']}
                   for _ip in ip_info['ip_result']]

        job_kwargs = {
            'app_id': biz_cc_id,
            'file_source': file_source,
            'ip_list': ip_list,
            'account': data.get_one_of_inputs('job_account'),
            'file_target_path': data.get_one_of_inputs('job_target_path'),
        }

        job_result = client.job.fast_push_file(job_kwargs)
        if job_result['result']:
            data.set_outputs('job_inst_id', job_result['data']['taskInstanceId'])
            data.set_outputs('job_inst_name', job_result['data']['taskInstanceName'])
            data.set_outputs('client', client)
            return True
        else:
            data.set_outputs('ex_data', job_result['message'])
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

        original_ip_list = data.get_one_of_inputs('job_ip_list')
        ip_info = cc_get_ips_info_by_str(executor, biz_cc_id, original_ip_list)
        ip_list = [{'ip': _ip['InnerIP'], 'source': _ip['Source']}
                   for _ip in ip_info['ip_result']]

        job_kwargs = {
            'app_id': biz_cc_id,
            'type': data.get_one_of_inputs('job_script_type'),
            'content': base64.b64encode(
                data.get_one_of_inputs('job_content').encode('utf-8')),
            'script_param': data.get_one_of_inputs('job_script_param'),
            'script_timeout': data.get_one_of_inputs('job_script_timeout'),
            'account': data.get_one_of_inputs('job_account'),
            'ip_list': ip_list,
        }
        job_result = client.job.fast_execute_script(job_kwargs)
        if job_result['result']:
            data.set_outputs('job_inst_id', job_result['data']['taskInstanceId'])
            data.set_outputs('job_inst_name', job_result['data']['taskInstanceName'])
            data.set_outputs('client', client)
            return True
        else:
            data.set_outputs('ex_data', job_result['message'])
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

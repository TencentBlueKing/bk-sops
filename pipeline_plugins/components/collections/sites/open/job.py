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
    (0, '状态未知'),
    (1, '未执行'),
    (2, '正在执行'),
    (3, '执行成功'),
    (4, '执行失败'),
    (5, '跳过'),
    (6, '忽略错误'),
    (7, '等待用户'),
    (8, '手动结束'),
    (9, '状态异常'),
    (10, '步骤强制终止中'),
    (11, '步骤强制终止成功'),
    (12, '步骤强制终止失败'),
    (-1, '接口调用失败'),
]
"""

import base64
import logging
import traceback
from functools import partial

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema, IntItemSchema, ArrayItemSchema, ObjectItemSchema
from pipeline.component_framework.component import Component

from pipeline_plugins.components.utils import (
    cc_get_ips_info_by_str,
    get_job_instance_url,
    get_node_callback_url,
    handle_api_error,
    loose_strip
)

from files.factory import ManagerFactory

from gcloud.conf import settings
from gcloud.core.models import EnvironmentVariables

# 作业状态码: 1.未执行; 2.正在执行; 3.执行成功; 4.执行失败; 5.跳过; 6.忽略错误; 7.等待用户; 8.手动结束;
# 9.状态异常; 10.步骤强制终止中; 11.步骤强制终止成功; 12.步骤强制终止失败
JOB_SUCCESS = {3}
JOB_VAR_TYPE_IP = 2

__group_name__ = _("作业平台(JOB)")

LOGGER = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

job_handle_api_error = partial(handle_api_error, __group_name__)


class JobService(Service):
    __need_schedule__ = True

    reload_outputs = True

    def execute(self, data, parent_data):
        pass

    def schedule(self, data, parent_data, callback_data=None):

        try:
            job_instance_id = callback_data.get('job_instance_id', None)
            status = callback_data.get('status', None)
        except Exception as e:
            err_msg = 'invalid callback_data: {}, err: {}'
            self.logger.error(err_msg.format(callback_data, traceback.format_exc()))
            data.outputs.ex_data = err_msg.format(callback_data, e)
            return False

        if not job_instance_id or not status:
            data.outputs.ex_data = "invalid callback_data, job_instance_id: %s, status: %s" % (job_instance_id, status)
            self.finish_schedule()
            return False

        if status in JOB_SUCCESS:

            if self.reload_outputs:

                client = data.outputs.client

                # 全局变量重载
                get_var_kwargs = {
                    "bk_biz_id": data.get_one_of_inputs('biz_cc_id', parent_data.inputs.biz_cc_id),
                    "job_instance_id": job_instance_id
                }
                global_var_result = client.job.get_job_instance_global_var_value(get_var_kwargs)

                if not global_var_result['result']:
                    message = job_handle_api_error('job.get_job_instance_global_var_value',
                                                   get_var_kwargs,
                                                   global_var_result)
                    self.logger.error(message)
                    data.outputs.ex_data = message
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
                    "任务执行失败，<a href='%s' target='_blank'>前往作业平台(JOB)查看详情</a>"
                ) % data.outputs.job_inst_url,
                'task_inst_id': job_instance_id,
                'show_ip_log': True
            })
            self.finish_schedule()
            return False

    def outputs_format(self):
        return [
            self.OutputItem(name=_('JOB任务ID'),
                            key='job_inst_id',
                            type='int',
                            schema=IntItemSchema(description=_('提交的任务在 JOB 平台的实例 ID'))),
            self.OutputItem(name=_('JOB任务链接'),
                            key='job_inst_url',
                            type='string',
                            schema=StringItemSchema(description=_('提交的任务在 JOB 平台的 URL')))]


class JobExecuteTaskService(JobService):

    def inputs_format(self):
        return [self.InputItem(name=_('业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(name=_('作业模板 ID'),
                               key='job_task_id',
                               type='string',
                               schema=StringItemSchema(description=_('需要执行的 JOB 作业模板 ID'))),
                self.InputItem(name=_('全局变量'),
                               key='job_global_var',
                               type='array',
                               schema=ArrayItemSchema(
                                   description=_('作业模板执行所需的全局变量列表'),
                                   item_schema=ObjectItemSchema(
                                       description=_('全局变量'),
                                       property_schemas={
                                           'type': IntItemSchema(description=_('变量类型，字符串(1) IP(2)')),
                                           'name': StringItemSchema(description=_('变量名')),
                                           'value': StringItemSchema(description=_('变量值'))})))]

    def outputs_format(self):
        return super(JobExecuteTaskService, self).outputs_format()

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        biz_cc_id = data.get_one_of_inputs('biz_cc_id', parent_data.inputs.biz_cc_id)
        original_global_var = data.get_one_of_inputs('job_global_var')
        global_vars = []
        for _value in original_global_var:
            # 1-字符串，2-IP
            if _value['type'] == 2:
                val = loose_strip(_value['value'])
                var_ip = cc_get_ips_info_by_str(
                    username=executor,
                    biz_cc_id=biz_cc_id,
                    ip_str=val,
                    use_cache=False)
                ip_list = [{'ip': _ip['InnerIP'], 'bk_cloud_id': _ip['Source']} for _ip in var_ip['ip_result']]
                if val and not ip_list:
                    data.outputs.ex_data = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法")
                    return False
                if ip_list:
                    global_vars.append({
                        'name': _value['name'],
                        'ip_list': ip_list,
                    })
            else:
                global_vars.append({
                    'name': _value['name'],
                    'value': val,
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
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.job_inst_id = job_instance_id
            data.outputs.job_inst_name = job_result['data']['job_instance_name']
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error('job.execute_job', job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobExecuteTaskService, self).schedule(data, parent_data, callback_data)


class JobExecuteTaskComponent(Component):
    name = _('执行作业')
    code = 'job_execute_task'
    bound_service = JobExecuteTaskService
    form = '%scomponents/atoms/job/job_execute_task.js' % settings.STATIC_URL


class JobFastPushFileService(JobService):

    def inputs_format(self):
        return [self.InputItem(name=_('源文件'),
                               key='job_source_files',
                               type='array',
                               schema=ArrayItemSchema(
                                   description=_('待分发文件列表'),
                                   item_schema=ObjectItemSchema(
                                       description=_('待分发文件信息'),
                                       property_schemas={
                                           'ip': StringItemSchema(description=_('机器 IP')),
                                           'files': StringItemSchema(description=_('文件路径')),
                                           'account': StringItemSchema(description=_('执行账户'))}))),
                self.InputItem(name=_('目标 IP'),
                               key='job_ip_list',
                               type='string',
                               schema=StringItemSchema(description=_('文件分发目标机器 IP，多个以 "," 分隔'))),
                self.InputItem(name=_('目标账户'),
                               key='job_account',
                               type='string',
                               schema=StringItemSchema(description=_('文件分发目标机器账户'))),
                self.InputItem(name=_('目标路径'),
                               key='job_target_path',
                               type='string',
                               schema=StringItemSchema(description=_('文件分发目标路径')))]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        biz_cc_id = data.get_one_of_inputs('biz_cc_id', parent_data.inputs.biz_cc_id)
        original_source_files = data.get_one_of_inputs('job_source_files', [])
        file_source = []
        for item in original_source_files:
            ip_info = cc_get_ips_info_by_str(
                username=executor,
                biz_cc_id=biz_cc_id,
                ip_str=item['ip'],
                use_cache=False)
            file_source.append({
                'files': [_file.strip() for _file in item['files'].split('\n') if _file.strip()],
                'ip_list': [{
                    'ip': _ip['InnerIP'],
                    'bk_cloud_id': _ip['Source']
                } for _ip in ip_info['ip_result']],
                'account': loose_strip(item['account']),
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
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error('job.fast_push_file', job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobFastPushFileService, self).schedule(data, parent_data, callback_data)

    def outputs_format(self):
        return super(JobFastPushFileService, self).outputs_format()


class JobFastPushFileComponent(Component):
    name = _('快速分发文件')
    code = 'job_fast_push_file'
    bound_service = JobFastPushFileService
    form = '%scomponents/atoms/sites/%s/job/job_fast_push_file.js' % (settings.STATIC_URL, settings.RUN_VER)


class JobFastExecuteScriptService(JobService):

    def inputs_format(self):
        return [self.InputItem(name=_('业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(name=_('脚本来源'),
                               key='job_script_source',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待执行的脚本来源，手动(manual)，业务脚本(general)，公共脚本(public)'),
                                   enum=['manual', 'general', 'public'])),
                self.InputItem(name=_('脚本类型'),
                               key='job_script_type',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待执行的脚本类型：shell(1) bat(2) perl(3) python(4) powershell(5)'
                                                 '，仅在脚本来源为手动时生效'),
                                   enum=['1', '2', '3', '4', '5'])),
                self.InputItem(name=_('脚本内容'),
                               key='job_content',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待执行的脚本内容，仅在脚本来源为手动时生效'))),
                self.InputItem(name=_('公共脚本'),
                               key='job_script_list_public',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待执行的公共脚本 ID，仅在脚本来源为公共脚本时生效'))),
                self.InputItem(name=_('业务脚本'),
                               key='job_script_list_general',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待执行的业务脚本 ID，仅在脚本来源为业务脚本时生效'))),
                self.InputItem(name=_('脚本执行参数'),
                               key='job_script_param',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('脚本执行参数'))),
                self.InputItem(name=_('目标 IP'),
                               key='job_ip_list',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('执行脚本的目标机器 IP，多个以 "," 分隔'))),
                self.InputItem(name=_('目标账户'),
                               key='job_account',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('执行脚本的目标机器账户'))),
                ]

    def outputs_format(self):
        return super(JobFastExecuteScriptService, self).outputs_format()

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        biz_cc_id = data.get_one_of_inputs('biz_cc_id', parent_data.inputs.biz_cc_id)
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
            data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
            data.outputs.client = client
            return True
        else:
            message = job_handle_api_error('job.fast_execute_script', job_kwargs, job_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

    def schedule(self, data, parent_data, callback_data=None):
        return super(JobFastExecuteScriptService, self).schedule(data, parent_data, callback_data)


class JobFastExecuteScriptComponent(Component):
    name = _('快速执行脚本')
    code = 'job_fast_execute_script'
    bound_service = JobFastExecuteScriptService
    form = '%scomponents/atoms/job/job_fast_execute_script.js' % settings.STATIC_URL


class JobCronTaskService(Service):

    def inputs_format(self):
        return [self.InputItem(name=_('业务 ID'),
                               key='biz_cc_id',
                               type='string',
                               schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID'))),
                self.InputItem(name=_('定时作业名称'),
                               key='job_cron_name',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待创建的定时作业名称'))),
                self.InputItem(name=_('定时规则'),
                               key='job_cron_expression',
                               type='string',
                               schema=StringItemSchema(
                                   description=_('待创建的定时作业定时规则'))),
                self.InputItem(name=_('定时作业状态'),
                               key='job_cron_status',
                               type='string',
                               schema=IntItemSchema(
                                   description=_('待创建的定时作业状态，暂停(1) 启动(2)'),
                                   enum=[1, 2]))]

    def outputs_format(self):
        return [
            self.OutputItem(name=_('定时作业ID'),
                            key='cron_id',
                            type='int',
                            schema=IntItemSchema(description=_('成功创建的定时作业 ID'))),
            self.OutputItem(name=_('定时作业状态'),
                            key='status',
                            type='string',
                            schema=StringItemSchema(description=_('成功创建的定时作业状态')))]

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        job_cron_job_id = data.get_one_of_inputs('job_cron_job_id')
        job_cron_name = data.get_one_of_inputs('job_cron_name')
        job_cron_expression = data.get_one_of_inputs('job_cron_expression')
        job_kwargs = {
            "bk_biz_id": biz_cc_id,
            "bk_job_id": job_cron_job_id,
            "cron_name": job_cron_name,
            "cron_expression": job_cron_expression,
        }
        client = get_client_by_user(executor)

        if parent_data.get_one_of_inputs('language'):
            setattr(client, 'language', parent_data.get_one_of_inputs('language'))
            translation.activate(parent_data.get_one_of_inputs('language'))

        # 新建作业
        job_save_result = client.job.save_cron(job_kwargs)
        LOGGER.info('job_result: {result}, job_kwargs: {kwargs}'.format(result=job_save_result, kwargs=job_kwargs))
        if not job_save_result['result']:
            message = job_handle_api_error('job.save_cron', job_kwargs, job_save_result)
            self.logger.error(message)
            data.outputs.ex_data = message
            return False

        data.outputs.cron_id = job_save_result['data']['cron_id']
        data.outputs.status = _('暂停')
        # 更新作业状态
        job_cron_status = data.get_one_of_inputs('job_cron_status')
        if job_cron_status == 1:
            job_update_cron_kwargs = {
                "bk_biz_id": biz_cc_id,
                "cron_status": 1,
                "cron_id": job_save_result['data']['cron_id']
            }
            job_update_result = client.job.update_cron_status(job_update_cron_kwargs)
            if job_update_result['result']:
                data.outputs.status = _('启动')
            else:
                message = _('新建定时任务成功但是启动失败：{error}').format(
                    error=job_handle_api_error('job.update_cron_status', job_update_cron_kwargs, job_update_result))
                self.logger.error(message)
                data.outputs.ex_data = message
                return False

        return True


class JobCronTaskComponent(Component):
    name = _('新建定时作业')
    code = 'job_cron_task'
    bound_service = JobCronTaskService
    form = '%scomponents/atoms/job/job_cron_task.js' % settings.STATIC_URL


class JobPushLocalFilesService(JobService):
    __need_schedule__ = True

    reload_outputs = False

    def inputs_format(self):
        return []

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        biz_cc_id = data.inputs.biz_cc_id
        local_files = data.inputs.job_local_files
        target_ip_list = data.inputs.job_target_ip_list
        target_account = data.inputs.job_target_account
        target_path = data.inputs.job_target_path

        file_manager_type = EnvironmentVariables.objects.get_var('BKAPP_FILE_MANAGER_TYPE')
        if not file_manager_type:
            data.outputs.ex_data = 'File Manager configuration error, contact administrator please.'
            return False

        try:
            file_manager = ManagerFactory.get_manager(manager_type=file_manager_type)
        except Exception as e:
            err_msg = 'can not get file manager for type: {}\n err: {}'
            self.logger.error(err_msg.format(file_manager_type, traceback.format_exc()))
            data.outputs.ex_data = err_msg.format(file_manager_type, e)
            return False

        client = get_client_by_user(executor)

        ip_info = cc_get_ips_info_by_str(executor, biz_cc_id, target_ip_list)
        ip_list = [{'ip': _ip['InnerIP'],
                    'bk_cloud_id': _ip['Source']} for _ip in ip_info['ip_result']]

        file_tags = [_file['tag'] for _file in local_files]

        push_result = file_manager.push_files_to_ips(
            esb_client=client,
            bk_biz_id=biz_cc_id,
            file_tags=file_tags,
            target_path=target_path,
            ips=ip_list,
            account=target_account,
            callback_url=get_node_callback_url(self.id)
        )

        if not push_result['result']:
            data.outputs.ex_data = push_result['message']
            return False

        job_instance_id = push_result['data']['job_id']
        data.outputs.job_inst_id = job_instance_id
        data.outputs.job_inst_url = get_job_instance_url(biz_cc_id, job_instance_id)
        return True


class JobPushLocalFilesComponent(Component):
    name = _('分发本地文件')
    code = 'job_push_local_files'
    bound_service = JobPushLocalFilesService
    form = '%scomponents/atoms/job/job_push_local_files.js' % settings.STATIC_URL
    version = '1.0.0'

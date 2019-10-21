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
import logging

import rsa

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import get_ip_by_regex
from pipeline.utils.crypt import rsa_decrypt_password
from pipeline.core.flow.io import IntItemSchema

from gcloud.conf import settings

__group_name__ = _(u"节点管理(Nodeman)")

LOGGER = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYvKQ/dAh499dXGDoQ2NWgwlev
GWq03EqlvJt+RSaYD1STStM6vEvsPiQ0Nc1GqxvZfqyS6v6acIbhCa1qgYKM8IGk
OVjmORwDUqVR807uCE+GXlf98PSxBbdAPp5e5dTLKd/ZSD6C70lUrMoa8mOktUp/
NnapTCnlIg0YdZjLVwIDAQAB
-----END PUBLIC KEY-----"""


def nodeman_rsa_encrypt(message):
    """
    RSA加密
    """
    return base64.b64encode(rsa.encrypt(
        str(message),
        rsa.PublicKey.load_pkcs1_openssl_pem(PUBLIC_KEY)
    ))


class NodemanCreateTaskService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(5)

    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        client = get_client_by_user(executor)

        bk_biz_id = data.inputs.biz_cc_id
        bk_cloud_id = data.inputs.nodeman_bk_cloud_id
        node_type = data.inputs.nodeman_node_type
        op_type = data.inputs.nodeman_op_type
        nodeman_hosts = data.inputs.nodeman_hosts

        auth_type_dict = {
            'PASSWORD': 'password',
            'KEY': 'key'
        }
        hosts = []

        for host in nodeman_hosts:
            conn_ips = get_ip_by_regex(host['conn_ips'])
            if len(conn_ips) == 0:
                data.set_outputs('ex_data', u'conn_ips %s.' % _(u'为空或输入格式错误'))
                return False

            try:
                login_ip = get_ip_by_regex(host['login_ip'])[0]
            except IndexError:
                data.set_outputs('ex_data', u'login_ip %s.' % _(u'为空或输入格式错误'))
                return False
            try:
                data_ip = get_ip_by_regex(host['data_ip'])[0]
            except IndexError:
                data.set_outputs('ex_data', u'data_ip %s.' % _(u'为空或输入格式错误'))
                return False
            try:
                cascade_ip = get_ip_by_regex(host['cascade_ip'])[0]
            except IndexError:
                data.set_outputs('ex_data', u'cascade_ip %s.' % _(u'为空或输入格式错误'))
                return False

            one = {
                'login_ip': login_ip,
                'data_ip': data_ip,
                'cascade_ip': cascade_ip,
                'os_type': host['os_type'],
                'has_cygwin': host['has_cygwin'],
                'port': host['port'],
                'account': host['account'],
                'auth_type': host['auth_type'],
                'password': host['password'],
                'key': host['key'],
            }

            auth_type = host['auth_type']

            value = host[auth_type.lower()]
            try:
                value = rsa_decrypt_password(value, settings.RSA_PRIV_KEY)
            except Exception:
                # password is not encrypted
                pass
            value = nodeman_rsa_encrypt(value)

            one.update({auth_type_dict[auth_type]: value})

            for conn_ip in conn_ips:
                dict_temp = {'conn_ips': conn_ip}
                dict_temp.update(one)
                hosts.append(dict_temp)

        agent_kwargs = {
            'bk_biz_id': bk_biz_id,
            'bk_cloud_id': bk_cloud_id,
            'node_type': node_type,
            'op_type': op_type,
            'creator': executor,
            'hosts': hosts
        }

        agent_result = client.nodeman.create_task(agent_kwargs)
        LOGGER.info('nodeman created task result: {result}, api_kwargs: {kwargs}'.format(
            result=agent_result, kwargs=agent_kwargs))
        if agent_result['result']:
            data.set_outputs('job_id', agent_result['data']['hosts'][0]['job_id'])
            return True
        else:
            message = u"create agent install task failed: %s" % agent_result['message']
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'任务ID'),
                            key='job_id',
                            type='int',
                            schema=IntItemSchema(description=_(u'提交的任务的job_id'))),
            self.OutputItem(name=_(u'安装成功个数'),
                            key='success_num',
                            type='int',
                            schema=IntItemSchema(description=_(u'任务中安装成功的机器个数'))),
            self.OutputItem(name=_(u'安装失败个数'),
                            key='fail_num',
                            type='int',
                            schema=IntItemSchema(description=_(u'任务中安装失败的机器个数'))),
        ]

    def schedule(self, data, parent_data, callback_data=None):
        bk_biz_id = data.inputs.biz_cc_id
        executor = parent_data.inputs.executor
        client = get_client_by_user(executor)

        job_id = data.get_one_of_outputs('job_id')
        success_num = 0
        fail_num = 0
        fail_ids = []
        fail_hosts = []

        job_kwargs = {
            'bk_biz_id': bk_biz_id,
            'job_id': job_id
        }
        job_result = client.nodeman.get_task_info(job_kwargs)
        host_count = job_result['data']['host_count']
        result_data = job_result['data']

        # 任务执行失败
        if job_result['message'] != 'success':
            data.set_outputs('ex_data', _(u'查询失败，未能获得任务执行结果'))
            self.finish_schedule()
            return False

        for i in range(host_count):
            job_result = result_data['hosts'][i]

            # 安装成功
            if job_result['status'] == 'SUCCEEDED':
                success_num += 1
            # 安装失败
            else:
                fail_num += 1
                fail_ids.append(job_result['host']['id'])
                fail_hosts.append(job_result['host']['inner_ip'])

        if success_num + fail_num == host_count:
            if success_num == host_count:
                self.finish_schedule()
                return True
            else:
                data.set_outputs('success_num', success_num)
                data.set_outputs('fail_num', fail_num)
                error_log = u"<br>%s</br>" % _(u'日志信息为：')
                for i in range(len(fail_ids)):
                    log_kwargs = {
                        'host_id': fail_ids[i],
                        'bk_biz_id': bk_biz_id
                    }
                    result = client.nodeman.get_log(log_kwargs)
                    log_info = result['data']['logs']
                    error_log = u'{error_log}<br><b>{host}{fail_host}</b></br><br>{log}</br>{log_info}'.format(
                        error_log=error_log,
                        host=_(u'主机：'),
                        fail_host=fail_hosts[i],
                        log=_(u'日志：'),
                        log_info=log_info
                    )

                data.set_outputs('ex_data', error_log)
                self.finish_schedule()
                return False


class NodemanCreateTaskComponent(Component):
    name = _(u'安装')
    code = 'nodeman_create_task'
    bound_service = NodemanCreateTaskService
    form = '%scomponents/atoms/sites/%s/nodeman/nodeman_create_task.js' % (settings.STATIC_URL, settings.RUN_VER)

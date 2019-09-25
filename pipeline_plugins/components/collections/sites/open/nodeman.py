# -*- coding: utf-8 -*-
import logging
import rsa
import base64

from django.utils.translation import ugettext_lazy as _
from gcloud.conf import settings
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component
from pipeline_plugins.components.utils import get_ip_by_regex
from pipeline.utils.crypt import rsa_decrypt_password


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

        bk_biz_id = data.inputs.nodeman_bk_biz_id
        bk_cloud_id = data.inputs.nodeman_bk_cloud_id
        node_type = data.inputs.nodeman_node_type
        op_type = data.inputs.nodeman_op_type
        nodeman_hosts = data.inputs.nodeman_hosts
        hosts = []

        for host in nodeman_hosts:
            conn_ips = get_ip_by_regex(host['conn_ips'])
            one = {
                'login_ip': get_ip_by_regex(host['login_ip'])[0],
                'data_ip': get_ip_by_regex(host['data_ip'])[0],
                'cascade_ip': get_ip_by_regex(host['cascade_ip'])[0],
                'os_type': host['os_type'],
                'has_cygwin': host['has_cygwin'],
                'port': host['port'],
                'account': host['account'],
                'auth_type': host['auth_type'],
                'password': host['password'],
                'key': host['key']
            }
            has_cygwin = True if host['has_cygwin'] == '1' else False
            one['has_cygwin'] = has_cygwin
            auth_type = host['auth_type']

            value = host[auth_type.lower()]
            try:
                value = rsa_decrypt_password(value, settings.RSA_PRIV_KEY)
            except Exception:
                # password is not encrypted
                pass
            value = nodeman_rsa_encrypt(value)

            one.update({auth_type.lower(): value})
            for conn_ip in conn_ips:
                one['conn_ips'] = conn_ip
                hosts.append(one)

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
            data.set_outputs('status', agent_result['message'])
            data.set_outputs('agent_kwargs', agent_kwargs)
            return True
        else:
            message = u"create agent install task failed: %s" % agent_result['message']
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []

    def schedule(self, data, parent_data, callback_data=None):
        bk_biz_id = data.inputs.nodeman_bk_biz_id
        executor = parent_data.inputs.executor
        client = get_client_by_user(executor)

        job_id = data.get_one_of_outputs('job_id')
        agent_kwargs = data.get_one_of_outputs('agent_kwargs')
        status = data.get_one_of_outputs('status')
        print job_id, agent_kwargs, status

        if not job_id or not status:
            data.outputs.ex_data = "invalid callback_data, job_instance_id: %s, status: %s" % (job_id, status)
            self.finish_schedule()
            return False

        job_kwargs = {
            'bk_biz_id': bk_biz_id,
            'job_id': job_id
        }
        job_result = client.nodeman.get_task_info(job_kwargs)

        if job_result['message'] != 'success':
            data.set_outputs('ex_data', job_result['message'])
            self.finish_schedule()
            return False
            # 任务执行结束
        job_result = job_result['data']['hosts'][0]

        # 执行成功
        if job_result['status'] == 'SUCCEEDED':
            data.set_outputs('data', job_result['step'])
            self.finish_schedule()
            return True
        # 执行失败
        else:
            data.set_outputs('ex_data', _(u"任务执行失败，%s, error_code: %s") %
                             (job_result['step'], job_result['err_code_desc']))
            self.finish_schedule()
            return False


class NodemanCreateTaskComponent(Component):
    name = _(u'安装')
    code = 'nodeman_create_task'
    bound_service = NodemanCreateTaskService
    form = '%scomponents/atoms/sites/%s/nodeman/nodeman_create_task.js' % (settings.STATIC_URL, settings.RUN_VER)

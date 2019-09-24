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
            return True
        else:
            message = u"create agent install task failed: %s" % agent_result['message']
            data.set_outputs('ex_data', message)
            return False

    def outputs_format(self):
        return []


class NodemanCreateTaskComponent(Component):
    name = _(u'安装')
    code = 'nodeman_create_task'
    bound_service = NodemanCreateTaskService
    form = '%scomponents/atoms/sites/%s/nodeman/nodeman_create_task.js' % (settings.STATIC_URL, settings.RUN_VER)

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging

from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

from blueking.component.shortcuts import get_client_by_user

__group_name__ = _(u"蓝鲸服务(BK)")
logger = logging.getLogger(__name__)


def get_notify_receivers(client, biz_cc_id, receiver_group, more_receiver):
    """
    @summary: 根据通知分组和附加通知人获取最终通知人
    @param username: 请求人
    @param biz_cc_id: 业务CC ID
    @param receiver_group: 通知分组
    @param more_receiver: 附加通知人
    @return:
    """
    kwargs = {
        "app_id": biz_cc_id
    }
    cc_result = client.cc.get_app_by_id(kwargs)
    if not cc_result['result']:
        return False, cc_result['message'], None

    if not cc_result['data']:
        return False, _(u'业务不存在'), None

    biz_data = cc_result['data'][0]
    receivers = []

    if not isinstance(receiver_group, list):
        receiver_group = receiver_group.split(',')

    for group in receiver_group:
        receivers.extend(biz_data[group].split(';'))

    if more_receiver:
        receivers.extend([name.strip() for name in more_receiver.split(',')])

    logger.debug('receivers: %s' % receivers)

    return True, 'success', ','.join(set(receivers))


class NotifyService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)

        notify_type = data.get_one_of_inputs('bk_notify_type')
        receiver_group = data.get_one_of_inputs('bk_receiver_group')
        more_receiver = data.get_one_of_inputs('bk_more_receiver')
        title = data.get_one_of_inputs('bk_notify_title')
        content = data.get_one_of_inputs('bk_notify_content')

        code = ''
        message = ''
        result, msg, receivers = get_notify_receivers(client, biz_cc_id, receiver_group, more_receiver)
        logger.debug('notify receivers: %s' % receivers)

        if not result:
            data.set_outputs('ex_data', msg)
            return False

        for t in notify_type:
            kwargs = self._args_gen[t](self, receivers, title, content)
            result = getattr(client.cmsi, self._send_func[t])(kwargs)

            if not result['result']:
                data.set_outputs('ex_data', result['message'])
                return False

            code = result['code']
            message = result['message']

        data.set_outputs('code', code)
        data.set_outputs('message', message)
        return True

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'返回码'), key='code', type='str'),
            self.OutputItem(name=_(u'信息'), key='message', type='str')
        ]

    def _email_args(self, receivers, title, content):
        return {
            'receiver__username': receivers,
            'title': title,
            'content': content
        }

    def _weixin_args(self, receivers, title, content):
        return {
            'receiver__username': receivers,
            'data': {
                'heading': title,
                'message': content
            }
        }

    def _sms_args(self, receivers, title, content):
        return {
            'receiver__username': receivers,
            'content': u"%s\n%s" % (title, content)
        }

    _send_func = {
        'weixin': 'send_weixin',
        'email': 'send_mail',
        'sms': 'send_sms',
    }

    _args_gen = {
        'weixin': _weixin_args,
        'email': _email_args,
        'sms': _sms_args
    }


class NotifyComponent(Component):
    name = _(u'发送通知')
    code = 'bk_notify'
    bound_service = NotifyService
    form = '%scomponents/atoms/sites/%s/bk/notify.js' % (settings.STATIC_URL, settings.RUN_VER)

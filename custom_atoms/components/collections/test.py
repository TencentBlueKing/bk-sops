# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from blueking.component.shortcuts import get_client_by_user

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

from conf.default import APP_ID

__group_name__ = _(u"测试原子(TEST)")


class TestCustomService(Service):
    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        # biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)

        ip_input = data.get_one_of_inputs('eb_ip_input')
        system_radio = data.get_one_of_inputs('eb_system_radio')
        path_input = data.get_one_of_inputs('eb_path_input')

        api_kwargs = {
            'bk_app_code': APP_ID,
            'ip': ip_input,
            'system': system_radio,
            'path': path_input
        }
        resp = client.myapi.get_dfinfo(**api_kwargs)

        if resp['result']:
            if len(resp['data']) > 1:
                disk_usaged = resp['data'][-1]['usaged']
                message = resp['message']
            else:
                disk_usaged = 0
                message = u"未查询到指定分区"
            data.set_outputs('usaged', disk_usaged)
            data.set_outputs('message', message)
            return True
        else:
            data.set_outputs('ex_data', resp['message'])
            return False

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u"磁盘使用率"), key='usaged', type='int'),
            # self.OutputItem(name='disk_usaged', key='data', type='int'),
            self.OutputItem(name=_(u"返回信息"), key='message', type='str'),
            self.OutputItem(name=_(u"异常信息"), key='ex_message', type='str'),
        ]


class TestCustomComponent(Component):
    name = _(u"磁盘容量查询")
    # name = _(u"diskcapacityquery")
    code = 'test_custom'
    bound_service = TestCustomService
    form = settings.STATIC_URL + 'custom_atoms/test/test_custom.js'

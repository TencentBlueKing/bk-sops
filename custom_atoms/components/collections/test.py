# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from blueking.component.shortcuts import get_client_by_user

__group_name__ = _(u"自定义原子(TEST)")


class GetDfuasgeService(Service):
    __need_schedule__ = False  # 是否异步执行

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        client = get_client_by_user(executor)

        host_ip = data.get_one_of_inputs('self_server_ip')
        host_system = data.get_one_of_inputs('self_server_system')
        hsot_disk = data.get_one_of_inputs('self_server_disk')
        bk_username = data.get_one_of_inputs('self_server_username')

        api_kwargs = {
            'ip': host_ip,
            'system': host_system,
            'disk': hsot_disk,
            ' bk_username': bk_username
        }
        api_result = client.disk_query.get_disk_usage(api_kwargs)

        if api_result['result']:
            data.set_outputs('data', api_result)
            data.set_outputs('message', api_result)
            return True
        else:
            data.set_outputs('ex_data', api_result['message'])
            return False

    def outputs_format(self):
    	"""
    	这里其实就是你完成执行想要看到的输出，对应set_outputs的key
    	"""
        return [
            self.OutputItem(name=_(u'查询结果'), key='data', type='list'),
            self.OutputItem(name=_(u'返回信息'), key='message', type='str'),
            self.OutputItem(name=_(u'异常信息'), key='ex_data', type='str')
        ]


class GetDfuasgeComponent(Component):
    name = _(u'磁盘容量查询')
    code = 'self_server_get_dfusage'
    bound_service = GetDfuasgeService
    form = settings.STATIC_URL + 'custom_atoms/test/test_custom.js'
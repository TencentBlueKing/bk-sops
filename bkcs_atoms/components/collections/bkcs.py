# -*- coding: utf-8 -*-
import logging
from blueapps.utils.esbclient import get_client_by_user

from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component


__group_name__= u"测试API(BKCS)"

LOGGER = logging.getLogger('celery')


class TestCustomService(Service):

    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        server_ip = data.get_one_of_inputs('server_ip')
        disk = data.get_one_of_inputs('disk')

        LOGGER.info('client: %s' % client.__dict__)
        api_kwargs = {
            'bk_biz_id': biz_cc_id,
            'ip': server_ip,
            'disk': disk
        }
        api_result = client.bkcs.get_host_capacity(api_kwargs)
        LOGGER.info('api_result: {result}, api_kwargs: {kwargs}'.format(result=api_result, kwargs=api_kwargs))

        if api_result['result']:
            data.set_outputs('disk', disk)
            data.set_outputs('capacity', api_result['data']['capacity'])
            data.set_outputs('datatime', api_result['data']['datatime'])
            return True
        else:
            data.set_outputs('ex_data', api_result['message'])

    def outputs_format(self):
        return [
            self.OutputItem(name=u'磁盘', key='disk', type='str'),
            self.OutputItem(name=u'已使用容量', key='capacity', type='str'),
            self.OutputItem(name=u'查询时间', key='datatime', type='str')
        ]


class TestCustomCommponent(Component):
    """docstring for TestCustomCommponent"""
    name = u"获取磁盘容量"
    code = 'bkcs_get_host_capacity'
    bound_service = TestCustomService
    form = settings.STATIC_URL + 'bkcs_atoms/bkcs/get_host_capacity.js'

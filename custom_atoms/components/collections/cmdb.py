# -*-coding:utf-8-*-

from django.utils.translation import ugettext_lazy as _
from pipeline.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from blueapps.utils.esbclient import get_client_by_request


__group_name__ = _(u"配置平台(CMDB)")


class TransferFaultModuleService(Service):
    __need_schedule__ = False  # 异步轮询

    def execute(self, data, parent_data):  # 执行函数
        try:
            bk_biz_id = data.get_one_of_inputs('bk_biz_id')
            bk_host_innerip_list = data.get_one_of_inputs('bk_host_innerips').split(";")
            params = {
                "bk_biz_id": bk_biz_id,
                "ip": {
                    "data": bk_host_innerip_list,
                    "exact": 1,
                    "flag": "bk_host_innerip"
                }
            }
            client = get_client_by_request()
            search_result = client.cc.search_host(params)
            search_result_ip_list = [host["host"]["bk_host_innerip"] for host in search_result["data"]["info"]]
            diff_ip_list = list(set(bk_host_innerip_list).difference(set(search_result_ip_list)))
            if not diff_ip_list:
                host_id_list = [host["host"]["bk_host_id"] for host in search_result["data"]["info"]]
                transfer_host_params = {
                    "bk_biz_id": bk_biz_id,
                    "bk_host_id": host_id_list
                }
                transfer_to_faultmodule_result = client.cc.transfer_host_to_faultmodule(transfer_host_params)
                if transfer_to_faultmodule_result["result"]:
                    data.set_outputs('message', u"转移主机成功")
                    return True
                else:
                    data.set_outputs('message', transfer_to_faultmodule_result["message"])
            else:
                data.set_outputs('message', u"该业务不存在以下主机:{0}".format(";".join(diff_ip_list)))
            return False
        except Exception, e:
            data.set_outputs('message', str(e))
            return False

    def schedule(self, data, parent_data, callback_data=None):  # 轮巡函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class TransferFaultModuleComponent(Component):
    name = _(u'上交主机到业务的故障机模块')
    code = 'transfer_host_to_faultmodule'
    bound_service = TransferFaultModuleService
    form = settings.STATIC_URL + 'custom_atoms/cmdb/cmdb_custom.js'


class TransferResourceModuleService(Service):
    __need_schedule__ = False  # 异步轮询

    def execute(self, data, parent_data):  # 执行函数
        try:
            bk_biz_id = data.get_one_of_inputs('bk_biz_id')
            bk_host_innerip_list = data.get_one_of_inputs('bk_host_innerips').split(";")
            params = {
                "bk_biz_id": bk_biz_id,
                "ip": {
                    "data": bk_host_innerip_list,
                    "exact": 1,
                    "flag": "bk_host_innerip"
                }
            }
            client = get_client_by_request()
            search_result = client.cc.search_host(params)
            search_result_ip_list = [host["host"]["bk_host_innerip"] for host in search_result["data"]["info"]]
            diff_ip_list = list(set(bk_host_innerip_list).difference(set(search_result_ip_list)))
            if not diff_ip_list:
                host_id_list = [host["host"]["bk_host_id"] for host in search_result["data"]["info"]]
                transfer_host_params = {
                    "bk_biz_id": bk_biz_id,
                    "bk_host_id": host_id_list
                }
                transfer_to_resourcemodule_result = client.cc.transfer_host_to_resourcemodule(transfer_host_params)
                if transfer_to_resourcemodule_result["result"]:
                    data.set_outputs('message', u"上交主机成功")
                    return True
                else:
                    data.set_outputs('message', transfer_to_resourcemodule_result["message"])
            else:
                data.set_outputs('message', u"该业务不存在以下主机:{0}".format(";".join(diff_ip_list)))
            return False
        except Exception, e:
            data.set_outputs('message', str(e))
            return False

    def schedule(self, data, parent_data, callback_data=None):  # 轮询函数

        return True

    def outputs_format(self):  # 输出结果
        return [
            self.OutputItem(name=_(u'执行信息'), key='message', type='str'),
        ]


class TransferResourceModuleComponent(Component):
    name = _(u'上交主机至资源池')
    code = 'transfer_host_to_resourcemodule'
    bound_service = TransferResourceModuleService
    form = settings.STATIC_URL + 'custom_atoms/cmdb/cmdb_custom.js'

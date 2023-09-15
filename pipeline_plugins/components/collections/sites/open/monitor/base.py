# -*- coding: utf-8 -*-
import ipaddress
from functools import partial

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

from gcloud.core.models import Business
from gcloud.utils import cmdb
from gcloud.utils.handlers import handle_api_error

__group_name__ = _("监控平台(Monitor)")
monitor_handle_api_error = partial(handle_api_error, __group_name__)


class MonitorBaseService(Service):
    """
    监控基类，封装request_body构建与send_request这些通用逻辑
    """

    def build_request_body(self, begin_time, bk_biz_id, shied_type, dimension_config, end_time):
        category_map = {"business": "scope", "IP": "scope", "node": "scope", "strategy": "strategy"}
        request_body = {
            "begin_time": begin_time,
            "bk_biz_id": bk_biz_id,
            "category": category_map[shied_type],
            "cycle_config": {"begin_time": "", "end_time": "", "day_list": [], "week_list": [], "type": 1},
            "description": "shield by bk_sops",
            "dimension_config": dimension_config,
            "end_time": end_time,
            "notice_config": {},
            "shield_notice": False,
        }
        return request_body

    def get_ip_dimension_config(self, scope_value, bk_biz_id, username):
        ip_list = scope_value.split(",")
        if settings.ENABLE_IPV6:
            # 开启了IPV6 要同时查ipv6和ipv4
            ipv4_list = []
            ipv6_list = []

            for ip in ip_list:
                p_address = ipaddress.ip_address(ip)
                if p_address.version == 6:
                    ipv6_list.append(ip)
                else:
                    ipv4_list.append(ip)

            ip_v6_hosts = cmdb.get_business_host_ipv6(
                username=username,
                bk_biz_id=bk_biz_id,
                supplier_account=Business.objects.supplier_account_for_business(bk_biz_id),
                host_fields=["bk_host_id", "bk_cloud_id", "bk_host_innerip", "bk_host_innerip_v6"],
                ip_list=ipv6_list,
            )
            # 监控接口不支持 host_id, 进支持 ip
            host_without_innerip = [host for host in ip_v6_hosts if host["bk_host_innerip"] == ""]
            if host_without_innerip:
                raise Exception(
                    _("主机[{}]innerip字段为空，蓝鲸监控接口仅支持通过该字段进行ip传参").format(
                        ",".join([str(host["bk_host_id"]) for host in host_without_innerip])
                    )
                )

            ip_v4_hosts = cmdb.get_business_host(
                username=username,
                bk_biz_id=bk_biz_id,
                supplier_account=Business.objects.supplier_account_for_business(bk_biz_id),
                host_fields=["bk_host_id", "bk_cloud_id", "bk_host_innerip"],
                ip_list=ipv4_list,
            )

            if not ip_v4_hosts:
                raise Exception(_("当前业务下未查询到ip信息, 请检查ip地址是否填写正确:{}").format(ipv4_list))

            hosts = ip_v4_hosts + ip_v6_hosts

        else:
            hosts = cmdb.get_business_host(
                username=username,
                bk_biz_id=bk_biz_id,
                supplier_account=Business.objects.supplier_account_for_business(bk_biz_id),
                host_fields=["bk_host_id", "bk_cloud_id", "bk_host_innerip"],
                ip_list=ip_list,
            )
        if not hosts:
            raise Exception(_("当前业务下未查询到ip信息, 请检查ip地址是否填写正确:{}").format(scope_value))

        target = []
        for host in hosts:
            target.append({"ip": host["bk_host_innerip"], "bk_cloud_id": host["bk_cloud_id"]})

        return {"scope_type": "ip", "target": target}

    def send_request(self, request_body, data, client):
        response = client.add_shield(**request_body)
        if not response["result"]:
            message = monitor_handle_api_error("monitor.create_shield", request_body, response)
            self.logger.error(message)
            shield_id = ""
            ret_flag = False
        else:
            shield_id = response["data"]["id"]
            ret_flag = True
            message = response["message"]
        data.set_outputs("shield_id", shield_id)
        data.set_outputs("message", message)
        return ret_flag

    def outputs_format(self):
        return [
            self.OutputItem(
                name=_("屏蔽Id"), key="shield_id", type="string", schema=StringItemSchema(description=_("创建的告警屏蔽 ID"))
            ),
            self.OutputItem(
                name=_("详情"), key="message", type="string", schema=StringItemSchema(description=_("创建的告警屏蔽详情"))
            ),
        ]

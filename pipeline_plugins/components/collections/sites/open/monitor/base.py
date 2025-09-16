# -*- coding: utf-8 -*-
import ipaddress
from functools import partial

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from pipeline.core.flow.activity import Service
from pipeline.core.flow.io import StringItemSchema

from gcloud.utils import cmdb
from gcloud.utils.handlers import handle_api_error
from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex
from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6
from pipeline_plugins.components.collections.sites.open.cc.ipv6_utils import cc_get_host_by_innerip_with_ipv6_across_business
from pipeline_plugins.components.utils.sites.open.utils import get_biz_ip_from_frontend_hybrid

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
    
    def get_ip_list(self, ip_str):
        if settings.ENABLE_IPV6:
            ipv6_list, ipv4_list, *_ = extract_ip_from_ip_str(ip_str)
            return ipv6_list + ipv4_list
        return get_ip_by_regex(ip_str)
    
    def get_target_server_ipv6_across_business(self, tenant_id, executor, biz_cc_id, ip_str, logger_handle, data):
        """
        step 1: 去本业务查这些ip，得到两个列表，本业务查询到的host, 本业务查不到的ip列表
        step 2: 对于本业务查不到的host, 去全业务查询，查不到的话则报错，将查到的host_id 与 本业务的 host_id 进行合并
        """
        logger_handle.info("[get_target_server_ipv6_across_business] start search ip, ip_str={}".format(ip_str))
        # 去本业务查
        try:
            (
                host_list,
                ipv4_not_find_list,
                ipv4_with_cloud_not_find_list,
                ipv6_not_find_list,
                ipv6_with_cloud_not_find_list,
            ) = cc_get_host_by_innerip_with_ipv6_across_business(
                tenant_id,
                executor,
                biz_cc_id,
                ip_str,
            )
        except Exception as e:
            logger_handle.exception(
                f"[get_target_server_ipv6_across_business] call "
                f"cc_get_host_by_innerip_with_ipv6_across_business error: {e}"
            )
            data.outputs.ex_data = "ip查询失败，请检查ip配置是否正确：{}".format(e)
            return False, {}

        ip_not_find_str = ",".join(
            ipv4_not_find_list + ipv6_not_find_list + ipv4_with_cloud_not_find_list + ipv6_with_cloud_not_find_list
        )
        logger_handle.info(
            "[get_target_server_ipv6_across_business] not find this ip, ip_not_find_str={}".format(ip_not_find_str)
        )
        # 剩下的ip去全业务查
        host_result = cc_get_host_by_innerip_with_ipv6(tenant_id, executor, None, ip_not_find_str, is_biz_set=True)
        logger_handle.info(
            "[get_target_server_ipv6_across_business] start search this ip:{}, result:{}".format(
                ip_not_find_str, host_list
            )
        )
        if not host_result["result"]:
            data.outputs.ex_data = "ip查询失败，请检查ip配置是否正确，ip_list={}".format(host_result.get("message"))
            return False, {}
        host_data = host_result["data"] + host_list
        return True, {"ip_list": [{"ip": host["bk_host_innerip"], "bk_cloud_id": host["bk_cloud_id"]} for host in host_data]}
    
    def get_target_server_hybrid(self, tenant_id, executor, biz_cc_id, data, ip_str, logger_handle):
        if settings.ENABLE_IPV6:
            return self.get_target_server_ipv6_across_business(
                tenant_id, executor, biz_cc_id, ip_str, logger_handle, data
            )
        # 获取IP
        clean_result, ip_list = get_biz_ip_from_frontend_hybrid(tenant_id, executor, ip_str, biz_cc_id, data)
        if not clean_result:
            return False, {}

        return True, {"ip_list": ip_list}

    def get_ip_dimension_config(self, tenant_id, scope_value, bk_biz_id, username, data):

        # 获取 IP
        _, target_server = self.get_target_server_hybrid(
            tenant_id, username, bk_biz_id, data, scope_value, logger_handle=self.logger
        )
        # if not result:
        #     raise Exception(_("当前业务下未查询到ip信息, 请检查ip地址是否填写正确:{}").format(scope_value))

        return {"scope_type": "ip", "target": target_server.get("ip_list", [])}

    def send_request(self, tenant_id, request_body, data, client):
        response = client.api.add_shield(request_body, headers={"X-Bk-Tenant-Id": tenant_id})
        if not response["result"]:
            message = monitor_handle_api_error("monitor.create_shield", request_body, response)
            self.logger.error(message)
            data.outputs.ex_data = message
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
                name=_("屏蔽Id"),
                key="shield_id",
                type="string",
                schema=StringItemSchema(description=_("创建的告警屏蔽 ID")),
            ),
            self.OutputItem(
                name=_("详情"),
                key="message",
                type="string",
                schema=StringItemSchema(description=_("创建的告警屏蔽详情")),
            ),
        ]

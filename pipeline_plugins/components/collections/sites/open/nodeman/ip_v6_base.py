# -*- coding: utf-8 -*-
from gcloud.conf import settings
from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6
from pipeline_plugins.components.collections.sites.open.nodeman.base import get_host_id_by_inner_ip


class NodemanPluginIPMixin:
    def get_host_list(self, tenant_id, executor, logger, biz_cc_id, ip_str, bk_cloud_id):
        """
        获取host_list
        @param tenant_id: 租户id
        @param executor: executor 执行人
        @param biz_cc_id: biz_cc_id 业务id
        @param ip_str: ip_str ip字符串
        @param supplier_account: supplier_account
        @return:
        """

        def build_ip_str():
            (
                ipv6_list,
                ipv4_list,
                host_id_list,
                ipv4_list_with_cloud_id,
                ipv6_list_with_cloud_id,
            ) = extract_ip_from_ip_str(ip_str)

            ip_list = [
                *["{}:[{}]".format(bk_cloud_id, item) for item in ipv6_list],
                *host_id_list,
                *ipv4_list_with_cloud_id,
                *ipv6_list_with_cloud_id,
                *["{}:{}".format(bk_cloud_id, item) for item in ipv4_list],
            ]

            return ",".join(ip_list)

        supplier_account = supplier_account_for_business(biz_cc_id)
        # 如果开启IPV6
        if settings.ENABLE_IPV6:
            ip_str = build_ip_str()
            host_result = cc_get_host_by_innerip_with_ipv6(tenant_id, executor, biz_cc_id, ip_str, supplier_account)
            if not host_result["result"]:
                return host_result
            return {"result": True, "data": [str(host["bk_host_id"]) for host in host_result["data"]]}

        ip_list = get_ip_by_regex(ip_str)
        host_id_dict = get_host_id_by_inner_ip(tenant_id, executor, logger, bk_cloud_id, biz_cc_id, ip_list)
        return {"result": True, "data": list(host_id_dict.values())}

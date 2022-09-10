# -*- coding: utf-8 -*-
from gcloud.conf import settings
from gcloud.utils.ip import get_ip_by_regex, extract_ip_from_ip_str
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6
from pipeline_plugins.components.utils.sites.open.utils import get_biz_ip_from_frontend


class GetJobTargetServerMixin(object):
    def get_target_server_ipv6(self, executor, biz_cc_id, ip_str):
        supplier_account = supplier_account_for_business(biz_cc_id)
        host_result = cc_get_host_by_innerip_with_ipv6(executor, biz_cc_id, ip_str, supplier_account)
        if not host_result["result"]:
            return host_result
        return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_result["data"]]}

    def get_target_server(
        self,
        executor,
        biz_cc_id,
        data,
        ip_str,
        ip_is_exist=False,
        logger_handle=None,
        is_across=False,
        ignore_ex_data=False,
    ):
        if settings.OPEN_IP_V6:
            return self.get_target_server_ipv6(executor, biz_cc_id, ip_str)
        # 获取IP
        clean_result, ip_list = get_biz_ip_from_frontend(
            ip_str,
            executor,
            biz_cc_id,
            data,
            logger_handle=logger_handle,
            is_across=is_across,
            ip_is_exist=ip_is_exist,
            ignore_ex_data=ignore_ex_data,
        )
        if not clean_result:
            return False, {}

        return True, {"ip_list": ip_list}

    def get_target_server_biz_set(self, executor, ip_table, supplier_account, ip_key="ip", need_build_ip=True):
        def build_ip_str_from_table():
            ip_list = []
            # 第二步 分析表格, 得到 ipv6, host_id，ipv4, 三种字符串，并连接成字符串
            for _ip in ip_table:
                ipv6_list, ipv4_list, host_id_list, ipv4_list_with_cloud_id = extract_ip_from_ip_str(_ip[ip_key])
                ip_list.extend(ipv6_list)
                ip_list.extend(host_id_list)
                ip_list.extend(["{}:{}".format(_ip.get("bk_cloud_id", 0), item) for item in ipv4_list])

            return ",".join(ip_list)

        if settings.OPEN_IP_V6:
            # 第一步 查询这个业务集下所有的业务id, 得到bk_biz_ids
            ip_str = ip_table
            # 在业务集的执行方案中，可能不需要额外处理ip,这种情况直接透传就好
            if need_build_ip:
                ip_str = build_ip_str_from_table()
            host_result = cc_get_host_by_innerip_with_ipv6(executor, None, ip_str, supplier_account, is_biz_set=True)
            if not host_result["result"]:
                return host_result
            return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_result["data"]]}

        # 拼装ip_list， bk_cloud_id为空则值为0
        ip_list = [
            {"ip": ip, "bk_cloud_id": int(_ip["bk_cloud_id"]) if str(_ip["bk_cloud_id"]) else 0}
            for _ip in ip_table
            for ip in get_ip_by_regex(_ip[ip_key])
        ]

        return True, {"ip_list": ip_list}

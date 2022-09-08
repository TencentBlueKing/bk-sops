# -*- coding: utf-8 -*-
from gcloud.conf import settings
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

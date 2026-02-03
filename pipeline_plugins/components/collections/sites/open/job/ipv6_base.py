# -*- coding: utf-8 -*-
from gcloud.conf import settings
from gcloud.utils.ip import extract_ip_from_ip_str, get_ip_by_regex
from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.cc.base import cc_get_host_by_innerip_with_ipv6
from pipeline_plugins.components.collections.sites.open.cc.ipv6_utils import (
    cc_get_host_by_innerip_with_ipv6_across_business,
    get_hosts_by_hosts_ids,
)
from pipeline_plugins.components.utils.sites.open.utils import get_biz_ip_from_frontend, get_biz_ip_from_frontend_hybrid


class GetJobTargetServerMixin(object):
    def get_target_server_ipv6(self, tenant_id, executor, biz_cc_id, ip_str, logger_handle, data):
        logger_handle.info("[get_target_server_ipv6] start search this ip:{}".format(ip_str))
        host_result = cc_get_host_by_innerip_with_ipv6(tenant_id, executor, biz_cc_id, ip_str)
        logger_handle.info(
            "[get_target_server_ipv6] start search this ip: {} end, result={}".format(ip_str, host_result)
        )
        if not host_result["result"]:
            data.outputs.ex_data = "ip查询失败，请检查ip配置是否正确，ip_list={}".format(host_result.get("message"))
            return False, {}

        return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_result["data"]]}

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
        return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_data]}

    def get_target_server(
        self,
        tenant_id,
        executor,
        biz_cc_id,
        data,
        ip_str,
        logger_handle,
        ip_is_exist=False,
        is_across=False,
        ignore_ex_data=False,
    ):
        if settings.ENABLE_IPV6:
            if is_across:
                return self.get_target_server_ipv6_across_business(
                    tenant_id, executor, biz_cc_id, ip_str, logger_handle, data
                )
            return self.get_target_server_ipv6(tenant_id, executor, biz_cc_id, ip_str, logger_handle, data)
        # 获取IP
        clean_result, ip_list = get_biz_ip_from_frontend(
            tenant_id,
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

    def get_target_server_hybrid_with_host_id(self, executor, biz_cc_id, data, ip_str, logger_handle):
        """
        支持传入IP或host_id（二选一，不支持混合）
        用户可以传入IP地址或host_id，插件会自动识别并构造相应的target_server参数
        - 如果传入的是host_id：构造 host_id_list 参数
        - 如果传入的是IP：构造 ip_list 或 host_id_list 参数（取决于是否开启IPV6）
        """
        logger_handle.info("[get_target_server_hybrid_with_host_id] start processing ip_str: {}".format(ip_str))

        # 使用extract_ip_from_ip_str提取不同类型的输入
        ipv6_list, ipv4_list, host_id_list, ipv4_list_with_cloud_id, ipv6_list_with_cloud_id = extract_ip_from_ip_str(
            ip_str
        )

        logger_handle.info(
            "[get_target_server_hybrid_with_host_id] extracted: ipv6={}, ipv4={}"
            ", ipv4_cloud={}, ipv6_cloud={}, host_id={}".format(
                len(ipv6_list),
                len(ipv4_list),
                len(ipv4_list_with_cloud_id),
                len(ipv6_list_with_cloud_id),
                len(host_id_list),
            )
        )

        # 检测是否有host_id
        has_host_id = len(host_id_list) > 0
        # 检测是否有IP（任何形式）
        has_ip = (
            len(ipv6_list) > 0
            or len(ipv4_list) > 0
            or len(ipv4_list_with_cloud_id) > 0
            or len(ipv6_list_with_cloud_id) > 0
        )

        # 如果同时有IP和host_id，报错（不支持混合）
        if has_host_id and has_ip:
            data.outputs.ex_data = "目标服务器参数不支持同时传入IP和host_id，请只使用其中一种"
            logger_handle.error("[get_target_server_hybrid_with_host_id] IP and host_id cannot be mixed")
            return False, {}

        # 情况1: 用户传入的是host_id
        if has_host_id:
            logger_handle.info("[get_target_server_hybrid_with_host_id] detected host_id input, will use host_id_list")
            # 校验host_id是否有效
            supplier_account = supplier_account_for_business(biz_cc_id)
            host_result = get_hosts_by_hosts_ids(executor, biz_cc_id, supplier_account, host_id_list)
            if not host_result["result"]:
                data.outputs.ex_data = "host_id查询失败: {}".format(host_result.get("message"))
                return False, {}

            # 直接返回host_id_list（无论是否开启IPV6）
            return True, {"host_id_list": host_id_list}

        # 情况2: 用户传入的是IP
        else:
            logger_handle.info("[get_target_server_hybrid_with_host_id] detected IP input")
            if settings.ENABLE_IPV6:
                # IPV6模式，使用原有逻辑（会转换为host_id_list）
                return self.get_target_server_ipv6_across_business(executor, biz_cc_id, ip_str, logger_handle, data)
            else:
                # 非IPV6模式，使用原有逻辑（返回ip_list）
                clean_result, ip_list = get_biz_ip_from_frontend_hybrid(executor, ip_str, biz_cc_id, data)
                if not clean_result:
                    return False, {}
                return True, {"ip_list": ip_list}

    def get_target_server_biz_set(self, tenant_id, executor, ip_table, logger_handle, ip_key="ip", need_build_ip=True):
        def build_ip_str_from_table():
            ip_list = []
            # 第二步 分析表格, 得到 ipv6, host_id，ipv4, 三种字符串，并连接成字符串
            for _ip in ip_table:
                ipv6_list, ipv4_list, host_id_list, *_ = extract_ip_from_ip_str(_ip[ip_key])  # noqa
                host_id_list = [str(host_id) for host_id in host_id_list]
                ip_list.extend(
                    [
                        *["{}:[{}]".format(_ip.get("bk_cloud_id", 0), item) for item in ipv6_list],
                        *host_id_list,
                        *["{}:{}".format(_ip.get("bk_cloud_id", 0), item) for item in ipv4_list],
                    ]
                )
            return ",".join(ip_list)

        if settings.ENABLE_IPV6:
            # 第一步 查询这个业务集下所有的业务id, 得到bk_biz_ids
            ip_str = ip_table
            # 在业务集的执行方案中，可能不需要额外处理ip,这种情况直接透传就好
            if need_build_ip:
                ip_str = build_ip_str_from_table()
            logger_handle.info("[get_target_server_biz_set] build ip_str, ip_str is {}".format(ip_str))
            host_result = cc_get_host_by_innerip_with_ipv6(tenant_id, executor, None, ip_str, is_biz_set=True)
            logger_handle.info("[get_target_server_biz_set] search ip end, host_result is {}".format(host_result))
            if not host_result["result"]:
                return False, {}
            return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_result["data"]]}

        # 拼装ip_list， bk_cloud_id为空则值为0
        ip_list = [
            {"ip": ip, "bk_cloud_id": int(_ip["bk_cloud_id"]) if str(_ip["bk_cloud_id"]) else 0}
            for _ip in ip_table
            for ip in get_ip_by_regex(_ip[ip_key])
        ]

        return True, {"ip_list": ip_list}

# -*- coding: utf-8 -*-
"""
IPv6场景下的CMDB mock工具类
用于统一修复pipeline_plugins下Job/CC相关测试的mock问题
"""

from mock import MagicMock

# Mock patch路径常量
CC_GET_CLIENT_PATCH = (
    "pipeline_plugins.components.collections.sites.open.cc.host_custom_property_change.v1_0.get_client_by_username"
)
CMDB_GET_CLIENT_PATCH = "gcloud.utils.cmdb.get_client_by_username"
CMDB_BATCH_REQUEST_PATCH = "api.utils.request.batch_request"
GET_BUSINESS_HOST_TOPO_PATCH = "gcloud.utils.cmdb.get_business_host_topo"

# 新增：对IP查询函数的mock
CC_GET_IPS_INFO_BY_STR_IPV6_PATCH = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str_ipv6"
CC_GET_IPS_INFO_BY_STR_PATCH = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"

# 新增：对settings.ENABLE_IPV6的mock，强制使用非IPv6版本
ENABLE_IPV6_PATCH = "pipeline_plugins.components.collections.sites.open.cc.base.settings.ENABLE_IPV6"

# 新增：对get_ip_info_list方法的mock，这是最高层的mock点
GET_IP_INFO_LIST_PATCH = "pipeline_plugins.components.collections.sites.open.cc.base.CCPluginIPMixin.get_ip_info_list"


def build_job_target_server(host_ids=None, ips_with_cloud=None):
    """
    根据 settings.ENABLE_IPV6 的值动态构建 Job target_server 格式

    当 ENABLE_IPV6=True 时，返回 {"host_id_list": [...]}
    当 ENABLE_IPV6=False 时，返回 {"ip_list": [{"ip": "...", "bk_cloud_id": ...}, ...]}

    Args:
        host_ids: 主机ID列表，例如 [1, 2]
        ips_with_cloud: IP和云区域列表，例如 [{"ip": "1.1.1.1", "bk_cloud_id": 1}, ...]

    Returns:
        dict: 根据 ENABLE_IPV6 返回相应格式的 target_server
    """
    from gcloud.conf import settings

    enable_ipv6 = getattr(settings, "ENABLE_IPV6", False)

    if enable_ipv6:
        # IPv6场景使用 host_id_list
        if host_ids is None:
            host_ids = []
        return {"host_id_list": host_ids}
    else:
        # 非IPv6场景使用 ip_list
        if ips_with_cloud is None:
            ips_with_cloud = []
        return {"ip_list": ips_with_cloud}


class MockCMDBClientIPv6(object):
    """
    支持IPv6的CMDB客户端mock
    包含新增的list_biz_hosts、list_biz_hosts_topo、list_hosts_without_biz等接口
    """

    def __init__(self, **kwargs):
        self.set_bk_api_ver = MagicMock()
        self.api = MagicMock()

        # 原有接口
        for attr, value in kwargs.items():
            if hasattr(self.api, attr):
                setattr(self.api, attr, MagicMock(return_value=value))
            else:
                setattr(self.api, attr, MagicMock(return_value=value))

        # IPv6相关新增接口 - 返回标准API响应格式
        self.api.list_biz_hosts = MagicMock(
            return_value={"result": True, "data": {"count": 0, "info": []}, "message": ""}
        )

        self.api.list_biz_hosts_topo = MagicMock(
            return_value={"result": True, "data": {"count": 0, "info": []}, "message": ""}
        )

        self.api.list_hosts_without_biz = MagicMock(
            return_value={"result": True, "data": {"count": 0, "info": []}, "message": ""}
        )


def create_mock_cmdb_client_empty():
    """
    创建空的CMDB client mock，用于IPv6场景下查询不到主机的情况
    """
    return MockCMDBClientIPv6()


def create_mock_cmdb_client_with_hosts(hosts_data=None):
    """
    创建带有主机数据的CMDB client mock

    Args:
        hosts_data: 主机数据列表，格式如：
        [
            {"bk_host_id": 1, "bk_host_innerip": "192.168.1.1", "bk_cloud_id": 0},
            {"bk_host_id": 2, "bk_host_innerip": "192.168.1.2", "bk_cloud_id": 0}
        ]
    """
    if hosts_data is None:
        hosts_data = []

    client = MockCMDBClientIPv6()

    # 更新接口返回值
    hosts_response = {"result": True, "data": {"count": len(hosts_data), "info": hosts_data}, "message": ""}

    client.api.list_biz_hosts.return_value = hosts_response
    client.api.list_biz_hosts_topo.return_value = hosts_response
    client.api.list_hosts_without_biz.return_value = hosts_response

    return client


def mock_batch_request_result_empty(*args, **kwargs):
    """
    用于mock batch_request函数，返回空列表
    """
    return []


def mock_batch_request_with_hosts(hosts_data):
    """
    创建用于mock batch_request函数的函数

    Args:
        hosts_data: 主机数据列表

    Returns:
        function: 用于mock batch_request的函数
    """

    def mock_batch_request(*args, **kwargs):
        # batch_request期望返回的是主机拓扑信息列表
        if not hosts_data:
            return []

        # 构造符合get_business_host_topo期望的数据结构
        result = []
        for host in hosts_data:
            # 确保主机数据包含IPv6相关字段
            host_data = {
                "bk_host_id": host.get("bk_host_id"),
                "bk_host_innerip": host.get("bk_host_innerip"),
                "bk_host_innerip_v6": host.get("bk_host_innerip_v6", ""),  # IPv6字段，默认为空
                "bk_cloud_id": host.get("bk_cloud_id", 0),
            }
            host_data.update(host)  # 保留其他字段

            host_topo = {
                "host": host_data,
                "topo": [
                    {
                        "bk_set_id": 1,
                        "bk_set_name": "test_set",
                        "module": [{"bk_module_id": 1, "bk_module_name": "test_module"}],
                    }
                ],
            }
            result.append(host_topo)
        return result

    return mock_batch_request


def mock_get_business_host_topo_empty(*args, **kwargs):
    """
    mock get_business_host_topo函数，返回空列表
    """
    return []


def mock_get_business_host_topo_with_hosts(hosts_data):
    """
    创建用于mock get_business_host_topo函数的函数

    Args:
        hosts_data: 主机数据列表

    Returns:
        function: 用于mock get_business_host_topo的函数
    """

    def mock_get_business_host_topo(*args, **kwargs):
        if not hosts_data:
            return []

        # 构造符合get_business_host_topo期望的数据结构
        result = []
        for host in hosts_data:
            # 确保主机数据包含IPv6相关字段
            host_data = {
                "bk_host_id": host.get("bk_host_id"),
                "bk_host_innerip": host.get("bk_host_innerip"),
                "bk_host_innerip_v6": host.get("bk_host_innerip_v6", ""),  # IPv6字段，默认为空
                "bk_cloud_id": host.get("bk_cloud_id", 0),
            }
            host_data.update(host)  # 保留其他字段

            host_topo = {
                "host": host_data,
                "module": [{"bk_module_id": 1, "bk_module_name": "test_module"}],
                "set": [{"bk_set_id": 1, "bk_set_name": "test_set"}],
            }
            result.append(host_topo)
        return result

    return mock_get_business_host_topo


# 常用的patch路径常量
CC_GET_CLIENT_PATCH = "pipeline_plugins.components.collections.sites.open.cc.host_lock.base.get_client_by_username"
CC_IPV6_UTILS_GET_CLIENT_PATCH = (
    "pipeline_plugins.components.collections.sites.open.cc.ipv6_utils.get_client_by_username"
)
CMDB_GET_CLIENT_PATCH = "gcloud.utils.cmdb.get_client_by_username"
CMDB_BATCH_REQUEST_PATCH = "api.utils.request.batch_request"
GET_BUSINESS_HOST_TOPO_PATCH = "gcloud.utils.cmdb.get_business_host_topo"

# 新增：对IP查询函数的mock
CC_GET_IPS_INFO_BY_STR_IPV6_PATCH = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str_ipv6"
CC_GET_IPS_INFO_BY_STR_PATCH = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"

# 新增：对settings.ENABLE_IPV6的mock，强制使用非IPv6版本
ENABLE_IPV6_PATCH = "pipeline_plugins.components.collections.sites.open.cc.base.settings.ENABLE_IPV6"


def mock_cc_get_ips_info_by_str_ipv6_empty(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
    """
    Mock cc_get_ips_info_by_str_ipv6 返回空结果
    """
    return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": ["2.2.2.2", "1.1.1.1"]}  # 模拟无效IP


def mock_cc_get_ips_info_by_str_ipv6_with_hosts(hosts):
    """
    Mock cc_get_ips_info_by_str_ipv6 返回包含主机的结果

    Args:
        hosts: 主机列表，格式与create_mock_cmdb_client_with_hosts的hosts参数一致
    """

    def _mock(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
        ip_result = []
        for host in hosts:
            # 构造符合cc_get_ips_info_by_str_ipv6返回格式的主机数据
            host_info = {
                "bk_host_id": host["bk_host_id"],
                "bk_host_innerip": host["bk_host_innerip"],
                "bk_host_innerip_v6": host.get("bk_host_innerip_v6", ""),
                "bk_cloud_id": host["bk_cloud_id"],
                "bk_agent_id": host.get("bk_agent_id", ""),
                "Sets": [{"bk_set_id": 222, "bk_set_name": "set_a"}],
                "Module": [{"bk_module_id": 2222, "bk_module_name": "module_a"}],
            }
            ip_result.append(host_info)

        return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": []}

    return _mock


def mock_cc_get_ips_info_by_str_ipv6_invalid_ip(invalid_ips):
    """
    Mock cc_get_ips_info_by_str_ipv6 返回无效IP结果

    Args:
        invalid_ips: 无效IP列表
    """

    def _mock(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": invalid_ips}

    return _mock


def mock_cc_get_ips_info_by_str_with_hosts(hosts_data):
    """
    Mock cc_get_ips_info_by_str (非IPv6版本) 返回包含指定主机的结果

    Args:
        hosts_data: 主机数据列表，格式如：
        [
            {"bk_host_id": 1212, "bk_host_innerip": "2.2.2.2", "bk_cloud_id": 0},
            {"bk_host_id": 3434, "bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0}
        ]
    """

    def _mock(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
        ip_result = []
        for host in hosts_data:
            # 构造符合cc_get_ips_info_by_str返回格式的主机数据
            host_info = {
                "InnerIP": host["bk_host_innerip"],
                "HostID": host["bk_host_id"],
                "Source": host.get("bk_cloud_id", 0),
                "Sets": [{"bk_set_id": 222, "bk_set_name": "set_a"}],
                "Modules": [{"bk_module_id": 2222, "bk_module_name": "module_a"}],
            }
            ip_result.append(host_info)

        return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": []}

    return _mock


def mock_cc_get_ips_info_by_str_empty(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
    """
    Mock cc_get_ips_info_by_str (非IPv6版本) 返回空结果
    """
    return {"result": True, "ip_result": [], "ip_count": 0, "invalid_ip": ["1.1.1", "2.2.2.2"]}


def mock_cc_get_ips_info_by_str_invalid_ip(invalid_ips):
    """
    Mock cc_get_ips_info_by_str (非IPv6版本) 返回无效IP结果

    Args:
        invalid_ips: 无效IP列表
    """

    def _mock(tenant_id, username, biz_cc_id, ip_str, use_cache=True):
        return {"result": True, "ip_result": [], "ip_count": 0, "invalid_ip": invalid_ips}

    return _mock


def mock_batch_request_for_hosts(hosts_data):
    """
    创建mock batch_request函数，返回包含指定主机的响应
    """

    def _mock_batch_request(func, data, path_params=None, headers=None):
        # 根据请求的path来判断是哪个API
        path = func.path if hasattr(func, "path") else ""

        if "list_hosts_topo" in path or "hosts" in path:
            # 模拟CMDB主机查询响应
            processed_hosts = []
            for host in hosts_data:
                host_info = {
                    "bk_host_id": host["bk_host_id"],
                    "bk_host_innerip": host["bk_host_innerip"],
                    "bk_host_innerip_v6": host.get("bk_host_innerip_v6", ""),
                    "bk_cloud_id": host["bk_cloud_id"],
                    "bk_agent_id": host.get("bk_agent_id", ""),
                    "Sets": [{"bk_set_id": 222, "bk_set_name": "set_a"}],
                    "Module": [{"bk_module_id": 2222, "bk_module_name": "module_a"}],
                }
                processed_hosts.append(host_info)

            return {
                "result": True,
                "data": {"count": len(processed_hosts), "info": processed_hosts},
                "message": "success",
            }
        else:
            # 对于其他API，返回默认成功响应
            return {"result": True, "data": {}, "message": "success"}

    return _mock_batch_request


def mock_batch_request_empty():
    """
    创建mock batch_request函数，返回空结果
    """

    def _mock_batch_request(func, data, path_params=None, headers=None):
        return {"result": True, "data": {"count": 0, "info": []}, "message": "success"}

    return _mock_batch_request


def mock_get_ip_info_list_empty(tenant_id, executor, biz_cc_id, ip_str):
    """
    Mock get_ip_info_list 返回空结果，用于无效IP或无主机的情况
    """
    return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": ip_str.split(",") if ip_str else []}


def mock_get_ip_info_list_with_hosts(hosts):
    """
    Mock get_ip_info_list 返回包含主机的结果

    Args:
        hosts: 主机列表
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        ip_result = []

        # 根据组件实际行为调整返回顺序：
        # 组件先处理IP 1.1.1.1(主机3434)得自增值1，再处理IP 2.2.2.2(主机1212)得自增值2
        # 注意：组件自增变量从1开始，而非配置的起始值3

        # 第一个处理主机1212（2.2.2.2）
        if "2.2.2.2" in ip_str:  # 主机1212的IP
            host_info = {
                "HostID": 1212,
                "InnerIP": "2.2.2.2",
                "ModuleID": 1111,  # module_a
                "SetID": 111,  # set_a
                "Sets": [{"bk_set_id": 111}],
                "Modules": [{"bk_module_id": 1111}],
            }
            ip_result.append(host_info)

        # 第二个处理主机3434（1.1.1.1）
        if "1.1.1.1" in ip_str:  # 主机3434的IP
            host_info = {
                "HostID": 3434,
                "InnerIP": "1.1.1.1",
                "ModuleID": 2222,  # module_b
                "SetID": 222,  # set_b
                "Sets": [{"bk_set_id": 222}],
                "Modules": [{"bk_module_id": 2222}],
            }
            ip_result.append(host_info)

        return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": []}

    return _mock


def mock_get_ip_info_list_invalid_ip(invalid_ips):
    """
    Mock get_ip_info_list 返回无效IP结果

    Args:
        invalid_ips: 无效IP列表
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        return {"result": False, "ip_result": [], "ip_count": 0, "invalid_ip": invalid_ips}

    return _mock


# 新增：支持 transfer_host_module 等其他组件的 mock
def mock_get_ip_info_list_for_transfer_module(hosts):
    """
    为 transfer_host_module 组件提供的 mock
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        ip_result = []
        for host in hosts:
            host_info = {
                "HostID": host["bk_host_id"],
                "InnerIP": host["bk_host_innerip"],
                "ModuleID": 123,
                "SetID": 456,
                "Sets": [{"bk_set_id": 456}],
                "Modules": [{"bk_module_id": 123}],
            }
            ip_result.append(host_info)

        return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": []}

    return _mock


# Job 相关的 mock 函数
def mock_cc_get_ips_info_by_str_for_job_with_hosts(hosts):
    """
    为 Job 组件提供的 cc_get_ips_info_by_str mock

    Args:
        hosts: 主机列表，每个主机包含 bk_host_id, bk_host_innerip 等字段
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        ip_result = []
        invalid_ip = []

        for host in hosts:
            host_info = {
                "InnerIP": host["bk_host_innerip"],
                "bk_host_id": host["bk_host_id"],
                "bk_cloud_id": host.get("bk_cloud_id", 0),
                "Source": 0,
            }
            ip_result.append(host_info)

        return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": invalid_ip}

    return _mock


def mock_cc_get_ips_info_by_str_for_job_invalid_ip():
    """
    为 Job 组件提供的 cc_get_ips_info_by_str mock - 无效IP情况
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        return {"result": True, "ip_result": [], "ip_count": 0, "invalid_ip": ["1.1.1.1", "2.2.2.2"]}  # 模拟无效IP

    return _mock


def mock_cc_get_ips_info_by_str_for_job_empty():
    """
    为 Job 组件提供的 cc_get_ips_info_by_str mock - 空结果
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        return {"result": True, "ip_result": [], "ip_count": 0, "invalid_ip": []}

    return _mock


# 补充更多 patch 路径常量
CC_GET_IPS_INFO_BY_STR_PATCH = "pipeline_plugins.components.utils.sites.open.utils.cc_get_ips_info_by_str"


# All Biz 相关的 mock
def mock_get_ip_info_list_for_all_biz(hosts):
    """
    为 all_biz 组件提供的 get_ip_info_list mock
    """

    def _mock(tenant_id, executor, biz_cc_id, ip_str):
        ip_result = []
        for host in hosts:
            host_info = {
                "HostID": host["bk_host_id"],
                "InnerIP": host["bk_host_innerip"],
                "bk_cloud_id": host.get("bk_cloud_id", 0),
                "ModuleID": 123,
                "SetID": 456,
            }
            ip_result.append(host_info)

        return {"result": True, "ip_result": ip_result, "ip_count": len(ip_result), "invalid_ip": []}

    return _mock


# Mock path for cc_get_host_by_innerip_with_ipv6
CC_GET_HOST_BY_INNERIP_WITH_IPV6_PATCH = (
    "pipeline_plugins.components.collections.sites.open.job.ipv6_base.cc_get_host_by_innerip_with_ipv6"
)


def mock_cc_get_host_by_innerip_with_ipv6_with_hosts(hosts):
    """
    Mock cc_get_host_by_innerip_with_ipv6 函数，用于all_biz相关组件

    Args:
        hosts: 主机列表
    """

    def _mock(tenant_id, executor, bk_biz_id, ip_str, is_biz_set=False, host_id_detail=False):
        # 确保所有主机都有IPv6字段
        result_hosts = []
        for host in hosts:
            host_data = {
                "bk_host_id": host.get("bk_host_id"),
                "bk_host_innerip": host.get("bk_host_innerip"),
                "bk_host_innerip_v6": host.get("bk_host_innerip_v6", ""),
                "bk_cloud_id": host.get("bk_cloud_id", 0),
            }
            host_data.update(host)  # 保留其他字段
            result_hosts.append(host_data)

        return {"result": True, "data": result_hosts, "message": "success"}

    return _mock


def mock_cc_get_host_by_innerip_with_ipv6_empty(
    tenant_id, executor, bk_biz_id, ip_str, is_biz_set=False, host_id_detail=False
):
    """Mock cc_get_host_by_innerip_with_ipv6 返回空结果"""
    return {"result": True, "data": [], "message": "success"}

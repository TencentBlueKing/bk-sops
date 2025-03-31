# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource ap_ap_is_using
    # 返回正在被使用的接入点
    ap_ap_is_using = bind_property(
        Operation,
        name="ap_ap_is_using",
        method="GET",
        path="/api/ap/ap_is_using/",
    )

    # bkapi resource ap_create_ap
    # 新增接入点
    ap_create_ap = bind_property(
        Operation,
        name="ap_create_ap",
        method="POST",
        path="/api/ap/",
    )

    # bkapi resource ap_delete_ap
    # 删除接入点
    ap_delete_ap = bind_property(
        Operation,
        name="ap_delete_ap",
        method="DELETE",
        path="/api/ap/{pk}/",
    )

    # bkapi resource ap_init_plugin_data
    # 初始化插件信息
    ap_init_plugin_data = bind_property(
        Operation,
        name="ap_init_plugin_data",
        method="POST",
        path="/api/ap/init_plugin/",
    )

    # bkapi resource ap_list_ap
    # 查询接入点列表
    ap_list_ap = bind_property(
        Operation,
        name="ap_list_ap",
        method="GET",
        path="/api/ap/",
    )

    # bkapi resource ap_retrieve_ap
    # 查询接入点详情
    ap_retrieve_ap = bind_property(
        Operation,
        name="ap_retrieve_ap",
        method="GET",
        path="/api/ap/{pk}/",
    )

    # bkapi resource ap_test_ap
    # 接入点可用性测试
    ap_test_ap = bind_property(
        Operation,
        name="ap_test_ap",
        method="POST",
        path="/api/ap/test/",
    )

    # bkapi resource ap_update_ap
    # 编辑接入点
    ap_update_ap = bind_property(
        Operation,
        name="ap_update_ap",
        method="PUT",
        path="/api/ap/{pk}/",
    )

    # bkapi resource backend_plugin_create_export_plugin_task
    # 触发插件打包导出
    backend_plugin_create_export_plugin_task = bind_property(
        Operation,
        name="backend_plugin_create_export_plugin_task",
        method="POST",
        path="/backend/api/plugin/create_export_task/",
    )

    # bkapi resource backend_plugin_create_plugin_config_template
    # 创建配置模板,未指定则创建全部平台类型
    backend_plugin_create_plugin_config_template = bind_property(
        Operation,
        name="backend_plugin_create_plugin_config_template",
        method="POST",
        path="/backend/api/plugin/create_config_template/",
    )

    # bkapi resource backend_plugin_create_register_task
    # 创建注册任务
    backend_plugin_create_register_task = bind_property(
        Operation,
        name="backend_plugin_create_register_task",
        method="POST",
        path="/backend/api/plugin/create_register_task/",
    )

    # bkapi resource backend_plugin_delete_plugin
    # 删除插件
    backend_plugin_delete_plugin = bind_property(
        Operation,
        name="backend_plugin_delete_plugin",
        method="POST",
        path="/backend/api/plugin/delete/",
    )

    # bkapi resource backend_plugin_download_content
    # 下载导出的内容,此处不做实际的文件读取，将由nginx负责处理
    backend_plugin_download_content = bind_property(
        Operation,
        name="backend_plugin_download_content",
        method="GET",
        path="/backend/export/download/",
    )

    # bkapi resource backend_plugin_list_plugin
    # 插件列表
    backend_plugin_list_plugin = bind_property(
        Operation,
        name="backend_plugin_list_plugin",
        method="GET",
        path="/backend/api/plugin/",
    )

    # bkapi resource backend_plugin_package_status_operation
    # 插件包状态类操作
    backend_plugin_package_status_operation = bind_property(
        Operation,
        name="backend_plugin_package_status_operation",
        method="POST",
        path="/backend/api/plugin/package_status_operation/",
    )

    # bkapi resource backend_plugin_plugin_history
    # 插件包历史
    backend_plugin_plugin_history = bind_property(
        Operation,
        name="backend_plugin_plugin_history",
        method="GET",
        path="/backend/api/plugin/{pk}/history/",
    )

    # bkapi resource backend_plugin_plugin_parse
    # 解析插件包
    backend_plugin_plugin_parse = bind_property(
        Operation,
        name="backend_plugin_plugin_parse",
        method="POST",
        path="/backend/api/plugin/parse/",
    )

    # bkapi resource backend_plugin_plugin_status_operation
    # 插件状态类操作
    backend_plugin_plugin_status_operation = bind_property(
        Operation,
        name="backend_plugin_plugin_status_operation",
        method="POST",
        path="/backend/api/plugin/plugin_status_operation/",
    )

    # bkapi resource backend_plugin_query_debug
    # 查询调试结果
    backend_plugin_query_debug = bind_property(
        Operation,
        name="backend_plugin_query_debug",
        method="GET",
        path="/backend/api/plugin/query_debug/",
    )

    # bkapi resource backend_plugin_query_export_plugin_task
    # 获取一个导出任务结果
    backend_plugin_query_export_plugin_task = bind_property(
        Operation,
        name="backend_plugin_query_export_plugin_task",
        method="GET",
        path="/backend/api/plugin/query_export_task/",
    )

    # bkapi resource backend_plugin_query_plugin_config_instance
    # 查询配置模板实例
    backend_plugin_query_plugin_config_instance = bind_property(
        Operation,
        name="backend_plugin_query_plugin_config_instance",
        method="GET",
        path="/backend/api/plugin/query_config_instance/",
    )

    # bkapi resource backend_plugin_query_plugin_config_template
    # 查询配置模板
    backend_plugin_query_plugin_config_template = bind_property(
        Operation,
        name="backend_plugin_query_plugin_config_template",
        method="GET",
        path="/backend/api/plugin/query_config_template/",
    )

    # bkapi resource backend_plugin_query_plugin_info
    # 查询插件信息
    backend_plugin_query_plugin_info = bind_property(
        Operation,
        name="backend_plugin_query_plugin_info",
        method="GET",
        path="/backend/api/plugin/info/",
    )

    # bkapi resource backend_plugin_query_register_task
    # 查询插件注册任务
    backend_plugin_query_register_task = bind_property(
        Operation,
        name="backend_plugin_query_register_task",
        method="GET",
        path="/backend/api/plugin/query_register_task/",
    )

    # bkapi resource backend_plugin_release_package
    # 发布（上线）插件包
    backend_plugin_release_package = bind_property(
        Operation,
        name="backend_plugin_release_package",
        method="POST",
        path="/backend/api/plugin/release/",
    )

    # bkapi resource backend_plugin_release_plugin_config_template
    # 发布配置模板
    backend_plugin_release_plugin_config_template = bind_property(
        Operation,
        name="backend_plugin_release_plugin_config_template",
        method="POST",
        path="/backend/api/plugin/release_config_template/",
    )

    # bkapi resource backend_plugin_render_plugin_config_template
    # 渲染配置模板
    backend_plugin_render_plugin_config_template = bind_property(
        Operation,
        name="backend_plugin_render_plugin_config_template",
        method="POST",
        path="/backend/api/plugin/render_config_template/",
    )

    # bkapi resource backend_plugin_retrieve_plugin
    # 插件详情
    backend_plugin_retrieve_plugin = bind_property(
        Operation,
        name="backend_plugin_retrieve_plugin",
        method="GET",
        path="/backend/api/plugin/{pk}/",
    )

    # bkapi resource backend_plugin_start_debug
    # 开始调试
    backend_plugin_start_debug = bind_property(
        Operation,
        name="backend_plugin_start_debug",
        method="POST",
        path="/backend/api/plugin/start_debug/",
    )

    # bkapi resource backend_plugin_stop_debug
    # 停止调试
    backend_plugin_stop_debug = bind_property(
        Operation,
        name="backend_plugin_stop_debug",
        method="POST",
        path="/backend/api/plugin/stop_debug/",
    )

    # bkapi resource backend_plugin_upload
    # 上传文件接口
    backend_plugin_upload = bind_property(
        Operation,
        name="backend_plugin_upload",
        method="POST",
        path="/backend/api/plugin/upload/",
    )

    # bkapi resource backend_plugin_upload_file
    # 上传文件接口
    backend_plugin_upload_file = bind_property(
        Operation,
        name="backend_plugin_upload_file",
        method="POST",
        path="/backend/package/upload/",
    )

    # bkapi resource choice_list_category
    # 查询类别列表
    choice_list_category = bind_property(
        Operation,
        name="choice_list_category",
        method="GET",
        path="/api/choice/category/",
    )

    # bkapi resource choice_list_job_type
    # 查询任务类型列表
    choice_list_job_type = bind_property(
        Operation,
        name="choice_list_job_type",
        method="GET",
        path="/api/choice/job_type/",
    )

    # bkapi resource choice_list_op
    # 查询操作列表
    choice_list_op = bind_property(
        Operation,
        name="choice_list_op",
        method="GET",
        path="/api/choice/op/",
    )

    # bkapi resource choice_list_os_type
    # 查询系统列表
    choice_list_os_type = bind_property(
        Operation,
        name="choice_list_os_type",
        method="GET",
        path="/api/choice/os_type/",
    )

    # bkapi resource cloud_create_cloud
    # 创建云区域
    cloud_create_cloud = bind_property(
        Operation,
        name="cloud_create_cloud",
        method="POST",
        path="/api/cloud/",
    )

    # bkapi resource cloud_delete_cloud
    # 删除云区域
    cloud_delete_cloud = bind_property(
        Operation,
        name="cloud_delete_cloud",
        method="DELETE",
        path="/api/cloud/{pk}/",
    )

    # bkapi resource cloud_list_cloud
    # 查询云区域列表
    cloud_list_cloud = bind_property(
        Operation,
        name="cloud_list_cloud",
        method="GET",
        path="/api/cloud/",
    )

    # bkapi resource cloud_list_cloud_biz
    # 查询某主机服务信息
    cloud_list_cloud_biz = bind_property(
        Operation,
        name="cloud_list_cloud_biz",
        method="GET",
        path="/api/cloud/{pk}/biz/",
    )

    # bkapi resource cloud_retrieve_cloud
    # 查询云区域详情
    cloud_retrieve_cloud = bind_property(
        Operation,
        name="cloud_retrieve_cloud",
        method="GET",
        path="/api/cloud/{pk}/",
    )

    # bkapi resource cloud_update_cloud
    # 编辑云区域
    cloud_update_cloud = bind_property(
        Operation,
        name="cloud_update_cloud",
        method="PUT",
        path="/api/cloud/{pk}/",
    )

    # bkapi resource cmdb_fetch_topo
    # 获得拓扑信息
    cmdb_fetch_topo = bind_property(
        Operation,
        name="cmdb_fetch_topo",
        method="GET",
        path="/api/cmdb/fetch_topo/",
    )

    # bkapi resource cmdb_retrieve_biz
    # 查询用户所有业务
    cmdb_retrieve_biz = bind_property(
        Operation,
        name="cmdb_retrieve_biz",
        method="GET",
        path="/api/cmdb/biz/",
    )

    # bkapi resource cmdb_search_ip
    # 查询IP
    cmdb_search_ip = bind_property(
        Operation,
        name="cmdb_search_ip",
        method="GET",
        path="/api/cmdb/search_ip/",
    )

    # bkapi resource cmdb_search_topo
    # 查询拓扑
    cmdb_search_topo = bind_property(
        Operation,
        name="cmdb_search_topo",
        method="GET",
        path="/api/cmdb/search_topo/",
    )

    # bkapi resource cmdb_service_template
    # 查询服务模板列表
    cmdb_service_template = bind_property(
        Operation,
        name="cmdb_service_template",
        method="GET",
        path="/api/cmdb/service_template/",
    )

    # bkapi resource create_task
    # 新增任务
    create_task = bind_property(
        Operation,
        name="create_task",
        method="POST",
        path="/api/v1/{bk_biz_id}/tasks/",
    )

    # bkapi resource debug_fetch_hosts_by_subscription
    # 查询订阅任务下的主机
    debug_fetch_hosts_by_subscription = bind_property(
        Operation,
        name="debug_fetch_hosts_by_subscription",
        method="GET",
        path="/api/debug/fetch_hosts_by_subscription/",
    )

    # bkapi resource debug_fetch_subscription_details
    # 查询订阅任务详情
    debug_fetch_subscription_details = bind_property(
        Operation,
        name="debug_fetch_subscription_details",
        method="GET",
        path="/api/debug/fetch_subscription_details/",
    )

    # bkapi resource debug_fetch_subscriptions_by_host
    # 查询主机涉及到的所有订阅任务
    debug_fetch_subscriptions_by_host = bind_property(
        Operation,
        name="debug_fetch_subscriptions_by_host",
        method="GET",
        path="/api/debug/fetch_subscriptions_by_host/",
    )

    # bkapi resource debug_fetch_task_details
    # 查询任务执行详情
    debug_fetch_task_details = bind_property(
        Operation,
        name="debug_fetch_task_details",
        method="GET",
        path="/api/debug/fetch_task_details/",
    )

    # bkapi resource get_gse_config
    # 获取配置
    get_gse_config = bind_property(
        Operation,
        name="get_gse_config",
        method="GET",
        path="/backend/get_gse_config/",
    )

    # bkapi resource get_log
    # 获取日志
    get_log = bind_property(
        Operation,
        name="get_log",
        method="GET",
        path="/api/v1/get_log/{bk_biz_id}/{host_id}/",
    )

    # bkapi resource get_task_info
    # 根据id获取任务执行信息
    get_task_info = bind_property(
        Operation,
        name="get_task_info",
        method="GET",
        path="/api/v1/get_task_info/{bk_biz_id}/{job_id}/",
    )

    # bkapi resource healthz
    healthz = bind_property(
        Operation,
        name="healthz",
        method="GET",
        path="/backend/api/healthz/",
    )

    # bkapi resource healthz_healthz
    # 自监控
    healthz_healthz = bind_property(
        Operation,
        name="healthz_healthz",
        method="GET",
        path="/api/healthz/",
    )

    # bkapi resource host_list_host
    # 查询主机列表
    host_list_host = bind_property(
        Operation,
        name="host_list_host",
        method="POST",
        path="/api/host/search/",
    )

    # bkapi resource host_remove_host
    # 移除主机
    host_remove_host = bind_property(
        Operation,
        name="host_remove_host",
        method="POST",
        path="/api/host/remove_host/",
    )

    # bkapi resource host_retrieve_biz_proxies
    # 查询业务下云区域的proxy集合
    host_retrieve_biz_proxies = bind_property(
        Operation,
        name="host_retrieve_biz_proxies",
        method="GET",
        path="/api/host/biz_proxies/",
    )

    # bkapi resource host_retrieve_cloud_proxies
    # 查询有proxy操作权限的云区域proxy列表
    host_retrieve_cloud_proxies = bind_property(
        Operation,
        name="host_retrieve_cloud_proxies",
        method="GET",
        path="/api/host/proxies/",
    )

    # bkapi resource host_sync_cmdb_host
    # 同步CMDB主机
    host_sync_cmdb_host = bind_property(
        Operation,
        name="host_sync_cmdb_host",
        method="GET",
        path="/api/host/sync_cmdb_host/",
    )

    # bkapi resource host_update_host
    # 更新Proxy主机信息
    host_update_host = bind_property(
        Operation,
        name="host_update_host",
        method="POST",
        path="/api/host/update_single/",
    )

    # bkapi resource host_v2_list_host
    # 查询主机列表
    host_v2_list_host = bind_property(
        Operation,
        name="host_v2_list_host",
        method="POST",
        path="/api/v2/host/search/",
    )

    # bkapi resource host_v2_node_statistic
    # 统计给定拓扑节点的主机数量
    host_v2_node_statistic = bind_property(
        Operation,
        name="host_v2_node_statistic",
        method="POST",
        path="/api/v2/host/node_statistic/",
    )

    # bkapi resource host_v2_nodes_agent_status
    # 统计给定拓扑节点的agent状态统计
    host_v2_nodes_agent_status = bind_property(
        Operation,
        name="host_v2_nodes_agent_status",
        method="POST",
        path="/api/v2/host/agent_status/",
    )

    # bkapi resource installchannel_create_install_channel
    # 创建安装通道
    installchannel_create_install_channel = bind_property(
        Operation,
        name="installchannel_create_install_channel",
        method="POST",
        path="/api/install_channel/",
    )

    # bkapi resource installchannel_delete_install_channel
    # 删除安装通道
    installchannel_delete_install_channel = bind_property(
        Operation,
        name="installchannel_delete_install_channel",
        method="DELETE",
        path="/api/install_channel/{pk}/",
    )

    # bkapi resource installchannel_list_install_channel
    # 查询安装通道列表
    installchannel_list_install_channel = bind_property(
        Operation,
        name="installchannel_list_install_channel",
        method="GET",
        path="/api/install_channel/",
    )

    # bkapi resource installchannel_update_install_channel
    # 编辑安装通道
    installchannel_update_install_channel = bind_property(
        Operation,
        name="installchannel_update_install_channel",
        method="PUT",
        path="/api/install_channel/{pk}/",
    )

    # bkapi resource ipchooser_host_check
    # 根据用户手动输入的`IP`/`IPv6`/`主机名`/`host_id`等关键字信息获取真实存在的机器信息
    ipchooser_host_check = bind_property(
        Operation,
        name="ipchooser_host_check",
        method="POST",
        path="/core/api/ipchooser_host/check/",
    )

    # bkapi resource ipchooser_host_details
    # 根据主机关键信息获取机器详情信息
    ipchooser_host_details = bind_property(
        Operation,
        name="ipchooser_host_details",
        method="POST",
        path="/core/system/api/ipchooser_host/details/",
    )

    # bkapi resource ipchooser_topo_agent_statistics
    # 获取多个拓扑节点的主机 Agent 状态统计信息
    ipchooser_topo_agent_statistics = bind_property(
        Operation,
        name="ipchooser_topo_agent_statistics",
        method="POST",
        path="/core/api/ipchooser_topo/agent_statistics/",
    )

    # bkapi resource ipchooser_topo_query_host_id_infos
    # 根据多个拓扑节点与搜索条件批量分页查询所包含的主机 ID 信息
    ipchooser_topo_query_host_id_infos = bind_property(
        Operation,
        name="ipchooser_topo_query_host_id_infos",
        method="POST",
        path="/core/api/ipchooser_topo/query_host_id_infos/",
    )

    # bkapi resource ipchooser_topo_query_hosts
    # 根据多个拓扑节点与搜索条件批量分页查询所包含的主机信息
    ipchooser_topo_query_hosts = bind_property(
        Operation,
        name="ipchooser_topo_query_hosts",
        method="POST",
        path="/core/api/ipchooser_topo/query_hosts/",
    )

    # bkapi resource ipchooser_topo_query_path
    # 查询多个节点拓扑路径
    ipchooser_topo_query_path = bind_property(
        Operation,
        name="ipchooser_topo_query_path",
        method="POST",
        path="/core/api/ipchooser_topo/query_path/",
    )

    # bkapi resource ipchooser_topo_trees
    # 批量获取含各节点主机数量的拓扑树
    ipchooser_topo_trees = bind_property(
        Operation,
        name="ipchooser_topo_trees",
        method="POST",
        path="/core/api/ipchooser_topo/trees/",
    )

    # bkapi resource job_collect_job_log
    # 查询日志
    job_collect_job_log = bind_property(
        Operation,
        name="job_collect_job_log",
        method="POST",
        path="/api/job/{pk}/collect_log/",
    )

    # bkapi resource job_get_job_commands
    # 获取安装命令
    job_get_job_commands = bind_property(
        Operation,
        name="job_get_job_commands",
        method="GET",
        path="/api/job/{pk}/get_job_commands/",
    )

    # bkapi resource job_get_job_log
    # 查询日志
    job_get_job_log = bind_property(
        Operation,
        name="job_get_job_log",
        method="GET",
        path="/api/job/{pk}/log/",
    )

    # bkapi resource job_install_job
    # 安装类任务
    job_install_job = bind_property(
        Operation,
        name="job_install_job",
        method="POST",
        path="/api/job/install/",
    )

    # bkapi resource job_list_job
    # 查询任务列表
    job_list_job = bind_property(
        Operation,
        name="job_list_job",
        method="POST",
        path="/api/job/job_list/",
    )

    # bkapi resource job_operate_job
    # 操作类任务
    job_operate_job = bind_property(
        Operation,
        name="job_operate_job",
        method="POST",
        path="/api/job/operate/",
    )

    # bkapi resource job_retrieve_job
    # 查询任务详情
    job_details = bind_property(
        Operation,
        name="job_retrieve_job",
        method="POST",
        path="/system/api/job/{id}/details/",
    )

    get_job_log = bind_property(
        Operation,
        name="get_job_log",
        method="GET",
        path="/system/api/job/{id}/log/",
    )

    # bkapi resource job_retry_job
    # 重试任务
    job_retry_job = bind_property(
        Operation,
        name="job_retry_job",
        method="POST",
        path="/api/job/{pk}/retry/",
    )

    # bkapi resource job_retry_node
    # 原子粒度重试任务
    job_retry_node = bind_property(
        Operation,
        name="job_retry_node",
        method="POST",
        path="/api/job/{pk}/retry_node/",
    )

    # bkapi resource job_revoke_job
    # 终止任务
    job_revoke_job = bind_property(
        Operation,
        name="job_revoke_job",
        method="POST",
        path="/api/job/{pk}/revoke/",
    )

    # bkapi resource list_profile
    # 查询个性配置
    list_profile = bind_property(
        Operation,
        name="list_profile",
        method="GET",
        path="/api/profile/",
    )

    # bkapi resource meta_get_filter_condition
    # 获取过滤条件
    meta_get_filter_condition = bind_property(
        Operation,
        name="meta_get_filter_condition",
        method="GET",
        path="/api/meta/filter_condition/",
    )

    # bkapi resource meta_job_settings
    # 任务配置接口
    meta_job_settings = bind_property(
        Operation,
        name="meta_job_settings",
        method="POST",
        path="/api/meta/job_settings/",
    )

    # bkapi resource meta_retrieve_global_settings
    # 查询全局配置
    meta_retrieve_global_settings = bind_property(
        Operation,
        name="meta_retrieve_global_settings",
        method="GET",
        path="/api/meta/global_settings/",
    )

    # bkapi resource permission_fetch_permission
    # 根据条件返回用户权限
    permission_fetch_permission = bind_property(
        Operation,
        name="permission_fetch_permission",
        method="POST",
        path="/api/permission/fetch/",
    )

    # bkapi resource permission_list_ap_permission
    # 返回用户接入点权限
    permission_list_ap_permission = bind_property(
        Operation,
        name="permission_list_ap_permission",
        method="GET",
        path="/api/permission/ap/",
    )

    # bkapi resource permission_list_cloud_permission
    # 返回用户云区域的权限
    permission_list_cloud_permission = bind_property(
        Operation,
        name="permission_list_cloud_permission",
        method="GET",
        path="/api/permission/cloud/",
    )

    # bkapi resource permission_list_package_permission
    # 返回用户插件包权限
    permission_list_package_permission = bind_property(
        Operation,
        name="permission_list_package_permission",
        method="GET",
        path="/api/permission/package/",
    )

    # bkapi resource permission_list_plugin_instance_permission
    # 返回用户插件实例权限
    permission_list_plugin_instance_permission = bind_property(
        Operation,
        name="permission_list_plugin_instance_permission",
        method="GET",
        path="/api/permission/plugin/",
    )

    # bkapi resource permission_list_startegy_permission
    # 返回用户部署策略权限
    permission_list_startegy_permission = bind_property(
        Operation,
        name="permission_list_startegy_permission",
        method="GET",
        path="/api/permission/startegy/",
    )

    # bkapi resource plugin_fetch_package_info
    # 获取插件包信息
    plugin_fetch_package_info = bind_property(
        Operation,
        name="plugin_fetch_package_info",
        method="GET",
        path="/api/plugin/{plugin_name}/package/{pk}/",
    )

    # bkapi resource plugin_fetch_version
    # 获取插件最新版本
    plugin_fetch_version = bind_property(
        Operation,
        name="plugin_fetch_version",
        method="GET",
        path="/api/plugin/{plugin_name}/package/fetch_version/",
    )

    # bkapi resource plugin_list_host
    # 查询插件列表
    plugin_list_host = bind_property(
        Operation,
        name="plugin_list_host",
        method="POST",
        path="/api/plugin/search/",
    )

    # bkapi resource plugin_list_package
    # 查询进程包列表,pk为具体进程名
    plugin_list_package = bind_property(
        Operation,
        name="plugin_list_package",
        method="GET",
        path="/api/plugin/{pk}/package/",
    )

    # bkapi resource plugin_list_process
    # 查询插件列表,pk为official, external 或 scripts
    plugin_list_process = bind_property(
        Operation,
        name="plugin_list_process",
        method="GET",
        path="/api/plugin/{pk}/process/",
    )

    # bkapi resource plugin_list_process_status
    # 查询主机进程状态信息
    plugin_list_process_status = bind_property(
        Operation,
        name="plugin_list_process_status",
        method="POST",
        path="/api/plugin/process/status/",
    )

    # bkapi resource plugin_operate_plugin
    # 插件操作类任务
    plugin_operate_plugin = bind_property(
        Operation,
        name="plugin_operate_plugin",
        method="POST",
        path="/api/plugin/operate/",
    )

    # bkapi resource plugin_plugin_statistics
    # 获取插件统计数据
    plugin_plugin_statistics = bind_property(
        Operation,
        name="plugin_plugin_statistics",
        method="GET",
        path="/api/plugin/statistics/",
    )

    # bkapi resource plugin_v2_create_export_plugin_task
    # 触发插件打包导出
    plugin_v2_create_export_plugin_task = bind_property(
        Operation,
        name="plugin_v2_create_export_plugin_task",
        method="POST",
        path="/api/v2/plugin/create_export_task/",
    )

    # bkapi resource plugin_v2_create_register_task
    # 创建注册任务
    plugin_v2_create_register_task = bind_property(
        Operation,
        name="plugin_v2_create_register_task",
        method="POST",
        path="/api/v2/plugin/create_register_task/",
    )

    # bkapi resource plugin_v2_fetch_config_variables
    # 获取配置模板参数
    plugin_v2_fetch_config_variables = bind_property(
        Operation,
        name="plugin_v2_fetch_config_variables",
        method="POST",
        path="/api/v2/plugin/fetch_config_variables/",
    )

    # bkapi resource plugin_v2_fetch_package_deploy_info
    # 获取插件包部署信息
    plugin_v2_fetch_package_deploy_info = bind_property(
        Operation,
        name="plugin_v2_fetch_package_deploy_info",
        method="POST",
        path="/api/v2/plugin/fetch_package_deploy_info/",
    )

    # bkapi resource plugin_v2_fetch_resource_policy
    # 查询资源策略
    plugin_v2_fetch_resource_policy = bind_property(
        Operation,
        name="plugin_v2_fetch_resource_policy",
        method="GET",
        path="/api/v2/plugin/fetch_resource_policy/",
    )

    # bkapi resource plugin_v2_fetch_resource_policy_status
    # 查询资源策略状态
    plugin_v2_fetch_resource_policy_status = bind_property(
        Operation,
        name="plugin_v2_fetch_resource_policy_status",
        method="GET",
        path="/api/v2/plugin/fetch_resource_policy_status/",
    )

    # bkapi resource plugin_v2_list_plugin
    # 插件列表
    plugin_v2_list_plugin = bind_property(
        Operation,
        name="plugin_v2_list_plugin",
        method="GET",
        path="/api/v2/plugin/",
    )

    # bkapi resource plugin_v2_list_plugin_host
    # 查询插件下主机
    plugin_v2_list_plugin_host = bind_property(
        Operation,
        name="plugin_v2_list_plugin_host",
        method="POST",
        path="/api/v2/plugin/list_plugin_host/",
    )

    # bkapi resource plugin_v2_operate_plugin
    # 插件操作
    plugin_v2_operate_plugin = bind_property(
        Operation,
        name="plugin_v2_operate_plugin",
        method="POST",
        path="/api/v2/plugin/operate/",
    )

    # bkapi resource plugin_v2_package_status_operation
    # 插件包状态类操作
    plugin_v2_package_status_operation = bind_property(
        Operation,
        name="plugin_v2_package_status_operation",
        method="POST",
        path="/api/v2/plugin/package_status_operation/",
    )

    # bkapi resource plugin_v2_plugin_history
    # 插件包历史
    plugin_v2_plugin_history = bind_property(
        Operation,
        name="plugin_v2_plugin_history",
        method="GET",
        path="/api/v2/plugin/{pk}/history/",
    )

    # bkapi resource plugin_v2_plugin_parse
    # 解析插件包
    plugin_v2_plugin_parse = bind_property(
        Operation,
        name="plugin_v2_plugin_parse",
        method="POST",
        path="/api/v2/plugin/parse/",
    )

    # bkapi resource plugin_v2_plugin_status_operation
    # 插件状态类操作
    plugin_v2_plugin_status_operation = bind_property(
        Operation,
        name="plugin_v2_plugin_status_operation",
        method="POST",
        path="/api/v2/plugin/plugin_status_operation/",
    )

    # bkapi resource plugin_v2_plugin_upload
    # 插件上传
    plugin_v2_plugin_upload = bind_property(
        Operation,
        name="plugin_v2_plugin_upload",
        method="POST",
        path="/api/v2/plugin/upload/",
    )

    # bkapi resource plugin_v2_query_export_plugin_task
    # 获取一个导出任务结果
    plugin_v2_query_export_plugin_task = bind_property(
        Operation,
        name="plugin_v2_query_export_plugin_task",
        method="GET",
        path="/api/v2/plugin/query_export_task/",
    )

    # bkapi resource plugin_v2_query_register_task
    # 查询插件注册任务
    plugin_v2_query_register_task = bind_property(
        Operation,
        name="plugin_v2_query_register_task",
        method="GET",
        path="/api/v2/plugin/query_register_task/",
    )

    # bkapi resource plugin_v2_retrieve_plugin
    # 插件详情
    plugin_v2_retrieve_plugin = bind_property(
        Operation,
        name="plugin_v2_retrieve_plugin",
        method="GET",
        path="/api/v2/plugin/{pk}/",
    )

    # bkapi resource plugin_v2_set_resource_policy
    # 设置资源策略
    plugin_v2_set_resource_policy = bind_property(
        Operation,
        name="plugin_v2_set_resource_policy",
        method="POST",
        path="/api/v2/plugin/set_resource_policy/",
    )

    # bkapi resource plugin_v2_update_plugin
    # 编辑插件
    plugin_v2_update_plugin = bind_property(
        Operation,
        name="plugin_v2_update_plugin",
        method="PUT",
        path="/api/v2/plugin/{pk}/",
    )

    # bkapi resource policy_create_policy
    # 创建策略
    policy_create_policy = bind_property(
        Operation,
        name="policy_create_policy",
        method="POST",
        path="/api/policy/create_policy/",
    )

    # bkapi resource policy_fetch_common_variable
    # 获取公共变量
    policy_fetch_common_variable = bind_property(
        Operation,
        name="policy_fetch_common_variable",
        method="GET",
        path="/api/policy/fetch_common_variable/",
    )

    # bkapi resource policy_fetch_policy_abnormal_info
    # 获取策略异常信息
    policy_fetch_policy_abnormal_info = bind_property(
        Operation,
        name="policy_fetch_policy_abnormal_info",
        method="POST",
        path="/api/policy/fetch_policy_abnormal_info/",
    )

    # bkapi resource policy_fetch_policy_topo
    # 插件策略拓扑
    policy_fetch_policy_topo = bind_property(
        Operation,
        name="policy_fetch_policy_topo",
        method="POST",
        path="/api/policy/fetch_policy_topo/",
    )

    # bkapi resource policy_host_policy
    # 主机策略列表
    policy_host_policy = bind_property(
        Operation,
        name="policy_host_policy",
        method="GET",
        path="/api/policy/host_policy/",
    )

    # bkapi resource policy_list_policy
    # 查询策略列表
    policy_list_policy = bind_property(
        Operation,
        name="policy_list_policy",
        method="POST",
        path="/api/policy/search/",
    )

    # bkapi resource policy_migrate_preview
    # 策略执行预览（计算变更详情）
    policy_migrate_preview = bind_property(
        Operation,
        name="policy_migrate_preview",
        method="POST",
        path="/api/policy/migrate_preview/",
    )

    # bkapi resource policy_policy_empty
    # empty
    policy_policy_empty = bind_property(
        Operation,
        name="policy_policy_empty",
        method="GET",
        path="/api/policy/empty/",
    )

    # bkapi resource policy_policy_info
    # 策略详细
    policy_policy_info = bind_property(
        Operation,
        name="policy_policy_info",
        method="GET",
        path="/api/policy/{pk}/",
    )

    # bkapi resource policy_policy_operate
    # 策略操作
    policy_policy_operate = bind_property(
        Operation,
        name="policy_policy_operate",
        method="POST",
        path="/api/policy/operate/",
    )

    # bkapi resource policy_policy_preselection
    # plugin_preselection
    policy_policy_preselection = bind_property(
        Operation,
        name="policy_policy_preselection",
        method="POST",
        path="/api/policy/plugin_preselection/",
    )

    # bkapi resource policy_policy_preview
    # 策略执行预览（预览所选范围）
    policy_policy_preview = bind_property(
        Operation,
        name="policy_policy_preview",
        method="POST",
        path="/api/policy/selected_preview/",
    )

    # bkapi resource policy_rollback_preview
    # 策略回滚预览
    policy_rollback_preview = bind_property(
        Operation,
        name="policy_rollback_preview",
        method="POST",
        path="/api/policy/rollback_preview/",
    )

    # bkapi resource policy_run_policy
    # 执行策略
    policy_run_policy = bind_property(
        Operation,
        name="policy_run_policy",
        method="POST",
        path="/api/policy/{pk}/run/",
    )

    # bkapi resource policy_update_policy
    # 更新策略
    policy_update_policy = bind_property(
        Operation,
        name="policy_update_policy",
        method="POST",
        path="/api/policy/{pk}/update_policy/",
    )

    # bkapi resource policy_update_policy_info
    # 编辑策略概要信息
    policy_update_policy_info = bind_property(
        Operation,
        name="policy_update_policy_info",
        method="PUT",
        path="/api/policy/{pk}/",
    )

    # bkapi resource policy_upgrade_preview
    # 升级预览
    policy_upgrade_preview = bind_property(
        Operation,
        name="policy_upgrade_preview",
        method="GET",
        path="/api/policy/{pk}/upgrade_preview/",
    )

    # bkapi resource rsa_fetch_public_keys
    # 获取公钥列表
    rsa_fetch_public_keys = bind_property(
        Operation,
        name="rsa_fetch_public_keys",
        method="POST",
        path="/core/api/encrypt_rsa/fetch_public_keys/",
    )

    # bkapi resource service_info
    # 查询某主机服务信息
    service_info = bind_property(
        Operation,
        name="service_info",
        method="GET",
        path="/api/cloud/service_info/",
    )

    # bkapi resource subscription_cmdb_subscription
    # 接收cmdb事件回调
    subscription_cmdb_subscription = bind_property(
        Operation,
        name="subscription_cmdb_subscription",
        method="POST",
        path="/backend/api/subscription/cmdb_subscription/",
    )

    # bkapi resource subscription_collect_subscription_task_result_detail
    # 采集任务执行详细结果
    subscription_collect_subscription_task_result_detail = bind_property(
        Operation,
        name="subscription_collect_subscription_task_result_detail",
        method="POST",
        path="/backend/api/subscription/collect_task_result_detail/",
    )

    # bkapi resource subscription_create_subscription
    # 创建订阅
    subscription_create_subscription = bind_property(
        Operation,
        name="subscription_create_subscription",
        method="POST",
        path="/backend/api/subscription/create/",
    )

    # bkapi resource subscription_delete_subscription
    # 删除订阅
    subscription_delete_subscription = bind_property(
        Operation,
        name="subscription_delete_subscription",
        method="POST",
        path="/backend/api/subscription/delete/",
    )

    # bkapi resource subscription_fetch_commands
    # 返回安装命令
    subscription_fetch_commands = bind_property(
        Operation,
        name="subscription_fetch_commands",
        method="POST",
        path="/backend/api/subscription/fetch_commands/",
    )

    # bkapi resource subscription_fetch_policy_topo
    # 插件策略拓扑
    subscription_fetch_policy_topo = bind_property(
        Operation,
        name="subscription_fetch_policy_topo",
        method="POST",
        path="/backend/api/subscription/fetch_policy_topo/",
    )

    # bkapi resource subscription_get_gse_config
    # 获取配置
    subscription_get_gse_config = bind_property(
        Operation,
        name="subscription_get_gse_config",
        method="POST",
        path="/backend/get_gse_config/",
    )

    # bkapi resource subscription_list_deploy_policy
    # 查询策略列表
    subscription_list_deploy_policy = bind_property(
        Operation,
        name="subscription_list_deploy_policy",
        method="POST",
        path="/backend/api/subscription/search_deploy_policy/",
    )

    # bkapi resource subscription_query_host_policy
    # 获取主机策略列表
    subscription_query_host_policy = bind_property(
        Operation,
        name="subscription_query_host_policy",
        method="GET",
        path="/backend/api/subscription/query_host_policy/",
    )

    # bkapi resource subscription_query_host_subscription_ids
    # 获取主机订阅列表
    subscription_query_host_subscription_ids = bind_property(
        Operation,
        name="subscription_query_host_subscription_ids",
        method="GET",
        path="/backend/api/subscription/query_host_subscriptions/",
    )

    # bkapi resource subscription_query_instance_status
    # 查询订阅运行状态
    subscription_query_instance_status = bind_property(
        Operation,
        name="subscription_query_instance_status",
        method="POST",
        path="/backend/api/subscription/instance_status/",
    )

    # bkapi resource subscription_report_log
    # 上报日志
    subscription_report_log = bind_property(
        Operation,
        name="subscription_report_log",
        method="POST",
        path="/backend/report_log/",
    )

    # bkapi resource subscription_retry_node
    # 重试原子
    subscription_retry_node = bind_property(
        Operation,
        name="subscription_retry_node",
        method="POST",
        path="/backend/api/subscription/retry_node/",
    )

    # bkapi resource subscription_retry_subscription
    # 重试失败的任务
    subscription_retry_subscription = bind_property(
        Operation,
        name="subscription_retry_subscription",
        method="POST",
        path="/backend/api/subscription/retry/",
    )

    # bkapi resource subscription_revoke_subscription
    # 终止正在执行的任务
    subscription_revoke_subscription = bind_property(
        Operation,
        name="subscription_revoke_subscription",
        method="POST",
        path="/backend/api/subscription/revoke/",
    )

    # bkapi resource subscription_run_subscription
    # 执行订阅
    subscription_run_subscription = bind_property(
        Operation,
        name="subscription_run_subscription",
        method="POST",
        path="/backend/api/subscription/run/",
    )

    # bkapi resource subscription_search_plugin_policy
    # 获取插件策略信息
    subscription_search_plugin_policy = bind_property(
        Operation,
        name="subscription_search_plugin_policy",
        method="GET",
        path="/backend/api/subscription/search_plugin_policy/",
    )

    # bkapi resource subscription_statistic
    # 统计订阅任务数据
    subscription_statistic = bind_property(
        Operation,
        name="subscription_statistic",
        method="POST",
        path="/backend/api/subscription/statistic/",
    )

    # bkapi resource subscription_subscription_check_task_ready
    # 查询任务是否已准备完成
    subscription_subscription_check_task_ready = bind_property(
        Operation,
        name="subscription_subscription_check_task_ready",
        method="POST",
        path="/backend/api/subscription/check_task_ready/",
    )

    # bkapi resource subscription_subscription_info
    # 订阅详情
    subscription_subscription_info = bind_property(
        Operation,
        name="subscription_subscription_info",
        method="POST",
        path="/backend/api/subscription/info/",
    )

    # bkapi resource subscription_subscription_switch
    # 订阅启停
    subscription_subscription_switch = bind_property(
        Operation,
        name="subscription_subscription_switch",
        method="POST",
        path="/backend/api/subscription/switch/",
    )

    # bkapi resource subscription_subscription_task_result
    # 任务执行结果
    subscription_subscription_task_result = bind_property(
        Operation,
        name="subscription_subscription_task_result",
        method="POST",
        path="/backend/api/subscription/task_result/",
    )

    # bkapi resource subscription_subscription_task_result_detail
    # 任务执行详细结果
    subscription_subscription_task_result_detail = bind_property(
        Operation,
        name="subscription_subscription_task_result_detail",
        method="POST",
        path="/backend/api/subscription/task_result_detail/",
    )

    # bkapi resource subscription_update_subscription
    # 更新订阅
    subscription_update_subscription = bind_property(
        Operation,
        name="subscription_update_subscription",
        method="POST",
        path="/backend/api/subscription/update/",
    )

    # bkapi resource tjj_fetch_pwd
    # 查询支持查询密码的主机
    tjj_fetch_pwd = bind_property(
        Operation,
        name="tjj_fetch_pwd",
        method="POST",
        path="/api/tjj/fetch_pwd/",
    )

    # bkapi resource update_or_create_profile
    # 更新或创建个性配置
    update_or_create_profile = bind_property(
        Operation,
        name="update_or_create_profile",
        method="POST",
        path="/api/profile/update_or_create/",
    )

    # 查询插件列表
    search_host_plugin = bind_property(
        Operation,
        name="search_host_plugin",
        method="POST",
        path="/system/api/plugin/search/",
    )

    # 插件操作类任务
    operate_plugin = bind_property(Operation, name="operate_plugin", method="POST", path="/system/api/plugin/operate/")

    # 获取公钥列表
    fetch_public_keys = bind_property(
        Operation,
        name="fetch_public_keys",
        method="GET",
        path="/system/api/encrypt_rsa/fetch_public_keys/",
    )

    # bkapi resource ap_list_ap
    # 查询接入点列表
    ap_list = bind_property(
        Operation,
        name="ap_list",
        method="GET",
        path="/system/api/ap/",
    )

    # bkapi resource cloud_list_cloud
    # 查询云区域列表
    cloud_list = bind_property(
        Operation,
        name="cloud_list",
        method="GET",
        path="/system/api/cloud/",
    )

    # 查询插件列表
    plugin_list = bind_property(
        Operation,
        name="plugin_list",
        method="GET",
        path="/system/backend/api/plugin/",
    )

    # bkapi resource installchannel_list_install_channel
    # 查询安装通道列表
    install_channel_list = bind_property(
        Operation,
        name="install_channel_list",
        method="GET",
        path="/system/api/install_channel/",
    )

    # 获取插件列表
    list_packages = bind_property(
        Operation, name="list_packages", method="GET", path="/system/api/plugin/{process}/package/"
    )

    job_install = bind_property(
        Operation,
        name="job_install",
        method="POST",
        path="/system/api/job/install/",
    )

    job_operate = bind_property(
        Operation,
        name="job_operate",
        method="POST",
        path="/system/api/job/operate/",
    )


class Client(APIGatewayClient):
    """Bkapi bk-nodeman client"""

    _api_name = "bk-nodeman"

    api = bind_property(Group, name="api")

# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def ap_ap_is_using(self) -> Operation:
        """
        bkapi resource ap_ap_is_using
        返回正在被使用的接入点
        """
    @property
    def ap_create_ap(self) -> Operation:
        """
        bkapi resource ap_create_ap
        新增接入点
        """
    @property
    def ap_delete_ap(self) -> Operation:
        """
        bkapi resource ap_delete_ap
        删除接入点
        """
    @property
    def ap_init_plugin_data(self) -> Operation:
        """
        bkapi resource ap_init_plugin_data
        初始化插件信息
        """
    @property
    def ap_list_ap(self) -> Operation:
        """
        bkapi resource ap_list_ap
        查询接入点列表
        """
    @property
    def ap_retrieve_ap(self) -> Operation:
        """
        bkapi resource ap_retrieve_ap
        查询接入点详情
        """
    @property
    def ap_test_ap(self) -> Operation:
        """
        bkapi resource ap_test_ap
        接入点可用性测试
        """
    @property
    def ap_update_ap(self) -> Operation:
        """
        bkapi resource ap_update_ap
        编辑接入点
        """
    @property
    def backend_plugin_create_export_plugin_task(self) -> Operation:
        """
        bkapi resource backend_plugin_create_export_plugin_task
        触发插件打包导出
        """
    @property
    def backend_plugin_create_plugin_config_template(self) -> Operation:
        """
        bkapi resource backend_plugin_create_plugin_config_template
        创建配置模板,未指定则创建全部平台类型
        """
    @property
    def backend_plugin_create_register_task(self) -> Operation:
        """
        bkapi resource backend_plugin_create_register_task
        创建注册任务
        """
    @property
    def backend_plugin_delete_plugin(self) -> Operation:
        """
        bkapi resource backend_plugin_delete_plugin
        删除插件
        """
    @property
    def backend_plugin_download_content(self) -> Operation:
        """
        bkapi resource backend_plugin_download_content
        下载导出的内容,此处不做实际的文件读取，将由nginx负责处理
        """
    @property
    def backend_plugin_list_plugin(self) -> Operation:
        """
        bkapi resource backend_plugin_list_plugin
        插件列表
        """
    @property
    def backend_plugin_package_status_operation(self) -> Operation:
        """
        bkapi resource backend_plugin_package_status_operation
        插件包状态类操作
        """
    @property
    def backend_plugin_plugin_history(self) -> Operation:
        """
        bkapi resource backend_plugin_plugin_history
        插件包历史
        """
    @property
    def backend_plugin_plugin_parse(self) -> Operation:
        """
        bkapi resource backend_plugin_plugin_parse
        解析插件包
        """
    @property
    def backend_plugin_plugin_status_operation(self) -> Operation:
        """
        bkapi resource backend_plugin_plugin_status_operation
        插件状态类操作
        """
    @property
    def backend_plugin_query_debug(self) -> Operation:
        """
        bkapi resource backend_plugin_query_debug
        查询调试结果
        """
    @property
    def backend_plugin_query_export_plugin_task(self) -> Operation:
        """
        bkapi resource backend_plugin_query_export_plugin_task
        获取一个导出任务结果
        """
    @property
    def backend_plugin_query_plugin_config_instance(self) -> Operation:
        """
        bkapi resource backend_plugin_query_plugin_config_instance
        查询配置模板实例
        """
    @property
    def backend_plugin_query_plugin_config_template(self) -> Operation:
        """
        bkapi resource backend_plugin_query_plugin_config_template
        查询配置模板
        """
    @property
    def backend_plugin_query_plugin_info(self) -> Operation:
        """
        bkapi resource backend_plugin_query_plugin_info
        查询插件信息
        """
    @property
    def backend_plugin_query_register_task(self) -> Operation:
        """
        bkapi resource backend_plugin_query_register_task
        查询插件注册任务
        """
    @property
    def backend_plugin_release_package(self) -> Operation:
        """
        bkapi resource backend_plugin_release_package
        发布（上线）插件包
        """
    @property
    def backend_plugin_release_plugin_config_template(self) -> Operation:
        """
        bkapi resource backend_plugin_release_plugin_config_template
        发布配置模板
        """
    @property
    def backend_plugin_render_plugin_config_template(self) -> Operation:
        """
        bkapi resource backend_plugin_render_plugin_config_template
        渲染配置模板
        """
    @property
    def backend_plugin_retrieve_plugin(self) -> Operation:
        """
        bkapi resource backend_plugin_retrieve_plugin
        插件详情
        """
    @property
    def backend_plugin_start_debug(self) -> Operation:
        """
        bkapi resource backend_plugin_start_debug
        开始调试
        """
    @property
    def backend_plugin_stop_debug(self) -> Operation:
        """
        bkapi resource backend_plugin_stop_debug
        停止调试
        """
    @property
    def backend_plugin_upload(self) -> Operation:
        """
        bkapi resource backend_plugin_upload
        上传文件接口
        """
    @property
    def backend_plugin_upload_file(self) -> Operation:
        """
        bkapi resource backend_plugin_upload_file
        上传文件接口
        """
    @property
    def choice_list_category(self) -> Operation:
        """
        bkapi resource choice_list_category
        查询类别列表
        """
    @property
    def choice_list_job_type(self) -> Operation:
        """
        bkapi resource choice_list_job_type
        查询任务类型列表
        """
    @property
    def choice_list_op(self) -> Operation:
        """
        bkapi resource choice_list_op
        查询操作列表
        """
    @property
    def choice_list_os_type(self) -> Operation:
        """
        bkapi resource choice_list_os_type
        查询系统列表
        """
    @property
    def cloud_create_cloud(self) -> Operation:
        """
        bkapi resource cloud_create_cloud
        创建云区域
        """
    @property
    def cloud_delete_cloud(self) -> Operation:
        """
        bkapi resource cloud_delete_cloud
        删除云区域
        """
    @property
    def cloud_list_cloud(self) -> Operation:
        """
        bkapi resource cloud_list_cloud
        查询云区域列表
        """
    @property
    def cloud_list_cloud_biz(self) -> Operation:
        """
        bkapi resource cloud_list_cloud_biz
        查询某主机服务信息
        """
    @property
    def cloud_retrieve_cloud(self) -> Operation:
        """
        bkapi resource cloud_retrieve_cloud
        查询云区域详情
        """
    @property
    def cloud_update_cloud(self) -> Operation:
        """
        bkapi resource cloud_update_cloud
        编辑云区域
        """
    @property
    def cmdb_fetch_topo(self) -> Operation:
        """
        bkapi resource cmdb_fetch_topo
        获得拓扑信息
        """
    @property
    def cmdb_retrieve_biz(self) -> Operation:
        """
        bkapi resource cmdb_retrieve_biz
        查询用户所有业务
        """
    @property
    def cmdb_search_ip(self) -> Operation:
        """
        bkapi resource cmdb_search_ip
        查询IP
        """
    @property
    def cmdb_search_topo(self) -> Operation:
        """
        bkapi resource cmdb_search_topo
        查询拓扑
        """
    @property
    def cmdb_service_template(self) -> Operation:
        """
        bkapi resource cmdb_service_template
        查询服务模板列表
        """
    @property
    def create_task(self) -> Operation:
        """
        bkapi resource create_task
        新增任务
        """
    @property
    def debug_fetch_hosts_by_subscription(self) -> Operation:
        """
        bkapi resource debug_fetch_hosts_by_subscription
        查询订阅任务下的主机
        """
    @property
    def debug_fetch_subscription_details(self) -> Operation:
        """
        bkapi resource debug_fetch_subscription_details
        查询订阅任务详情
        """
    @property
    def debug_fetch_subscriptions_by_host(self) -> Operation:
        """
        bkapi resource debug_fetch_subscriptions_by_host
        查询主机涉及到的所有订阅任务
        """
    @property
    def debug_fetch_task_details(self) -> Operation:
        """
        bkapi resource debug_fetch_task_details
        查询任务执行详情
        """
    @property
    def get_gse_config(self) -> Operation:
        """
        bkapi resource get_gse_config
        获取配置
        """
    @property
    def get_log(self) -> Operation:
        """
        bkapi resource get_log
        获取日志
        """
    @property
    def get_task_info(self) -> Operation:
        """
        bkapi resource get_task_info
        根据id获取任务执行信息
        """
    @property
    def healthz(self) -> Operation:
        """
        bkapi resource healthz
        """
    @property
    def healthz_healthz(self) -> Operation:
        """
        bkapi resource healthz_healthz
        自监控
        """
    @property
    def host_list_host(self) -> Operation:
        """
        bkapi resource host_list_host
        查询主机列表
        """
    @property
    def host_remove_host(self) -> Operation:
        """
        bkapi resource host_remove_host
        移除主机
        """
    @property
    def host_retrieve_biz_proxies(self) -> Operation:
        """
        bkapi resource host_retrieve_biz_proxies
        查询业务下云区域的proxy集合
        """
    @property
    def host_retrieve_cloud_proxies(self) -> Operation:
        """
        bkapi resource host_retrieve_cloud_proxies
        查询有proxy操作权限的云区域proxy列表
        """
    @property
    def host_sync_cmdb_host(self) -> Operation:
        """
        bkapi resource host_sync_cmdb_host
        同步CMDB主机
        """
    @property
    def host_update_host(self) -> Operation:
        """
        bkapi resource host_update_host
        更新Proxy主机信息
        """
    @property
    def host_v2_list_host(self) -> Operation:
        """
        bkapi resource host_v2_list_host
        查询主机列表
        """
    @property
    def host_v2_node_statistic(self) -> Operation:
        """
        bkapi resource host_v2_node_statistic
        统计给定拓扑节点的主机数量
        """
    @property
    def host_v2_nodes_agent_status(self) -> Operation:
        """
        bkapi resource host_v2_nodes_agent_status
        统计给定拓扑节点的agent状态统计
        """
    @property
    def installchannel_create_install_channel(self) -> Operation:
        """
        bkapi resource installchannel_create_install_channel
        创建安装通道
        """
    @property
    def installchannel_delete_install_channel(self) -> Operation:
        """
        bkapi resource installchannel_delete_install_channel
        删除安装通道
        """
    @property
    def installchannel_list_install_channel(self) -> Operation:
        """
        bkapi resource installchannel_list_install_channel
        查询安装通道列表
        """
    @property
    def installchannel_update_install_channel(self) -> Operation:
        """
        bkapi resource installchannel_update_install_channel
        编辑安装通道
        """
    @property
    def ipchooser_host_check(self) -> Operation:
        """
        bkapi resource ipchooser_host_check
        根据用户手动输入的`IP`/`IPv6`/`主机名`/`host_id`等关键字信息获取真实存在的机器信息
        """
    @property
    def ipchooser_host_details(self) -> Operation:
        """
        bkapi resource ipchooser_host_details
        根据主机关键信息获取机器详情信息
        """
    @property
    def ipchooser_topo_agent_statistics(self) -> Operation:
        """
        bkapi resource ipchooser_topo_agent_statistics
        获取多个拓扑节点的主机 Agent 状态统计信息
        """
    @property
    def ipchooser_topo_query_host_id_infos(self) -> Operation:
        """
        bkapi resource ipchooser_topo_query_host_id_infos
        根据多个拓扑节点与搜索条件批量分页查询所包含的主机 ID 信息
        """
    @property
    def ipchooser_topo_query_hosts(self) -> Operation:
        """
        bkapi resource ipchooser_topo_query_hosts
        根据多个拓扑节点与搜索条件批量分页查询所包含的主机信息
        """
    @property
    def ipchooser_topo_query_path(self) -> Operation:
        """
        bkapi resource ipchooser_topo_query_path
        查询多个节点拓扑路径
        """
    @property
    def ipchooser_topo_trees(self) -> Operation:
        """
        bkapi resource ipchooser_topo_trees
        批量获取含各节点主机数量的拓扑树
        """
    @property
    def job_collect_job_log(self) -> Operation:
        """
        bkapi resource job_collect_job_log
        查询日志
        """
    @property
    def job_get_job_commands(self) -> Operation:
        """
        bkapi resource job_get_job_commands
        获取安装命令
        """
    @property
    def job_get_job_log(self) -> Operation:
        """
        bkapi resource job_get_job_log
        查询日志
        """
    @property
    def job_install_job(self) -> Operation:
        """
        bkapi resource job_install_job
        安装类任务
        """
    @property
    def job_list_job(self) -> Operation:
        """
        bkapi resource job_list_job
        查询任务列表
        """
    @property
    def job_operate_job(self) -> Operation:
        """
        bkapi resource job_operate_job
        操作类任务
        """
    @property
    def job_retrieve_job(self) -> Operation:
        """
        bkapi resource job_retrieve_job
        查询任务详情
        """
    @property
    def job_retry_job(self) -> Operation:
        """
        bkapi resource job_retry_job
        重试任务
        """
    @property
    def job_retry_node(self) -> Operation:
        """
        bkapi resource job_retry_node
        原子粒度重试任务
        """
    @property
    def job_revoke_job(self) -> Operation:
        """
        bkapi resource job_revoke_job
        终止任务
        """
    @property
    def list_profile(self) -> Operation:
        """
        bkapi resource list_profile
        查询个性配置
        """
    @property
    def meta_get_filter_condition(self) -> Operation:
        """
        bkapi resource meta_get_filter_condition
        获取过滤条件
        """
    @property
    def meta_job_settings(self) -> Operation:
        """
        bkapi resource meta_job_settings
        任务配置接口
        """
    @property
    def meta_retrieve_global_settings(self) -> Operation:
        """
        bkapi resource meta_retrieve_global_settings
        查询全局配置
        """
    @property
    def permission_fetch_permission(self) -> Operation:
        """
        bkapi resource permission_fetch_permission
        根据条件返回用户权限
        """
    @property
    def permission_list_ap_permission(self) -> Operation:
        """
        bkapi resource permission_list_ap_permission
        返回用户接入点权限
        """
    @property
    def permission_list_cloud_permission(self) -> Operation:
        """
        bkapi resource permission_list_cloud_permission
        返回用户云区域的权限
        """
    @property
    def permission_list_package_permission(self) -> Operation:
        """
        bkapi resource permission_list_package_permission
        返回用户插件包权限
        """
    @property
    def permission_list_plugin_instance_permission(self) -> Operation:
        """
        bkapi resource permission_list_plugin_instance_permission
        返回用户插件实例权限
        """
    @property
    def permission_list_startegy_permission(self) -> Operation:
        """
        bkapi resource permission_list_startegy_permission
        返回用户部署策略权限
        """
    @property
    def plugin_fetch_package_info(self) -> Operation:
        """
        bkapi resource plugin_fetch_package_info
        获取插件包信息
        """
    @property
    def plugin_fetch_version(self) -> Operation:
        """
        bkapi resource plugin_fetch_version
        获取插件最新版本
        """
    @property
    def plugin_list_host(self) -> Operation:
        """
        bkapi resource plugin_list_host
        查询插件列表
        """
    @property
    def plugin_list_package(self) -> Operation:
        """
        bkapi resource plugin_list_package
        查询进程包列表,pk为具体进程名
        """
    @property
    def plugin_list_process(self) -> Operation:
        """
        bkapi resource plugin_list_process
        查询插件列表,pk为official, external 或 scripts
        """
    @property
    def plugin_list_process_status(self) -> Operation:
        """
        bkapi resource plugin_list_process_status
        查询主机进程状态信息
        """
    @property
    def plugin_operate_plugin(self) -> Operation:
        """
        bkapi resource plugin_operate_plugin
        插件操作类任务
        """
    @property
    def plugin_plugin_statistics(self) -> Operation:
        """
        bkapi resource plugin_plugin_statistics
        获取插件统计数据
        """
    @property
    def plugin_v2_create_export_plugin_task(self) -> Operation:
        """
        bkapi resource plugin_v2_create_export_plugin_task
        触发插件打包导出
        """
    @property
    def plugin_v2_create_register_task(self) -> Operation:
        """
        bkapi resource plugin_v2_create_register_task
        创建注册任务
        """
    @property
    def plugin_v2_fetch_config_variables(self) -> Operation:
        """
        bkapi resource plugin_v2_fetch_config_variables
        获取配置模板参数
        """
    @property
    def plugin_v2_fetch_package_deploy_info(self) -> Operation:
        """
        bkapi resource plugin_v2_fetch_package_deploy_info
        获取插件包部署信息
        """
    @property
    def plugin_v2_fetch_resource_policy(self) -> Operation:
        """
        bkapi resource plugin_v2_fetch_resource_policy
        查询资源策略
        """
    @property
    def plugin_v2_fetch_resource_policy_status(self) -> Operation:
        """
        bkapi resource plugin_v2_fetch_resource_policy_status
        查询资源策略状态
        """
    @property
    def plugin_v2_list_plugin(self) -> Operation:
        """
        bkapi resource plugin_v2_list_plugin
        插件列表
        """
    @property
    def plugin_v2_list_plugin_host(self) -> Operation:
        """
        bkapi resource plugin_v2_list_plugin_host
        查询插件下主机
        """
    @property
    def plugin_v2_operate_plugin(self) -> Operation:
        """
        bkapi resource plugin_v2_operate_plugin
        插件操作
        """
    @property
    def plugin_v2_package_status_operation(self) -> Operation:
        """
        bkapi resource plugin_v2_package_status_operation
        插件包状态类操作
        """
    @property
    def plugin_v2_plugin_history(self) -> Operation:
        """
        bkapi resource plugin_v2_plugin_history
        插件包历史
        """
    @property
    def plugin_v2_plugin_parse(self) -> Operation:
        """
        bkapi resource plugin_v2_plugin_parse
        解析插件包
        """
    @property
    def plugin_v2_plugin_status_operation(self) -> Operation:
        """
        bkapi resource plugin_v2_plugin_status_operation
        插件状态类操作
        """
    @property
    def plugin_v2_plugin_upload(self) -> Operation:
        """
        bkapi resource plugin_v2_plugin_upload
        插件上传
        """
    @property
    def plugin_v2_query_export_plugin_task(self) -> Operation:
        """
        bkapi resource plugin_v2_query_export_plugin_task
        获取一个导出任务结果
        """
    @property
    def plugin_v2_query_register_task(self) -> Operation:
        """
        bkapi resource plugin_v2_query_register_task
        查询插件注册任务
        """
    @property
    def plugin_v2_retrieve_plugin(self) -> Operation:
        """
        bkapi resource plugin_v2_retrieve_plugin
        插件详情
        """
    @property
    def plugin_v2_set_resource_policy(self) -> Operation:
        """
        bkapi resource plugin_v2_set_resource_policy
        设置资源策略
        """
    @property
    def plugin_v2_update_plugin(self) -> Operation:
        """
        bkapi resource plugin_v2_update_plugin
        编辑插件
        """
    @property
    def policy_create_policy(self) -> Operation:
        """
        bkapi resource policy_create_policy
        创建策略
        """
    @property
    def policy_fetch_common_variable(self) -> Operation:
        """
        bkapi resource policy_fetch_common_variable
        获取公共变量
        """
    @property
    def policy_fetch_policy_abnormal_info(self) -> Operation:
        """
        bkapi resource policy_fetch_policy_abnormal_info
        获取策略异常信息
        """
    @property
    def policy_fetch_policy_topo(self) -> Operation:
        """
        bkapi resource policy_fetch_policy_topo
        插件策略拓扑
        """
    @property
    def policy_host_policy(self) -> Operation:
        """
        bkapi resource policy_host_policy
        主机策略列表
        """
    @property
    def policy_list_policy(self) -> Operation:
        """
        bkapi resource policy_list_policy
        查询策略列表
        """
    @property
    def policy_migrate_preview(self) -> Operation:
        """
        bkapi resource policy_migrate_preview
        策略执行预览（计算变更详情）
        """
    @property
    def policy_policy_empty(self) -> Operation:
        """
        bkapi resource policy_policy_empty
        empty
        """
    @property
    def policy_policy_info(self) -> Operation:
        """
        bkapi resource policy_policy_info
        策略详细
        """
    @property
    def policy_policy_operate(self) -> Operation:
        """
        bkapi resource policy_policy_operate
        策略操作
        """
    @property
    def policy_policy_preselection(self) -> Operation:
        """
        bkapi resource policy_policy_preselection
        plugin_preselection
        """
    @property
    def policy_policy_preview(self) -> Operation:
        """
        bkapi resource policy_policy_preview
        策略执行预览（预览所选范围）
        """
    @property
    def policy_rollback_preview(self) -> Operation:
        """
        bkapi resource policy_rollback_preview
        策略回滚预览
        """
    @property
    def policy_run_policy(self) -> Operation:
        """
        bkapi resource policy_run_policy
        执行策略
        """
    @property
    def policy_update_policy(self) -> Operation:
        """
        bkapi resource policy_update_policy
        更新策略
        """
    @property
    def policy_update_policy_info(self) -> Operation:
        """
        bkapi resource policy_update_policy_info
        编辑策略概要信息
        """
    @property
    def policy_upgrade_preview(self) -> Operation:
        """
        bkapi resource policy_upgrade_preview
        升级预览
        """
    @property
    def rsa_fetch_public_keys(self) -> Operation:
        """
        bkapi resource rsa_fetch_public_keys
        获取公钥列表
        """
    @property
    def service_info(self) -> Operation:
        """
        bkapi resource service_info
        查询某主机服务信息
        """
    @property
    def subscription_cmdb_subscription(self) -> Operation:
        """
        bkapi resource subscription_cmdb_subscription
        接收cmdb事件回调
        """
    @property
    def subscription_collect_subscription_task_result_detail(self) -> Operation:
        """
        bkapi resource subscription_collect_subscription_task_result_detail
        采集任务执行详细结果
        """
    @property
    def subscription_create_subscription(self) -> Operation:
        """
        bkapi resource subscription_create_subscription
        创建订阅
        """
    @property
    def subscription_delete_subscription(self) -> Operation:
        """
        bkapi resource subscription_delete_subscription
        删除订阅
        """
    @property
    def subscription_fetch_commands(self) -> Operation:
        """
        bkapi resource subscription_fetch_commands
        返回安装命令
        """
    @property
    def subscription_fetch_policy_topo(self) -> Operation:
        """
        bkapi resource subscription_fetch_policy_topo
        插件策略拓扑
        """
    @property
    def subscription_get_gse_config(self) -> Operation:
        """
        bkapi resource subscription_get_gse_config
        获取配置
        """
    @property
    def subscription_list_deploy_policy(self) -> Operation:
        """
        bkapi resource subscription_list_deploy_policy
        查询策略列表
        """
    @property
    def subscription_query_host_policy(self) -> Operation:
        """
        bkapi resource subscription_query_host_policy
        获取主机策略列表
        """
    @property
    def subscription_query_host_subscription_ids(self) -> Operation:
        """
        bkapi resource subscription_query_host_subscription_ids
        获取主机订阅列表
        """
    @property
    def subscription_query_instance_status(self) -> Operation:
        """
        bkapi resource subscription_query_instance_status
        查询订阅运行状态
        """
    @property
    def subscription_report_log(self) -> Operation:
        """
        bkapi resource subscription_report_log
        上报日志
        """
    @property
    def subscription_retry_node(self) -> Operation:
        """
        bkapi resource subscription_retry_node
        重试原子
        """
    @property
    def subscription_retry_subscription(self) -> Operation:
        """
        bkapi resource subscription_retry_subscription
        重试失败的任务
        """
    @property
    def subscription_revoke_subscription(self) -> Operation:
        """
        bkapi resource subscription_revoke_subscription
        终止正在执行的任务
        """
    @property
    def subscription_run_subscription(self) -> Operation:
        """
        bkapi resource subscription_run_subscription
        执行订阅
        """
    @property
    def subscription_search_plugin_policy(self) -> Operation:
        """
        bkapi resource subscription_search_plugin_policy
        获取插件策略信息
        """
    @property
    def subscription_statistic(self) -> Operation:
        """
        bkapi resource subscription_statistic
        统计订阅任务数据
        """
    @property
    def subscription_subscription_check_task_ready(self) -> Operation:
        """
        bkapi resource subscription_subscription_check_task_ready
        查询任务是否已准备完成
        """
    @property
    def subscription_subscription_info(self) -> Operation:
        """
        bkapi resource subscription_subscription_info
        订阅详情
        """
    @property
    def subscription_subscription_switch(self) -> Operation:
        """
        bkapi resource subscription_subscription_switch
        订阅启停
        """
    @property
    def subscription_subscription_task_result(self) -> Operation:
        """
        bkapi resource subscription_subscription_task_result
        任务执行结果
        """
    @property
    def subscription_subscription_task_result_detail(self) -> Operation:
        """
        bkapi resource subscription_subscription_task_result_detail
        任务执行详细结果
        """
    @property
    def subscription_update_subscription(self) -> Operation:
        """
        bkapi resource subscription_update_subscription
        更新订阅
        """
    @property
    def tjj_fetch_pwd(self) -> Operation:
        """
        bkapi resource tjj_fetch_pwd
        查询支持查询密码的主机
        """
    @property
    def update_or_create_profile(self) -> Operation:
        """
        bkapi resource update_or_create_profile
        更新或创建个性配置
        """

class Client(APIGatewayClient):
    """Bkapi bk_nodeman client"""

    @property
    def api(self) -> Group:
        """api resources"""

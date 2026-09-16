# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def networkarea_list(self) -> Operation:
        """
        bkapi resource networkarea_list
        查询网络区域列表
        """
    @property
    def networkunit_list(self) -> Operation:
        """
        bkapi resource networkunit_list
        查询管控单元列表(简要信息)
        """
    @property
    def host_list(self) -> Operation:
        """
        bkapi resource host_list
        查询主机列表
        """
    @property
    def networkunit_recommend(self) -> Operation:
        """
        bkapi resource networkunit_recommend
        按网络段推荐管控单元
        """
    @property
    def package_list(self) -> Operation:
        """
        bkapi resource package_list
        查询安装包版本列表(简要信息)
        """
    @property
    def package_distinct(self) -> Operation:
        """
        bkapi resource package_distinct
        查询安装包版本的 OS 类型去重列表
        """
    @property
    def public_key_get(self) -> Operation:
        """
        bkapi resource public_key_get
        获取 RSA 公钥
        """
    @property
    def node_install_check(self) -> Operation:
        """
        bkapi resource node_install_check
        节点安装前置检查
        """
    @property
    def node_install(self) -> Operation:
        """
        bkapi resource node_install
        节点安装
        """
    @property
    def node_upgrade(self) -> Operation:
        """
        bkapi resource node_upgrade
        节点升级
        """
    @property
    def node_restart(self) -> Operation:
        """
        bkapi resource node_restart
        节点重启
        """
    @property
    def node_reconfig(self) -> Operation:
        """
        bkapi resource node_reconfig
        节点重载配置
        """
    @property
    def node_uninstall(self) -> Operation:
        """
        bkapi resource node_uninstall
        节点卸载
        """
    @property
    def plugin_install(self) -> Operation:
        """
        bkapi resource plugin_install
        插件安装
        """
    @property
    def plugin_uninstall(self) -> Operation:
        """
        bkapi resource plugin_uninstall
        插件卸载
        """
    @property
    def plugin_list(self) -> Operation:
        """
        bkapi resource plugin_list
        查询插件列表
        """
    @property
    def node_workflow_operation_list(self) -> Operation:
        """
        bkapi resource node_workflow_operation_list
        查询节点工作流操作实例列表
        """
    @property
    def plugin_workflow_operation_list(self) -> Operation:
        """
        bkapi resource plugin_workflow_operation_list
        查询插件工作流操作实例列表
        """
    @property
    def node_workflow_operation_instance_log_get(self) -> Operation:
        """
        bkapi resource node_workflow_operation_instance_log_get
        获取节点工作流操作实例日志
        """
    @property
    def plugin_workflow_operation_instance_log_get(self) -> Operation:
        """
        bkapi resource plugin_workflow_operation_instance_log_get
        获取插件工作流操作实例日志
        """


class Client(APIGatewayClient):
    """Bkapi bk-nodemgr client"""

    _api_name = "bk-nodemgr"

    api: Group

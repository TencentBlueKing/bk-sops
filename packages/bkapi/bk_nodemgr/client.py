from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property
from bkapi_client_core.client import RequestContextBuilder


class NodemgrRequestContextBuilder(RequestContextBuilder):
    """Nodemgr 请求上下文构建器。

    与父类唯一区别: 空字典 {} 也作为有效 body 下发, 而不是被 `if not data` 漏掉。
    """

    def build_data(self, context, data=None):
        if data is None:
            return

        if context["method"] in ["GET", "HEAD", "OPTIONS"]:
            params = data.copy()
            params.update(context.get("params") or {})
            context["params"] = params
        else:
            context["json"] = data


class Group(OperationGroup):
    # 查询网络区域列表
    networkarea_list = bind_property(
        Operation,
        name="networkarea_list",
        method="POST",
        path="/api/v3/topo/networkarea/list",
    )

    # 查询管控单元列表(简要信息)
    networkunit_list = bind_property(
        Operation,
        name="networkunit_list",
        method="POST",
        path="/api/v3/topo/networkunit/list/brief",
    )

    # 查询主机列表
    host_list = bind_property(
        Operation,
        name="host_list",
        method="POST",
        path="/api/v3/topo/host/list",
    )

    # 按网络段推荐管控单元
    networkunit_recommend = bind_property(
        Operation,
        name="networkunit_recommend",
        method="POST",
        path="/api/v3/topo/networkunit/recommend_by_network_segment",
    )

    # 查询安装包版本列表(简要信息)
    package_list = bind_property(
        Operation,
        name="package_list",
        method="POST",
        path="/api/v3/package/release/{node_role}/list/brief",
    )

    # 查询安装包版本的 OS 类型去重列表
    package_distinct = bind_property(
        Operation,
        name="package_distinct",
        method="POST",
        path="/api/v3/package/release/{node_role}/distinct",
    )

    # 获取 RSA 公钥
    public_key_get = bind_property(
        Operation,
        name="public_key_get",
        method="POST",
        path="/api/v3/cipher/rsa/get_public_key",
    )

    # 节点安装前置检查
    node_install_check = bind_property(
        Operation,
        name="node_install_check",
        method="POST",
        path="/api/v3/node/{node_role}/install_check",
    )

    # 节点安装
    node_install = bind_property(
        Operation,
        name="node_install",
        method="POST",
        path="/api/v3/node/{node_role}/install",
    )

    # 节点升级
    node_upgrade = bind_property(
        Operation,
        name="node_upgrade",
        method="POST",
        path="/api/v3/node/{node_role}/upgrade",
    )

    # 节点重启
    node_restart = bind_property(
        Operation,
        name="node_restart",
        method="POST",
        path="/api/v3/node/{node_role}/restart",
    )

    # 节点重载配置
    node_reconfig = bind_property(
        Operation,
        name="node_reconfig",
        method="POST",
        path="/api/v3/node/{node_role}/reconfig",
    )

    # 节点卸载
    node_uninstall = bind_property(
        Operation,
        name="node_uninstall",
        method="POST",
        path="/api/v3/node/{node_role}/uninstall",
    )

    # 插件安装
    plugin_install = bind_property(
        Operation,
        name="plugin_install",
        method="POST",
        path="/api/v3/plugin/install",
    )

    # 插件卸载
    plugin_uninstall = bind_property(
        Operation,
        name="plugin_uninstall",
        method="POST",
        path="/api/v3/plugin/uninstall",
    )

    # 查询插件列表
    plugin_list = bind_property(
        Operation,
        name="plugin_list",
        method="POST",
        path="/api/v3/plugin/list",
    )

    # 查询节点工作流操作实例列表
    node_workflow_operation_list = bind_property(
        Operation,
        name="node_workflow_operation_list",
        method="POST",
        path="/api/v3/node/workflow/operation/list",
    )

    # 查询插件工作流操作实例列表
    plugin_workflow_operation_list = bind_property(
        Operation,
        name="plugin_workflow_operation_list",
        method="POST",
        path="/api/v3/plugin/workflow/operation/list",
    )

    # 获取节点工作流操作实例日志
    node_workflow_operation_instance_log_get = bind_property(
        Operation,
        name="node_workflow_operation_instance_log_get",
        method="POST",
        path="/api/v3/node/workflow/operation/instance/log/get",
    )

    # 获取插件工作流操作实例日志
    plugin_workflow_operation_instance_log_get = bind_property(
        Operation,
        name="plugin_workflow_operation_instance_log_get",
        method="POST",
        path="/api/v3/plugin/workflow/operation/instance/log/get",
    )


class Client(APIGatewayClient):
    """Bkapi bk-nodemgr client"""

    _api_name = "bk-nodemgr"
    _build_class = NodemgrRequestContextBuilder

    api = bind_property(Group, name="api")

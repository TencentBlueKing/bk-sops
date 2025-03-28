# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):

    # list_hosts_without_biz
    # 没有业务ID的主机查询
    list_hosts_without_biz = bind_property(
        Operation,
        name="list_hosts_without_biz",
        method="POST",
        path="/api/v3/hosts/list_hosts_without_app",
    )

    # get_mainline_object_topo
    # 查询主线模型的业务拓扑
    get_mainline_object_topo = bind_property(
        Operation,
        name="get_mainline_object_topo",
        method="POST",
        path="/api/v3/find/topomodelmainline",
    )

    # search_biz_inst_topo
    # 查询业务实例拓扑
    search_biz_inst_topo = bind_property(
        Operation,
        name="search_biz_inst_topo",
        method="POST",
        path="/api/v3/find/topoinst/biz/{bk_biz_id}",
    )

    # search_object_attribute
    # 查询对象模型属性
    search_object_attribute = bind_property(
        Operation,
        name="search_object_attribute",
        method="POST",
        path="/api/v3/find/objectattr",
    )

    # create_set
    # 创建集群
    create_set = bind_property(
        Operation,
        name="create_set",
        method="POST",
        path="/api/v3/set/{bk_biz_id}",
    )

    # find_set_batch
    # 批量查询某业务的集群详情
    find_set_batch = bind_property(
        Operation,
        name="find_set_batch",
        method="POST",
        path="/api/v3/findmany/set/bk_biz_id/{bk_biz_id}",
    )

    # list_service_category
    # 查询服务分类列表
    list_service_category = bind_property(
        Operation,
        name="list_service_category",
        method="POST",
        path="/api/v3/findmany/proc/service_category",
    )

    # search_dynamic_group
    # 搜索动态分组
    search_dynamic_group = bind_property(
        Operation,
        name="search_dynamic_group",
        method="POST",
        path="/api/v3/dynamicgroup/search/{bk_biz_id}",
    )

    # get_biz_internal_module
    # 查询业务的空闲机/故障机/待回收模块
    get_biz_internal_module = bind_property(
        Operation,
        name="get_biz_internal_module",
        method="POST",
        path="/api/v3/topo/internal/{bk_supplier_account}/{bk_biz_id}",
    )

    # list_service_template
    # 服务模板列表查询
    list_service_template = bind_property(
        Operation,
        name="list_service_template",
        method="POST",
        path="/api/v3/findmany/proc/service_template",
    )

    # list_set_template
    # 查询集群模板
    list_set_template = bind_property(
        Operation,
        name="list_set_template",
        method="POST",
        path="/v3/findmany/topo/set_template/bk_biz_id/{bk_biz_id}",
    )

    # list_business_set
    # 查询业务集
    list_business_set = bind_property(
        Operation,
        name="list_business_set",
        method="POST",
        path="/api/v3/findmany/biz_set",
    )

    # search_business
    # 查询业务
    search_business = bind_property(
        Operation,
        name="search_business",
        method="POST",
        path="/api/v3/biz/search/{bk_supplier_account}",
    )

    # list_biz_hosts
    # 查询业务下的主机
    list_biz_hosts = bind_property(
        Operation,
        name="list_biz_hosts",
        method="POST",
        path="/api/v3/hosts/app/{bk_biz_id}/list_hosts",
    )

    # list_biz_hosts_topo
    # 查询业务下的主机和拓扑信息
    list_biz_hosts_topo = bind_property(
        Operation,
        name="list_biz_hosts_topo",
        method="POST",
        path="/api/v3/hosts/app/{bk_biz_id}/list_hosts_topo",
    )

    # execute_dynamic_group
    # 执行动态分组
    execute_dynamic_group = bind_property(
        Operation,
        name="execute_dynamic_group",
        method="POST",
        path="/api/v3/dynamicgroup/execute/{bk_biz_id}",
    )

    # find_module_batch
    # 批量查询某业务的模块详情
    find_module_batch = bind_property(
        Operation,
        name="find_module_batch",
        method="POST",
        path="/api/v3/findmany/module/bk_biz_id/{bk_biz_id}",
    )

    # search_set
    # 查询集群
    search_set = bind_property(
        Operation,
        name="search_set",
        method="POST",
        path="/api/v3/set/search/{bk_supplier_account}/{bk_biz_id}",
    )

    # update_set
    # 更新集群
    update_set = bind_property(
        Operation,
        name="update_set",
        method="PUT",
        path="/api/v3/set/{bk_biz_id}/{bk_set_id}",
    )

    # find_module_with_relation
    # 根据条件查询业务下的模块
    find_module_with_relation = bind_property(
        Operation,
        name="find_module_with_relation",
        method="POST",
        path="/api/v3/findmany/module/with_relation/biz/{bk_biz_id}",
    )

    # search_module
    # 查询模块
    search_module = bind_property(
        Operation,
        name="search_module",
        method="POST",
        path="/api/v3/module/search/{bk_supplier_account}/{bk_biz_id}/{bk_set_id}",
    )

    # update_host
    # 更新主机信息
    update_host = bind_property(
        Operation,
        name="update_host",
        method="PUT",
        path="/api/v3/hosts/batch",
    )

    # batch_delete_set
    # 批量删除集群
    batch_delete_set = bind_property(
        Operation,
        name="batch_delete_set",
        method="DELETE",
        path="/api/v3/set/{bk_biz_id}/batch",
    )

    # create_module
    # 创建模块
    create_module = bind_property(
        Operation,
        name="create_module",
        method="POST",
        path="/api/v3/module/{bk_biz_id}/{bk_set_id}",
    )

    # update_module
    # 更新模块
    update_module = bind_property(
        Operation,
        name="update_module",
        method="PUT",
        path="/api/v3/module/{bk_biz_id}/{bk_set_id}/{bk_module_id}",
    )

    # find_host_by_topo
    # 查询拓扑节点下的主机
    find_host_by_topo = bind_property(
       Operation,
        name="find_host_by_topo",
        method="POST",
        path="/api/v3/findmany/hosts/by_topo/biz/{bk_biz_id}",
    )

    # get_host_base_info
    # 查询主机基础信息
    get_host_base_info = bind_property(
        Operation,
        name="get_host_base_info",
        method="GET",
        path="/api/v3/hosts/{bk_supplier_account}/{bk_host_id}",
    )

    # add_host_lock
    # 新加主机锁
    add_host_lock = bind_property(
        Operation,
        name="add_host_lock",
        method="POST",
        path="/api/v3/host/lock",
    )

    # delete_host_lock
    # 删除主机锁
    delete_host_lock = bind_property(
        Operation,
        name="delete_host_lock",
        method="DELETE",
        path="/api/v3/host/lock",
    )

    # search_host_lock
    # 查询主机锁
    search_host_lock = bind_property(
        Operation,
        name="search_host_lock",
        method="POST",
        path="/api/v3/host/lock/search",
    )

    # transfer_host_module
    # 业务内主机转移模块
    transfer_host_module = bind_property(
        Operation,
        name="transfer_host_module",
        method="POST",
        path="/api/v3/hosts/modules",
    )

    # transfer_host_to_idlemodule
    # 上交主机到业务的空闲机模块
    transfer_host_to_idlemodule = bind_property(
        Operation,
        name="transfer_host_to_idlemodule",
        method="POST",
        path="/api/v3/hosts/modules/idle",
    )

    # transfer_host_to_recyclemodule
    # 上交主机到业务的待回收模块
    transfer_host_to_recyclemodule = bind_property(
        Operation,
        name="transfer_host_to_recyclemodule",
        method="POST",
        path="/api/v3/hosts/modules/recycle",
    )

    # transfer_host_to_faultmodule
    # 上交主机到业务的故障机模块
    transfer_host_to_faultmodule = bind_property(
        Operation,
        name="transfer_host_to_faultmodule",
        method="POST",
        path="/api/v3/hosts/modules/fault",
    )

    # transfer_host_to_resourcemodule
    # 上交主机至资源池
    transfer_host_to_resourcemodule = bind_property(
        Operation,
        name="transfer_host_to_resourcemodule",
        method="POST",
        path="/api/v3/hosts/modules/resource",
    )

    # transfer_sethost_to_idle_module
    # 清空业务下集群/模块中主机
    transfer_sethost_to_idle_module = bind_property(
        Operation,
        name="transfer_sethost_to_idle_module",
        method="POST",
        path="/api/v3/hosts/modules/idle/set",
    )

    # batch_update_host
    # 批量更新主机信息
    batch_update_host = bind_property(
        Operation,
        name="batch_update_host",
        method="PUT",
        path="/api/v3/hosts/property/batch",
    )

    # search_cloud_area
    # 查询管控区域
    search_cloud_area = bind_property(
        Operation,
        name="search_cloud_area",
        method="POST",
        path="/api/v3/findmany/cloudarea",
    )


class Client(APIGatewayClient):
    """Bkapi bk_cmdb client"""

    _api_name = "bk-cmdb"

    api = bind_property(Group, name="api")

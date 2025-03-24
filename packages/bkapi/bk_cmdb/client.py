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

    # find_host_by_topo
    # 查询拓扑节点下的主机
    find_host_by_topo = bind_property(
       Operation,
        name="find_host_by_topo",
        method="POST",
        path="/api/v3/findmany/hosts/by_topo/biz/{bk_biz_id}",
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


class Client(APIGatewayClient):
    """Bkapi bk_cmdb client"""

    _api_name = "bk-cmdb"

    api = bind_property(Group, name="api")

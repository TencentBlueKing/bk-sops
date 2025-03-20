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




class Client(APIGatewayClient):
    """Bkapi bk_cmdb client"""

    _api_name = "bk-cmdb"

    api = bind_property(Group, name="api")

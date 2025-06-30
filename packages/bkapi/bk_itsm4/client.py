# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource action_components_callback
    # 动作回调
    action_components_callback = bind_property(
        Operation,
        name="action_components_callback",
        method="POST",
        path="/api/v1/action_components/callback/",
    )

    # bkapi resource category_groups
    # 工单分组分类标识
    category_groups = bind_property(
        Operation,
        name="category_groups",
        method="GET",
        path="/openapi/v2/ticket_search/category_groups/",
    )

    # bkapi resource create_ticket
    # 创建工单
    create_ticket = bind_property(
        Operation,
        name="create_ticket",
        method="POST",
        path="/api/v1/ticket/create/",
    )

    # bkapi resource create_ticket_comment
    # 创建工单评论
    create_ticket_comment = bind_property(
        Operation,
        name="create_ticket_comment",
        method="POST",
        path="/openapi/v2/ticket_comment/",
    )

    # bkapi resource download_file
    # 下载文件
    download_file = bind_property(
        Operation,
        name="download_file",
        method="GET",
        path="/openapi/v2/file/download/",
    )

    # bkapi resource file_upload
    # 上传附件
    file_upload = bind_property(
        Operation,
        name="file_upload",
        method="POST",
        path="/api/v1/file/upload/",
    )

    # bkapi resource flex_ticket_sync
    # get ticket list
    flex_ticket_sync = bind_property(
        Operation,
        name="flex_ticket_sync",
        method="GET",
        path="/openapi/v2/flex/ticket_sync/",
    )

    # bkapi resource flex_ticket_sync_with_token
    # get ticket list with token
    flex_ticket_sync_with_token = bind_property(
        Operation,
        name="flex_ticket_sync_with_token",
        method="GET",
        path="/openapi/v2/flex/ticket_sync_with_token/",
    )

    # bkapi resource full_text_search
    # 工单高级查询
    full_text_search = bind_property(
        Operation,
        name="full_text_search",
        method="POST",
        path="/openapi/v2/ticket_search/full_text_search/",
    )

    # bkapi resource handle_ticket
    # 处理工单流转
    handle_ticket = bind_property(
        Operation,
        name="handle_ticket",
        method="POST",
        path="/openapi/v2/tickets/{ticket_id}/handle/",
    )

    # bkapi resource list_services
    # 服务列表
    list_services = bind_property(
        Operation,
        name="list_services",
        method="GET",
        path="/openapi/v2/catalog_services/catalog_services_tree/",
    )

    # bkapi resource list_ticket
    # 工单列表
    list_ticket = bind_property(
        Operation,
        name="list_ticket",
        method="GET",
        path="/openapi/v2/tickets/",
    )

    # bkapi resource openapi_sops_components_callback
    # 标准运维节点回调
    openapi_sops_components_callback = bind_property(
        Operation,
        name="openapi_sops_components_callback",
        method="POST",
        path="/openapi/v1/sops_components/callback/",
    )

    # bkapi resource option_list
    # 工单选项
    option_list = bind_property(
        Operation,
        name="option_list",
        method="POST",
        path="/openapi/v2/option_manager/option_list/",
    )

    # bkapi resource portal_items
    # 门户列表
    portal_items = bind_property(
        Operation,
        name="portal_items",
        method="GET",
        path="/openapi/v2/portal/items/",
    )

    # bkapi resource retrieve_ticket_detail
    # retrieve ticket detail
    retrieve_ticket_detail = bind_property(
        Operation,
        name="retrieve_ticket_detail",
        method="GET",
        path="/openapi/v2/flex/ticket/{ticket_id}/",
    )

    # bkapi resource retrieve_ticket_info
    # retrieve ticket info
    retrieve_ticket_info = bind_property(
        Operation,
        name="retrieve_ticket_info",
        method="GET",
        path="/openapi/v2/tickets/{ticket_id}/",
    )

    # bkapi resource system_create
    # 创建系统
    system_create = bind_property(
        Operation,
        name="system_create",
        method="POST",
        path="/api/v1/system/create/",
    )

    # bkapi resource system_delete
    # 删除系统
    system_delete = bind_property(
        Operation,
        name="system_delete",
        method="POST",
        path="/api/v1/system/delete/",
    )

    # bkapi resource system_ticket_list
    # 工单列表
    system_ticket_list = bind_property(
        Operation,
        name="system_ticket_list",
        method="GET",
        path="/api/v1/system_ticket/list/",
    )

    # bkapi resource system_todo
    # 创建系统待办
    system_todo = bind_property(
        Operation,
        name="system_todo",
        method="POST",
        path="/api/v1/system/todo/",
    )

    # bkapi resource system_update
    # 更新系统
    system_update = bind_property(
        Operation,
        name="system_update",
        method="POST",
        path="/api/v1/system/update/",
    )

    # bkapi resource system_workflow_create
    # 创建系统流程
    system_workflow_create = bind_property(
        Operation,
        name="system_workflow_create",
        method="POST",
        path="/api/v1/system_workflow/create/",
    )

    # bkapi resource system_workflow_delete
    # 删除系统流程
    system_workflow_delete = bind_property(
        Operation,
        name="system_workflow_delete",
        method="POST",
        path="/api/v1/system_workflow/delete/",
    )

    # bkapi resource system_workflow_list
    # 系统流程列表
    system_workflow_list = bind_property(
        Operation,
        name="system_workflow_list",
        method="GET",
        path="/api/v1/system_workflow/list/",
    )

    # bkapi resource system_workflow_update
    # 更新系统流程
    system_workflow_update = bind_property(
        Operation,
        name="system_workflow_update",
        method="POST",
        path="/api/v1/system_workflow/update/",
    )

    # bkapi resource ticket_comment_list
    # 工单评论列表
    ticket_comment_list = bind_property(
        Operation,
        name="ticket_comment_list",
        method="GET",
        path="/openapi/v2/ticket_comment/",
    )

    # bkapi resource ticket_create
    # 工单创建
    ticket_create = bind_property(
        Operation,
        name="ticket_create",
        method="POST",
        path="/api/v1/ticket/create/",
    )

    # bkapi resource ticket_detail
    # 工单详情
    ticket_detail = bind_property(
        Operation,
        name="ticket_detail",
        method="GET",
        path="/api/v1/ticket/detail/",
    )

    # bkapi resource ticket_header_fields
    # 获取工单分组字段配置
    ticket_header_fields = bind_property(
        Operation,
        name="ticket_header_fields",
        method="GET",
        path="/openapi/v2/ticket_header/ticket_header_fields/",
    )

    # bkapi resource ticket_list
    # 工单列表
    ticket_list = bind_property(
        Operation,
        name="ticket_list",
        method="GET",
        path="/api/v1/ticket/list/",
    )

    # bkapi resource ticket_logs
    # 查看工单日志
    ticket_logs = bind_property(
        Operation,
        name="ticket_logs",
        method="GET",
        path="/openapi/v2/ticket_logs/",
    )

    # bkapi resource ticket_options
    # 获取表单下拉框数据
    ticket_options = bind_property(
        Operation,
        name="ticket_options",
        method="GET",
        path="/openapi/v2/tickets/options/",
    )

    # bkapi resource ticket_todo_callback_approve
    ticket_todo_callback_approve = bind_property(
        Operation,
        name="ticket_todo_callback_approve",
        method="POST",
        path="/openapi/v2/ticket_tool/{ticket_tool_id}/approve/",
    )

    # bkapi resource ticket_todo_callback_summary
    ticket_todo_callback_summary = bind_property(
        Operation,
        name="ticket_todo_callback_summary",
        method="GET",
        path="/openapi/v2/ticket_tool/{ticket_tool_id}/summary/",
    )

    # bkapi resource upload_file
    # 上传文件
    upload_file = bind_property(
        Operation,
        name="upload_file",
        method="POST",
        path="/openapi/v2/file/upload/",
    )

    # bkapi resource workflow_list
    # 流程列表
    workflow_list = bind_property(
        Operation,
        name="workflow_list",
        method="GET",
        path="/openapi/v2/workflow/",
    )

    system_migrate = bind_property(
        Operation,
        name="system_migrate",
        method="POST",
        path="/api/v1/system/migrate/",
    )

    handle_approval_node = bind_property(
        Operation,
        name="handle_approval_node",
        method="POST",
        path="/api/v1/handle_approval_node/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_itsm4 client"""

    _api_name = "bk-itsm4"

    api = bind_property(Group, name="api")

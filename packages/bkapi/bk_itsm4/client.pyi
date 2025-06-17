# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def action_components_callback(self) -> Operation:
        """
        bkapi resource action_components_callback
        动作回调
        """
    @property
    def category_groups(self) -> Operation:
        """
        bkapi resource category_groups
        工单分组分类标识
        """
    @property
    def create_ticket(self) -> Operation:
        """
        bkapi resource create_ticket
        创建工单
        """
    @property
    def create_ticket_comment(self) -> Operation:
        """
        bkapi resource create_ticket_comment
        创建工单评论
        """
    @property
    def download_file(self) -> Operation:
        """
        bkapi resource download_file
        下载文件
        """
    @property
    def file_upload(self) -> Operation:
        """
        bkapi resource file_upload
        上传附件
        """
    @property
    def flex_ticket_sync(self) -> Operation:
        """
        bkapi resource flex_ticket_sync
        get ticket list
        """
    @property
    def flex_ticket_sync_with_token(self) -> Operation:
        """
        bkapi resource flex_ticket_sync_with_token
        get ticket list with token
        """
    @property
    def full_text_search(self) -> Operation:
        """
        bkapi resource full_text_search
        工单高级查询
        """
    @property
    def handle_ticket(self) -> Operation:
        """
        bkapi resource handle_ticket
        处理工单流转
        """
    @property
    def list_services(self) -> Operation:
        """
        bkapi resource list_services
        服务列表
        """
    @property
    def list_ticket(self) -> Operation:
        """
        bkapi resource list_ticket
        工单列表
        """
    @property
    def openapi_sops_components_callback(self) -> Operation:
        """
        bkapi resource openapi_sops_components_callback
        标准运维节点回调
        """
    @property
    def option_list(self) -> Operation:
        """
        bkapi resource option_list
        工单选项
        """
    @property
    def portal_items(self) -> Operation:
        """
        bkapi resource portal_items
        门户列表
        """
    @property
    def retrieve_ticket_detail(self) -> Operation:
        """
        bkapi resource retrieve_ticket_detail
        retrieve ticket detail
        """
    @property
    def retrieve_ticket_info(self) -> Operation:
        """
        bkapi resource retrieve_ticket_info
        retrieve ticket info
        """
    @property
    def system_create(self) -> Operation:
        """
        bkapi resource system_create
        创建系统
        """
    @property
    def system_delete(self) -> Operation:
        """
        bkapi resource system_delete
        删除系统
        """
    @property
    def system_ticket_list(self) -> Operation:
        """
        bkapi resource system_ticket_list
        工单列表
        """
    @property
    def system_todo(self) -> Operation:
        """
        bkapi resource system_todo
        创建系统待办
        """
    @property
    def system_update(self) -> Operation:
        """
        bkapi resource system_update
        更新系统
        """
    @property
    def system_workflow_create(self) -> Operation:
        """
        bkapi resource system_workflow_create
        创建系统流程
        """
    @property
    def system_workflow_delete(self) -> Operation:
        """
        bkapi resource system_workflow_delete
        删除系统流程
        """
    @property
    def system_workflow_list(self) -> Operation:
        """
        bkapi resource system_workflow_list
        系统流程列表
        """
    @property
    def system_workflow_update(self) -> Operation:
        """
        bkapi resource system_workflow_update
        更新系统流程
        """
    @property
    def ticket_comment_list(self) -> Operation:
        """
        bkapi resource ticket_comment_list
        工单评论列表
        """
    @property
    def ticket_create(self) -> Operation:
        """
        bkapi resource ticket_create
        工单创建
        """
    @property
    def ticket_detail(self) -> Operation:
        """
        bkapi resource ticket_detail
        工单详情
        """
    @property
    def ticket_header_fields(self) -> Operation:
        """
        bkapi resource ticket_header_fields
        获取工单分组字段配置
        """
    @property
    def ticket_list(self) -> Operation:
        """
        bkapi resource ticket_list
        工单列表
        """
    @property
    def ticket_logs(self) -> Operation:
        """
        bkapi resource ticket_logs
        查看工单日志
        """
    @property
    def ticket_options(self) -> Operation:
        """
        bkapi resource ticket_options
        获取表单下拉框数据
        """
    @property
    def ticket_todo_callback_approve(self) -> Operation:
        """
        bkapi resource ticket_todo_callback_approve
        """
    @property
    def ticket_todo_callback_summary(self) -> Operation:
        """
        bkapi resource ticket_todo_callback_summary
        """
    @property
    def upload_file(self) -> Operation:
        """
        bkapi resource upload_file
        上传文件
        """
    @property
    def workflow_list(self) -> Operation:
        """
        bkapi resource workflow_list
        流程列表
        """

class Client(APIGatewayClient):
    """Bkapi bk_itsm4 client"""

    @property
    def api(self) -> OperationGroup:
        """api resources"""

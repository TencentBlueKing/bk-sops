# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def access_overview(self) -> Operation:
        """
        bkapi resource access_overview
        业务接入情况概览
        """
    @property
    def config_template_list(self) -> Operation:
        """
        bkapi resource config_template_list
        获取配置模板列表

        配置模板（ConfigTemplate）
        """
    @property
    def create_job(self) -> Operation:
        """
        bkapi resource create_job
        创建任务

        任务（Job）
        """
    @property
    def flush_process(self) -> Operation:
        """
        bkapi resource flush_process
        刷新业务进程缓存
        """
    @property
    def gray_build(self) -> Operation:
        """
        bkapi resource gray_build
        GSE 2.0灰度
        """
    @property
    def gray_info(self) -> Operation:
        """
        bkapi resource gray_info
        获取GSE 2.0灰度信息
        """
    @property
    def gray_rollback(self) -> Operation:
        """
        bkapi resource gray_rollback
        GSE 2.0灰度回滚
        """
    @property
    def job_status(self) -> Operation:
        """
        bkapi resource job_status
        任务状态查询

        任务（Job）
        """
    @property
    def process_status(self) -> Operation:
        """
        bkapi resource process_status
        进程状态列表
        """
    @property
    def sync_process_status(self) -> Operation:
        """
        bkapi resource sync_process_status
        同步进程状态
        """

class Client(APIGatewayClient):
    """Bkapi bk_gsekit client"""

    @property
    def api(self) -> OperationGroup:
        """api resources"""

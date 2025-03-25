# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource access_overview
    # 业务接入情况概览
    access_overview = bind_property(
        Operation,
        name="access_overview",
        method="GET",
        path="/api/{bk_biz_id}/meta/access_overview/",
    )

    # bkapi resource config_template_list
    # 获取配置模板列表
    #
    # 配置模板（ConfigTemplate）
    config_template_list = bind_property(
        Operation,
        name="config_template_list",
        method="GET",
        path="/api/{bk_biz_id}/config_template/",
    )

    # bkapi resource create_job
    # 创建任务
    #
    # 任务（Job）
    create_job = bind_property(
        Operation,
        name="create_job",
        method="POST",
        path="/api/{bk_biz_id}/job/",
    )

    # bkapi resource flush_process
    # 刷新业务进程缓存
    flush_process = bind_property(
        Operation,
        name="flush_process",
        method="POST",
        path="/api/{bk_biz_id}/process/flush_process/",
    )

    # bkapi resource gray_build
    # GSE 2.0灰度
    gray_build = bind_property(
        Operation,
        name="gray_build",
        method="POST",
        path="/api/core/gray/build/",
    )

    # bkapi resource gray_info
    # 获取GSE 2.0灰度信息
    gray_info = bind_property(
        Operation,
        name="gray_info",
        method="GET",
        path="/api/core/gray/info/",
    )

    # bkapi resource gray_rollback
    # GSE 2.0灰度回滚
    gray_rollback = bind_property(
        Operation,
        name="gray_rollback",
        method="POST",
        path="/api/core/gray/rollback/",
    )

    # bkapi resource job_status
    # 任务状态查询
    #
    # 任务（Job）
    job_status = bind_property(
        Operation,
        name="job_status",
        method="POST",
        path="/api/{bk_biz_id}/job/{id}/job_status/",
    )

    # bkapi resource process_status
    # 进程状态列表
    process_status = bind_property(
        Operation,
        name="process_status",
        method="POST",
        path="/api/{bk_biz_id}/process/process_status/",
    )

    # bkapi resource sync_process_status
    # 同步进程状态
    sync_process_status = bind_property(
        Operation,
        name="sync_process_status",
        method="POST",
        path="/api/{bk_biz_id}/process/sync_process_status/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_gsekit client"""

    _api_name = "bk-gsekit"

    api = bind_property(Group, name="api")

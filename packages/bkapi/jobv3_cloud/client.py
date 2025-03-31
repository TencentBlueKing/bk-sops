# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # 根据ip列表批量查询作业执行日志
    batch_get_job_instance_ip_log = bind_property(
        Operation,
        name="batch_get_job_instance_ip_log",
        method="POST",
        path="/api/v3/batch_get_job_instance_ip_log/",
    )

    # 启动作业执行方案
    execute_job_plan = bind_property(
        Operation,
        name="execute_job_plan",
        method="POST",
        path="/api/v3/system/execute_job_plan/",
    )

    # 快速执行脚本
    fast_execute_script = bind_property(
        Operation,
        name="fast_execute_script",
        method="POST",
        path="/api/v3/system/fast_execute_script/",
    )

    # 快速执行SQL脚本
    fast_execute_sql = bind_property(
        Operation,
        name="fast_execute_sql",
        method="POST",
        path="/api/v3/fast_execute_sql/",
    )

    # 快速分发文件
    fast_transfer_file = bind_property(
        Operation,
        name="fast_transfer_file",
        method="POST",
        path="/api/v3/system/fast_transfer_file/",
    )

    # 查询业务下用户有权限的执行账号列表
    get_account_list = bind_property(
        Operation,
        name="get_account_list",
        method="GET",
        path="/api/v3/system/get_account_list/",
    )

    # 查询定时作业详情
    get_cron_detail = bind_property(
        Operation,
        name="get_cron_detail",
        method="GET",
        path="/api/v3/get_cron_detail/",
    )

    # 查询业务下定时作业信息
    get_cron_list = bind_property(
        Operation,
        name="get_cron_list",
        method="GET",
        path="/api/v3/get_cron_list/",
    )

    # 获取作业实例全局变量的值
    get_job_instance_global_var_value = bind_property(
        Operation,
        name="get_job_instance_global_var_value",
        method="GET",
        path="/api/v3/system/get_job_instance_global_var_value/",
    )

    # 根据ip查询作业执行日志
    get_job_instance_ip_log = bind_property(
        Operation,
        name="get_job_instance_ip_log",
        method="GET",
        path="/api/v3/system/get_job_instance_ip_log/",
    )

    # 查询作业实例列表（执行历史)
    get_job_instance_list = bind_property(
        Operation,
        name="get_job_instance_list",
        method="GET",
        path="/api/v3/system/get_job_instance_list/",
    )

    # 根据作业实例 ID 查询作业执行状态
    get_job_instance_status = bind_property(
        Operation,
        name="get_job_instance_status",
        method="GET",
        path="/api/v3/system/get_job_instance_status/",
    )

    # 根据作业执行方案 ID 查询作业执行方案详情
    get_job_plan_detail = bind_property(
        Operation,
        name="get_job_plan_detail",
        method="GET",
        path="/api/v3/system/get_job_plan_detail/",
    )

    # 查询执行方案列表
    get_job_plan_list = bind_property(
        Operation,
        name="get_job_plan_list",
        method="GET",
        path="/api/v3/system/get_job_plan_list/",
    )

    # 查询作业模版列表
    get_job_template_list = bind_property(
        Operation,
        name="get_job_template_list",
        method="GET",
        path="/api/v3/system/get_job_template_list/",
    )

    # 查询公共脚本列表
    get_public_script_list = bind_property(
        Operation,
        name="get_public_script_list",
        method="GET",
        path="/api/v3/system/get_public_script_list/",
    )

    # 查询公共脚本版本详情
    get_public_script_version_detail = bind_property(
        Operation,
        name="get_public_script_version_detail",
        method="GET",
        path="/api/v3/get_public_script_version_detail/",
    )

    # 查询公共脚本版本列表
    get_public_script_version_list = bind_property(
        Operation,
        name="get_public_script_version_list",
        method="GET",
        path="/api/v3/get_public_script_version_list/",
    )

    # 查询业务脚本列表
    get_script_list = bind_property(
        Operation,
        name="get_script_list",
        method="GET",
        path="/api/v3/system/get_script_list/",
    )

    # 查询业务脚本版本详情
    get_script_version_detail = bind_property(
        Operation,
        name="get_script_version_detail",
        method="GET",
        path="/api/v3/system/get_script_version_detail/",
    )

    # 查询业务脚本版本列表
    get_script_version_list = bind_property(
        Operation,
        name="get_script_version_list",
        method="GET",
        path="/api/v3/system/get_script_version_list/",
    )

    # 用于对执行的作业实例进行操作
    operate_job_instance = bind_property(
        Operation,
        name="operate_job_instance",
        method="POST",
        path="/api/v3/operate_job_instance/",
    )

    # 用于对执行的实例的步骤进行操作
    operate_step_instance = bind_property(
        Operation,
        name="operate_step_instance",
        method="POST",
        path="/api/v3/operate_step_instance/",
    )

    # 分发配置文件，此接口用于分发配置文件等小的纯文本文件
    push_config_file = bind_property(
        Operation,
        name="push_config_file",
        method="POST",
        path="/api/v3/system/push_config_file/",
    )

    # 新建或保存定时作业；新建定时作业，定时任务状态默认为暂停。
    save_cron = bind_property(
        Operation,
        name="save_cron",
        method="POST",
        path="/api/v3/system/save_cron/",
    )

    # 更新定时作业状态，如启动或暂停
    update_cron_status = bind_property(
        Operation,
        name="update_cron_status",
        method="POST",
        path="/api/v3/system/update_cron_status/",
    )

    # 快速执行脚本。建议使用fast_execute_script替换该API !!!
    v2_fast_execute_script = bind_property(
        Operation,
        name="v2_fast_execute_script",
        method="POST",
        path="/api/v2/fast_execute_script/",
    )

    # 根据作业实例ID查询作业执行日志。建议使用get_job_instance_ip_log替换该API !!!
    v2_get_job_instance_log = bind_property(
        Operation,
        name="v2_get_job_instance_log",
        method="GET",
        path="/api/v2/system/get_job_instance_log/",
    )

    # 根据作业实例 ID 查询作业执行状态。建议使用get_job_instance_status替换该API !!!
    v2_get_job_instance_status = bind_property(
        Operation,
        name="v2_get_job_instance_status",
        method="GET",
        path="/api/v2/get_job_instance_status/",
    )

    # 获取用户有权限的业务列表
    get_business_list = bind_property(
        Operation,
        name="get_business_list",
        method="GET",
        path="/api/v3/get_business_list/",
    )

    # 新建凭证
    create_credential = bind_property(
        Operation, name="create_credential", method="POST", path="/api/v3/system/create_credential"
    )

    # 创建文件源
    create_file_source = bind_property(
        Operation, name="create_file_source", method="POST", path="/api/v3/system/create_file_source/"
    )


class Client(APIGatewayClient):
    """Bkapi bk-job client"""

    _api_name = "bk-job"

    api = bind_property(Group, name="api")

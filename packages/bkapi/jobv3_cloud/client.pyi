# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def batch_get_job_instance_ip_log(self) -> Operation:
        """
        根据ip列表批量查询作业执行日志
        """
    @property
    def execute_job_plan(self) -> Operation:
        """
        启动作业执行方案
        """
    @property
    def fast_execute_script(self) -> Operation:
        """
        快速执行脚本
        """
    @property
    def fast_execute_sql(self) -> Operation:
        """
        快速执行SQL脚本
        """
    @property
    def fast_transfer_file(self) -> Operation:
        """
        快速分发文件
        """
    @property
    def get_account_list(self) -> Operation:
        """
        查询业务下用户有权限的执行账号列表
        """
    @property
    def get_cron_detail(self) -> Operation:
        """
        查询定时作业详情
        """
    @property
    def get_cron_list(self) -> Operation:
        """
        查询业务下定时作业信息
        """
    @property
    def get_job_instance_global_var_value(self) -> Operation:
        """
        获取作业实例全局变量的值
        """
    @property
    def get_job_instance_ip_log(self) -> Operation:
        """
        根据ip查询作业执行日志
        """
    @property
    def get_job_instance_list(self) -> Operation:
        """
        查询作业实例列表（执行历史)
        """
    @property
    def get_job_instance_status(self) -> Operation:
        """
        根据作业实例 ID 查询作业执行状态
        """
    @property
    def get_job_plan_detail(self) -> Operation:
        """
        根据作业执行方案 ID 查询作业执行方案详情
        """
    @property
    def get_job_plan_list(self) -> Operation:
        """
        查询执行方案列表
        """
    @property
    def get_job_template_list(self) -> Operation:
        """
        查询作业模版列表
        """
    @property
    def get_public_script_list(self) -> Operation:
        """
        查询公共脚本列表
        """
    @property
    def get_public_script_version_detail(self) -> Operation:
        """
        查询公共脚本版本详情
        """
    @property
    def get_public_script_version_list(self) -> Operation:
        """
        查询公共脚本版本列表
        """
    @property
    def get_script_list(self) -> Operation:
        """
        查询业务脚本列表
        """
    @property
    def get_script_version_detail(self) -> Operation:
        """
        查询业务脚本版本详情
        """
    @property
    def get_script_version_list(self) -> Operation:
        """
        查询业务脚本版本列表
        """
    @property
    def operate_job_instance(self) -> Operation:
        """
        用于对执行的作业实例进行操作
        """
    @property
    def operate_step_instance(self) -> Operation:
        """
        用于对执行的实例的步骤进行操作
        """
    @property
    def push_config_file(self) -> Operation:
        """
        分发配置文件，此接口用于分发配置文件等小的纯文本文件
        """
    @property
    def save_cron(self) -> Operation:
        """
        新建或保存定时作业；新建定时作业，定时任务状态默认为暂停。
        """
    @property
    def update_cron_status(self) -> Operation:
        """
        更新定时作业状态，如启动或暂停
        """
    @property
    def v2_fast_execute_script(self) -> Operation:
        """
        快速执行脚本。建议使用fast_execute_script替换该API !!!
        """
    @property
    def v2_get_job_instance_log(self) -> Operation:
        """
        根据作业实例ID查询作业执行日志。建议使用get_job_instance_ip_log替换该API !!!
        """
    @property
    def v2_get_job_instance_status(self) -> Operation:
        """
        根据作业实例 ID 查询作业执行状态。建议使用get_job_instance_status替换该API !!!
        """

class Client(APIGatewayClient):
    """jobv3-cloud
    作业平台V3版本-内部上云版
    """

    @property
    def api(self) -> Group:
        """api resources"""

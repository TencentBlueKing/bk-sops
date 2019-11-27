# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.translation import ugettext_lazy as _

# 模板类型
TASK_CATEGORY = (
    ('OpsTools', _("运维工具")),
    ('MonitorAlarm', _("监控告警")),
    ('ConfManage', _("配置管理")),
    ('DevTools', _("开发工具")),
    ('EnterpriseIT', _("企业IT")),
    ('OfficeApp', _("办公应用")),
    ('Other', _("其它")),
)

# 任务流程类型
TASK_FLOW_TYPE = [
    ('common', _("默认任务流程")),
    ('common_func', _("职能化任务流程")),
]

# 任务流程对应的步骤
# NOTE：该变量用于模板和任务授权，如果有变更请务必 makemigrations tasktmpl
TASK_FLOW = {
    'common': [
        ('select_steps', _("步骤选择")),  # 创建时即完成该阶段
        ('fill_params', _("参数填写")),  # 创建时即完成该阶段
        ('execute_task', _("任务执行")),
        ('finished', _("完成")),  # 不显示在前端任务流程页面
    ],
    'common_func': [
        ('select_steps', _("步骤选择")),  # 创建时即完成该阶段
        ('func_submit', _("提交需求")),  # 创建时即完成该阶段
        ('func_claim', _("职能化认领")),
        ('execute_task', _("任务执行")),
        ('finished', _("完成")),  # 不显示在前端任务流程页面
    ]
}

# 任务可操作的类型
TASKENGINE_OPERATE_TYPE = {
    'start_task': 'create',
    'suspend_task': 'pause',
    'resume_task': 'resume',
    'retry_step': 'retry_step_by_id',
    'revoke_task': 'revoke',
    'callback_task': 'callback_task',
    'resume_step': 'resume_step_by_id',
    'complete_step': 'complete_step_by_id',
    'reset_step': 'supersede_step_by_id',
}

# 任务时间类型
TAG_EXECUTE_TIME_TYPES = [
    {"id": 'task_prepare', 'text': _("任务准备")},
    {"id": 'doing_work', 'text': _("操作执行")},
    {"id": 'db_alter', 'text': _("DB变更")},
    {"id": 'db_backup', 'text': _("DB备份")},
    {"id": 'online_test', 'text': _("现网测试")},
    {"id": 'idle_time', 'text': _("空闲时间")},
]

# 通知方式
NOTIFY_TYPE = [
    ("weixin", _("微信")),
    ("sms", _("短信")),
    ("email", _("邮件")),
    ("voice", _("语音")),
]

TEMPLATE_NAME_MAX_LENGTH = 50
TEMPLATE_NODE_NAME_MAX_LENGTH = 50
TASK_NAME_MAX_LENGTH = 100
PERIOD_TASK_NAME_MAX_LENGTH = 50


# 数据分析相关内容
class AnalysisElement(object):
    id = 'id'
    category = 'category'
    project__name = 'project__name'
    project_id = 'project_id'
    state = 'status'
    atom_cite = 'atom_cite'
    atom_template = 'atom_template'
    atom_execute = 'atom_execute'
    atom_execute_times = 'atom_execute_times'
    atom_execute_fail_times = 'atom_execute_fail_times'
    atom_avg_execute_time = 'atom_avg_execute_time'
    atom_fail_percent = 'atom_fail_percent'
    atom_instance = 'atom_instance'
    template_node = 'template_node'
    template_cite = 'template_cite'
    instance_node = 'instance_node'
    instance_details = 'instance_details'
    appmaker_instance = 'appmaker_instance'
    create_method = 'create_method'
    flow_type = 'flow_type'
    app_maker = 'app_maker'
    biz_cc_id = 'biz_cc_id'
    order_by = 'order_by'
    instance_time = 'instance_time'
    pipeline_template__name = 'pipeline_template__name'
    pipeline_template__editor = 'pipeline_template__editor'
    pipeline_template__edit_time = 'pipeline_template__edit_time'
    type = 'type'
    group_list = ['category',
                  'project_id',
                  'atom_template',
                  'atom_execute',
                  'atom_execute_fail_times',
                  'atom_instance',
                  'template_node',
                  'template_cite',
                  'instance_node',
                  'instance_details',
                  'instance_time',
                  'appmaker_instance',
                  'atom_cite',
                  'atom_execute_times',
                  'atom_avg_execute_time',
                  'atom_fail_percent']
    atom_dimensions = [atom_execute,
                       atom_instance,
                       atom_execute_times,
                       atom_execute_fail_times,
                       atom_avg_execute_time,
                       atom_fail_percent]


AE = AnalysisElement()

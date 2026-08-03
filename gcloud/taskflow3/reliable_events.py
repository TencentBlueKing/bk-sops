# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

可靠事件（reliable events）接管模式解析钩子。

引擎侧 `pipeline.contrib.reliable_events` 只定义契约 `mode_resolver(node_id, version)`，
判定哪些流程可以走 ACTIVE 兜底接管的逻辑全部由 bk-sops 提供，即本模块的 `resolve_mode`，
由 settings `PIPELINE_RELIABLE_EVENTS_MODE_RESOLVER` 指向。

注意：本模块与 `gcloud/contrib/admin/diagnostics/task_mapping.py` 的 `resolve_task_summaries()`
看起来相似但不可复用——后者是管理控制台展示用的重查询（select_related 拼 task_url、格式化时间，
且不返回 template_source）；本模块处在 callback 热路径上，只用 `.values(...)` 做最小字段查询。
"""

import logging

from gcloud.constants import COMMON
from gcloud.taskflow3.models import TaskConfig, TaskFlowInstance

logger = logging.getLogger("root")

# 与引擎侧 pipeline.contrib.reliable_events.models.EventMode 的取值保持一致，
# 引擎按精确字符串比较，只有 "ACTIVE" 才可能被接管。
SHADOW = "SHADOW"
ACTIVE = "ACTIVE"


def _resolve_project_template(node_id):
    """
    由引擎节点 id 反查出白名单判定所需的 (project_id, template_id)

    :return: (project_id, template_id) 或 None（信息不全时一律返回 None，由调用方退回 SHADOW）
    """
    # 函数内 import：避免模块导入期就依赖引擎运行时表
    from pipeline.eri.models import State

    state = State.objects.filter(node_id=node_id).values("root_id").first()
    if not state:
        return None

    root_id = state["root_id"]
    # root_id 允许为空串（默认值），此时无法定位任务
    if not root_id:
        return None

    taskflow = (
        TaskFlowInstance.objects.filter(pipeline_instance__instance_id=root_id, is_deleted=False)
        .values("project_id", "template_id", "template_source")
        .first()
    )
    if not taskflow:
        return None

    project_id = taskflow["project_id"]
    if project_id is None:
        return None

    # template_id 在 TaskFlowInstance 上是字符串，且允许为空
    try:
        template_id = int(taskflow["template_id"])
    except (TypeError, ValueError):
        return None

    if taskflow["template_source"] == COMMON:
        # 仓内约定：公共流程的配置以 scope_id = -template_id 存储。
        # 这里由我们自己取负，而不是传 project_id=-1 让 TaskConfigManager 去取负：
        # TaskFlowInstance.project_id 存的是真实项目 id，保留它才能让「按真实项目整体开启」的
        # 项目级回落继续生效；若传 project_id=-1，项目级回落将永远去查 scope_id=-1，等于废掉。
        template_id = -template_id

    return project_id, template_id


def resolve_mode(node_id, version):
    """
    引擎 mode_resolver 钩子：判定该节点的 callback 事件走 ACTIVE 还是 SHADOW

    :param node_id: 引擎节点 id
    :param version: 节点执行版本，当前不参与判定（白名单是流程级的），但引擎按位置传参，必须保留
    :return: "ACTIVE"（允许兜底接管）或 "SHADOW"（仅观察）

    引擎侧已把本钩子的调用包在 try/except 里，这里再兜一层是为了让契约在本模块内自洽，
    并避免异常刷到引擎侧的 debug 日志。任何异常都保守退回 SHADOW。
    """
    try:
        resolved = _resolve_project_template(node_id)
        if resolved is None:
            return SHADOW

        project_id, template_id = resolved
        if TaskConfig.objects.enable_active_callback_takeover(project_id=project_id, template_id=template_id):
            return ACTIVE
    except Exception:
        logger.debug(
            "[reliable_events] resolve_mode failed, fallback to SHADOW, node_id: {}".format(node_id), exc_info=True
        )
        return SHADOW

    return SHADOW

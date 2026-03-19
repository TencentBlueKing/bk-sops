# BKFlow 统计任务迁移开发方案

## 一、背景与目标

本文档旨在将 bk-sops 中的四个核心统计表的统计逻辑迁移到 bk-flow 项目。这四个统计表用于收集和分析流程模板与任务执行的运营数据。

### 需要迁移的统计表

| 统计表 | 用途 |
|--------|------|
| `TemplateNodeStatistics` | 模板中标准插件节点的引用统计 |
| `TemplateStatistics` | 模板维度的整体统计（节点数、变量数等） |
| `TaskflowStatistics` | 任务实例维度的统计 |
| `TaskflowExecutedNodeStatistics` | 任务执行过程中节点执行详情统计 |

---

## 二、bk-sops 与 bk-flow 数据结构差异对比

### 2.1 核心概念映射

| bk-sops | bk-flow | 说明 |
|---------|---------|------|
| `project_id` | 无直接对应 | bk-sops 的项目概念，bk-flow 中可能不需要或通过其他方式实现 |
| `bk_biz_id` (业务ID) | `scope_type` + `scope_value` | 业务范围标识，bk-flow 通过 scope_type/scope_value 实现更灵活的范围控制 |
| 无 | `space_id` | **bk-flow 新增字段**，用于区分不同的接入平台/空间（bk-flow 作为对接平台的核心概念） |
| `TaskTemplate` | `Template` | 流程模板 |
| `TaskFlowInstance` | `Task` / `TaskflowInstance` | 任务实例 |
| `pipeline_template.id` | `template.id` | 模板主键 |
| `pipeline_instance.id` | `instance_id` | 任务实例 ID（bk-flow 中是字符串形式） |
| `category` | 无 | bk-flow 无模板分类概念，可通过 `extra_info` 扩展 |

> **重要说明**：
> - `space_id` 是 bk-flow 作为流程引擎服务对接多个上层平台的核心概念，每个接入方（平台）对应一个 space
> - `scope_type` + `scope_value` 用于在 space 内部进一步区分业务范围，对应 bk-sops 中的 `bk_biz_id`
> - bk-sops 的 `project_id` 是项目维度的隔离，在 bk-flow 中这个概念由接入方自行管理

### 2.2 Template（模板）数据结构对比

**bk-sops TaskTemplate 关键字段：**
```python
{
    "id": 123,                          # 模板ID
    "project_id": 1,                    # 项目ID
    "category": "OpsTools",             # 模板分类
    "pipeline_template": {
        "id": 456,                      # Pipeline模板ID
        "template_id": "xxx",           # 模板唯一标识
        "creator": "admin",
        "create_time": "2024-01-01T00:00:00Z",
        "edit_time": "2024-01-02T00:00:00Z",
        "data": { ... }                 # pipeline_tree
    }
}
```

**bk-flow Template 关键字段：**
```python
{
    "id": 123,                          # 模板ID
    "space_id": 1,                      # 空间ID
    "scope_type": "biz",                # 范围类型（可为 null）
    "scope_value": "2",                 # 范围值（可为 null）
    "name": "模板名",
    "desc": null,
    "notify_config": {},
    "source": null,
    "version": "",
    "is_enabled": true,
    "extra_info": {},
    "creator": "",
    "create_at": "2024-07-30T06:27:52.642Z",
    "update_at": "2024-07-30T07:30:28.005Z",
    "updated_by": "",
    "pipeline_tree": { ... }            # 直接包含 pipeline_tree
}
```

### 2.3 Task（任务实例）数据结构对比

**bk-sops TaskFlowInstance 关键字段：**
```python
{
    "id": 10,
    "project_id": 1,
    "template_id": 123,                 # 关联的 TaskTemplate ID
    "pipeline_instance": {
        "id": 456,
        "instance_id": "xxx",
        "creator": "admin",
        "create_time": "2024-01-01T00:00:00Z",
        "start_time": "2024-01-01T00:01:00Z",
        "finish_time": "2024-01-01T00:10:00Z",
        "is_started": true,
        "is_finished": true,
        "is_revoked": false,
        "execution_data": { ... }       # 执行时的 pipeline_tree
    },
    "create_method": "app",             # 创建方式
    "engine_ver": 2                     # 引擎版本
}
```

**bk-flow Task 关键字段：**
```python
{
    "id": 10,
    "space_id": 1,                      # 空间ID
    "scope_type": null,                 # 范围类型
    "scope_value": null,                # 范围值
    "instance_id": "6e15e7cf27ab...",   # 实例ID（字符串）
    "template_id": 4,                   # 关联的模板ID
    "name": "任务名称",
    "creator": "",
    "create_time": "2024-01-01T00:00:00Z",
    "executor": "",
    "start_time": null,
    "finish_time": null,
    "description": "",
    "is_started": false,
    "is_finished": false,
    "is_revoked": false,
    "is_deleted": false,
    "is_expired": false,
    "create_method": "API",             # 创建方式
    "snapshot_id": 3,                   # 快照ID
    "execution_snapshot_id": 8,         # 执行快照ID
    "tree_info_id": null,
    "extra_info": {}
}
```

### 2.4 pipeline_tree 结构（两者基本一致）

```python
{
    "id": "p92c20c78...",
    "start_event": {
        "id": "ec628b28...",
        "type": "EmptyStartEvent",
        "incoming": "",
        "outgoing": "f06a78d1..."
    },
    "end_event": {
        "id": "e7533e78...",
        "type": "EmptyEndEvent",
        "incoming": ["f5b91a61..."],
        "outgoing": ""
    },
    "activities": {
        "e2945819...": {
            "id": "e2945819...",
            "type": "ServiceActivity",      # 标准插件节点
            "name": "节点名称",
            "component": {
                "code": "example_component", # 插件编码
                "version": "v1.0",           # 插件版本（可选）
                "inputs": {}
            },
            "error_ignorable": false,
            "skippable": true,
            "retryable": true,
            "optional": false,
            "incoming": [...],
            "outgoing": "..."
        }
        # SubProcess 类型节点也在 activities 中
    },
    "gateways": { ... },                    # 网关节点
    "flows": { ... },                       # 连线
    "data": {
        "inputs": { ... },                  # 全局变量
        "outputs": [ ... ]                  # 输出变量
    },
    "constants": { ... }                    # 常量定义（bk-sops 特有）
}
```

### 2.5 节点状态结构对比

**bk-flow 任务状态响应：**
```python
{
    "id": "ne7b82d4b...",
    "state": "FINISHED",                    # 状态：CREATED, READY, RUNNING, FINISHED, FAILED 等
    "root_id": "ne7b82d4b...",
    "parent_id": "ne7b82d4b...",
    "version": "va054509...",
    "loop": 1,
    "retry": 0,                             # 重试次数
    "skip": false,                          # 是否跳过
    "error_ignorable": false,
    "error_ignored": false,
    "elapsed_time": 0,                      # 执行耗时（秒）
    "start_time": "2023-06-15 17:29:41 +0800",
    "finish_time": "2023-06-15 17:29:41 +0800",
    "children": { ... }                     # 子节点状态
}
```

---

## 三、统计模型设计

### 3.1 TemplateNodeStatistics（模板节点统计）

```python
class TemplateNodeStatistics(models.Model):
    """模板中标准插件节点的引用统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 组件信息
    component_code = models.CharField("组件编码", max_length=255, db_index=True)
    version = models.CharField("插件版本", max_length=255, default="legacy")
    is_remote = models.BooleanField("是否第三方插件", default=False)
    
    # 模板关联（适配 bk-flow）
    template_id = models.BigIntegerField("模板ID", db_index=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True, db_index=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True, db_index=True)
    
    # 节点信息
    node_id = models.CharField("节点ID", max_length=64)
    node_name = models.CharField("节点名称", max_length=255, null=True, blank=True)
    is_sub = models.BooleanField("是否子流程引用", default=False)
    subprocess_stack = models.TextField("子流程堆栈", default="[]", help_text="JSON 格式的列表")
    
    # 模板元信息
    template_creator = models.CharField("模板创建者", max_length=255, null=True, blank=True)
    template_create_time = models.DateTimeField("模板创建时间", null=True)
    template_update_time = models.DateTimeField("模板更新时间", null=True)
    
    class Meta:
        verbose_name = "模板节点统计"
        verbose_name_plural = "模板节点统计"
        indexes = [
            models.Index(fields=['space_id', 'component_code']),
            models.Index(fields=['template_id', 'node_id']),
        ]

    def __str__(self):
        return f"{self.component_code}_{self.template_id}"
```

### 3.2 TemplateStatistics（模板统计）

```python
class TemplateStatistics(models.Model):
    """模板维度的整体统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 模板关联
    template_id = models.BigIntegerField("模板ID", db_index=True, unique=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True, db_index=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True, db_index=True)
    
    # 节点统计
    atom_total = models.IntegerField("标准插件节点总数", default=0)
    subprocess_total = models.IntegerField("子流程节点总数", default=0)
    gateways_total = models.IntegerField("网关节点总数", default=0)
    
    # 变量统计
    input_count = models.IntegerField("输入变量数", default=0)
    output_count = models.IntegerField("输出变量数", default=0)
    
    # 模板元信息
    template_name = models.CharField("模板名称", max_length=255, null=True, blank=True)
    template_creator = models.CharField("模板创建者", max_length=255, null=True, blank=True)
    template_create_time = models.DateTimeField("模板创建时间", null=True, db_index=True)
    template_update_time = models.DateTimeField("模板更新时间", null=True)
    is_enabled = models.BooleanField("是否启用", default=True)
    
    class Meta:
        verbose_name = "模板统计"
        verbose_name_plural = "模板统计"
        indexes = [
            models.Index(fields=['space_id', 'template_create_time']),
        ]

    def __str__(self):
        return f"Template_{self.template_id}"
```

### 3.3 TaskflowStatistics（任务实例统计）

```python
class TaskflowStatistics(models.Model):
    """任务实例维度的统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 任务关联
    task_id = models.BigIntegerField("任务ID", db_index=True, unique=True)
    instance_id = models.CharField("Pipeline实例ID", max_length=64, db_index=True)
    template_id = models.BigIntegerField("关联模板ID", null=True, blank=True, db_index=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True, db_index=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True, db_index=True)
    
    # 节点统计
    atom_total = models.IntegerField("标准插件节点总数", default=0)
    subprocess_total = models.IntegerField("子流程节点总数", default=0)
    gateways_total = models.IntegerField("网关节点总数", default=0)
    
    # 执行信息
    creator = models.CharField("创建者", max_length=128, blank=True)
    executor = models.CharField("执行者", max_length=128, blank=True)
    create_time = models.DateTimeField("创建时间", db_index=True)
    start_time = models.DateTimeField("启动时间", null=True, blank=True)
    finish_time = models.DateTimeField("结束时间", null=True, blank=True)
    elapsed_time = models.IntegerField("执行耗时(秒)", null=True, blank=True)
    
    # 创建方式
    create_method = models.CharField("创建方式", max_length=32, default="API", db_index=True)
    # 可选值: API, MANUAL, PERIODIC, CLOCKED 等
    
    class Meta:
        verbose_name = "任务统计"
        verbose_name_plural = "任务统计"
        indexes = [
            models.Index(fields=['space_id', 'create_time']),
            models.Index(fields=['template_id', 'create_time']),
        ]

    def __str__(self):
        return f"Task_{self.task_id}"
```

### 3.4 TaskflowExecutedNodeStatistics（节点执行统计）

```python
class TaskflowExecutedNodeStatistics(models.Model):
    """任务执行过程中节点执行详情统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 组件信息
    component_code = models.CharField("组件编码", max_length=255, db_index=True)
    version = models.CharField("插件版本", max_length=255, default="legacy")
    is_remote = models.BooleanField("是否第三方插件", default=False)
    
    # 任务关联
    task_id = models.BigIntegerField("任务ID", db_index=True)
    instance_id = models.CharField("Pipeline实例ID", max_length=64, db_index=True)
    template_id = models.BigIntegerField("关联模板ID", null=True, blank=True, db_index=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True)
    
    # 节点信息
    node_id = models.CharField("节点ID", max_length=64, db_index=True)
    node_name = models.CharField("节点名称", max_length=255, null=True, blank=True)
    template_node_id = models.CharField("模板节点ID", max_length=64, null=True, blank=True)
    is_sub = models.BooleanField("是否子流程引用", default=False)
    subprocess_stack = models.TextField("子流程堆栈", default="[]", help_text="JSON 格式的列表")
    
    # 执行信息
    started_time = models.DateTimeField("节点执行开始时间", db_index=True)
    archived_time = models.DateTimeField("节点执行结束时间", null=True, blank=True)
    elapsed_time = models.IntegerField("节点执行耗时(秒)", null=True, blank=True)
    
    # 执行状态
    status = models.BooleanField("是否执行成功", default=False)
    state = models.CharField("节点状态", max_length=32, default="", db_index=True)
    # 可选值: CREATED, READY, RUNNING, FINISHED, FAILED, SUSPENDED 等
    is_skip = models.BooleanField("是否跳过", default=False)
    is_retry = models.BooleanField("是否重试记录", default=False)
    retry_count = models.IntegerField("重试次数", default=0)
    
    # 任务实例时间（冗余，便于统计）
    task_create_time = models.DateTimeField("任务创建时间", db_index=True)
    task_start_time = models.DateTimeField("任务启动时间", null=True, blank=True)
    task_finish_time = models.DateTimeField("任务结束时间", null=True, blank=True)
    
    class Meta:
        verbose_name = "节点执行统计"
        verbose_name_plural = "节点执行统计"
        indexes = [
            models.Index(fields=['space_id', 'component_code', 'started_time']),
            models.Index(fields=['task_id', 'node_id']),
            models.Index(fields=['component_code', 'status', 'started_time']),
        ]

    def __str__(self):
        return f"{self.component_code}_{self.task_id}_{self.node_id}"
```

---

## 四、统计任务实现

### 4.1 任务触发机制设计

| 统计任务 | 触发方式 | 触发时机 |
|----------|----------|----------|
| `template_post_save_statistics_task` | 信号/事件 | 模板创建或更新时 |
| `task_post_save_statistics_task` | 信号/事件 | 任务实例创建或更新时 |
| `task_archive_statistics_task` | 信号/事件 | 任务执行完成或撤销时 |

### 4.2 信号处理器（signals/handlers.py）

```python
# -*- coding: utf-8 -*-
"""
BKFlow 统计信号处理器

需要根据 bk-flow 实际的信号机制进行调整。
可能的信号来源：
1. Django model 的 post_save 信号
2. bamboo_engine 的 pipeline 完成/撤销信号
3. bk-flow 自定义的信号
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

# 假设的 bk-flow 模型导入路径，需要根据实际情况调整
# from bkflow.template.models import Template
# from bkflow.task.models import Task

from .tasks import (
    template_post_save_statistics_task,
    task_post_save_statistics_task,
    task_archive_statistics_task,
)

logger = logging.getLogger("celery")


# 模板保存后的信号处理
# @receiver(post_save, sender=Template)
def template_post_save_handler(sender, instance, created, **kwargs):
    """
    模板保存后触发统计任务
    更新 TemplateNodeStatistics 和 TemplateStatistics
    """
    try:
        template_id = instance.id
        template_post_save_statistics_task.delay(template_id)
    except Exception as e:
        logger.exception(
            f"[template_post_save_handler] template_id={instance.id} send message error: {e}"
        )


# 任务创建/更新后的信号处理
# @receiver(post_save, sender=Task)
def task_post_save_handler(sender, instance, created, **kwargs):
    """
    任务实例保存后触发统计任务
    更新 TaskflowStatistics
    """
    try:
        task_id = instance.id
        task_post_save_statistics_task.delay(task_id, created)
    except Exception as e:
        logger.exception(
            f"[task_post_save_handler] task_id={instance.id} send message error: {e}"
        )


# Pipeline 完成信号处理
# 需要根据 bk-flow 或 bamboo_engine 的实际信号进行调整
# 可能需要监听 bamboo_engine 的 post_pipeline_finish 和 post_pipeline_revoke 信号
def pipeline_finish_handler(sender, instance_id, **kwargs):
    """
    Pipeline 执行完成后触发统计任务
    更新 TaskflowExecutedNodeStatistics 和 TaskflowStatistics
    """
    try:
        task_archive_statistics_task.delay(instance_id=instance_id)
    except Exception as e:
        logger.exception(
            f"[pipeline_finish_handler] instance_id={instance_id} send message error: {e}"
        )


def pipeline_revoke_handler(sender, instance_id, **kwargs):
    """
    Pipeline 撤销后触发统计任务
    """
    try:
        task_archive_statistics_task.delay(instance_id=instance_id)
    except Exception as e:
        logger.exception(
            f"[pipeline_revoke_handler] instance_id={instance_id} send message error: {e}"
        )
```

### 4.3 Celery 任务实现（tasks.py）

```python
# -*- coding: utf-8 -*-
"""
BKFlow 统计 Celery 任务

实现四个统计表的数据采集逻辑
"""

import logging
from copy import deepcopy
from datetime import datetime
from typing import List, Dict, Any, Optional

import ujson as json
from celery import shared_task
from django.db import transaction

# bamboo_engine 相关导入
from bamboo_engine import api as bamboo_engine_api
from bamboo_engine.engine import Engine
from pipeline.eri.runtime import BambooDjangoRuntime

# 假设的 bk-flow 模型导入路径
# from bkflow.template.models import Template
# from bkflow.task.models import Task, TaskSnapshot

from .models import (
    TemplateNodeStatistics,
    TemplateStatistics,
    TaskflowStatistics,
    TaskflowExecutedNodeStatistics,
)

logger = logging.getLogger("celery")


def count_pipeline_tree_nodes(pipeline_tree: dict) -> tuple:
    """
    统计 pipeline_tree 中的节点数量
    
    Args:
        pipeline_tree: pipeline 树结构
        
    Returns:
        tuple: (atom_total, subprocess_total, gateways_total)
    """
    activities = pipeline_tree.get("activities", {})
    gateways = pipeline_tree.get("gateways", {})
    
    atom_total = 0
    subprocess_total = 0
    
    for act_id, act in activities.items():
        act_type = act.get("type", "")
        if act_type == "ServiceActivity":
            atom_total += 1
        elif act_type == "SubProcess":
            subprocess_total += 1
            # 递归统计子流程内的节点
            sub_pipeline = act.get("pipeline", {})
            if sub_pipeline:
                sub_atom, sub_subproc, sub_gw = count_pipeline_tree_nodes(sub_pipeline)
                atom_total += sub_atom
                subprocess_total += sub_subproc
    
    gateways_total = len(gateways)
    
    return atom_total, subprocess_total, gateways_total


def parse_datetime(time_str: str, time_format: str = "%Y-%m-%d %H:%M:%S %z") -> Optional[datetime]:
    """
    解析时间字符串
    
    Args:
        time_str: 时间字符串
        time_format: 时间格式
        
    Returns:
        datetime 对象或 None
    """
    if not time_str:
        return None
    try:
        # 处理多种可能的时间格式
        formats = [
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S+%H%M",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(time_str.strip(), fmt)
            except ValueError:
                continue
        # 尝试去掉时区信息
        clean_str = time_str.split("+")[0].strip()
        return datetime.strptime(clean_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def calculate_elapsed_time(start_time: datetime, finish_time: datetime) -> Optional[int]:
    """
    计算执行耗时（秒）
    """
    if start_time and finish_time:
        return int((finish_time - start_time).total_seconds())
    return None


@shared_task(bind=True, ignore_result=True)
def template_post_save_statistics_task(self, template_id: int):
    """
    模板保存后的统计任务
    
    统计内容：
    1. TemplateNodeStatistics - 模板中每个标准插件节点的引用情况
    2. TemplateStatistics - 模板的整体统计
    
    Args:
        template_id: 模板 ID
    """
    try:
        # TODO: 根据 bk-flow 实际模型调整
        # template = Template.objects.get(id=template_id)
        template = None  # 占位，需要替换为实际模型查询
        
        if template is None:
            logger.warning(f"Template {template_id} not found")
            return False
        
        # 获取 pipeline_tree
        pipeline_tree = template.pipeline_tree or {}
        
        # 1. 删除该模板的旧统计数据
        with transaction.atomic():
            TemplateNodeStatistics.objects.filter(template_id=template_id).delete()
        
        # 2. 收集节点统计数据
        component_list = collect_template_nodes(
            template_id=template_id,
            space_id=template.space_id,
            scope_type=template.scope_type,
            scope_value=template.scope_value,
            pipeline_tree=pipeline_tree,
            template_creator=template.creator,
            template_create_time=template.create_at,
            template_update_time=template.update_at,
        )
        
        # 3. 批量创建节点统计记录
        if component_list:
            TemplateNodeStatistics.objects.bulk_create(component_list, batch_size=100)
        
        # 4. 更新模板统计
        atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(pipeline_tree)
        
        # 统计变量数量
        data = pipeline_tree.get("data", {})
        constants = pipeline_tree.get("constants", {})
        
        input_count = 0
        output_count = 0
        
        # 通过 constants 统计变量
        for key, const in constants.items():
            source_type = const.get("source_type", "")
            if source_type == "component_outputs":
                output_count += 1
            else:
                input_count += 1
        
        # 如果没有 constants，通过 data 统计
        if not constants:
            input_count = len(data.get("inputs", {}))
            output_count = len(data.get("outputs", []))
        
        TemplateStatistics.objects.update_or_create(
            template_id=template_id,
            defaults={
                "space_id": template.space_id,
                "scope_type": template.scope_type,
                "scope_value": template.scope_value,
                "atom_total": atom_total,
                "subprocess_total": subprocess_total,
                "gateways_total": gateways_total,
                "input_count": input_count,
                "output_count": output_count,
                "template_name": template.name,
                "template_creator": template.creator,
                "template_create_time": template.create_at,
                "template_update_time": template.update_at,
                "is_enabled": template.is_enabled,
            }
        )
        
        logger.info(f"[template_post_save_statistics_task] template_id={template_id} statistics updated")
        return True
        
    except Exception as e:
        logger.exception(
            f"[template_post_save_statistics_task] template_id={template_id} error: {e}"
        )
        return False


def collect_template_nodes(
    template_id: int,
    space_id: int,
    scope_type: str,
    scope_value: str,
    pipeline_tree: dict,
    template_creator: str,
    template_create_time: datetime,
    template_update_time: datetime,
    subprocess_stack: list = None,
    is_sub: bool = False,
) -> List[TemplateNodeStatistics]:
    """
    递归收集模板中的节点统计数据
    
    Args:
        template_id: 模板 ID
        space_id: 空间 ID
        scope_type: 范围类型
        scope_value: 范围值
        pipeline_tree: pipeline 树结构
        template_creator: 模板创建者
        template_create_time: 模板创建时间
        template_update_time: 模板更新时间
        subprocess_stack: 子流程堆栈
        is_sub: 是否子流程内的节点
        
    Returns:
        TemplateNodeStatistics 对象列表
    """
    if subprocess_stack is None:
        subprocess_stack = []
    
    component_list = []
    activities = pipeline_tree.get("activities", {})
    
    for act_id, act in activities.items():
        act_type = act.get("type", "")
        
        if act_type == "ServiceActivity":
            # 标准插件节点
            component = act.get("component", {})
            component_code = component.get("code", "")
            component_version = component.get("version", "legacy")
            
            # 判断是否第三方插件
            is_remote = False
            if component_code == "remote_plugin":
                inputs = component.get("inputs", {})
                component_code = inputs.get("plugin_code", {}).get("value", component_code)
                component_version = inputs.get("plugin_version", {}).get("value", component_version)
                is_remote = True
            
            node_stat = TemplateNodeStatistics(
                component_code=component_code,
                version=component_version,
                is_remote=is_remote,
                template_id=template_id,
                space_id=space_id,
                scope_type=scope_type,
                scope_value=scope_value,
                node_id=act_id,
                node_name=act.get("name", ""),
                is_sub=is_sub,
                subprocess_stack=json.dumps(subprocess_stack),
                template_creator=template_creator,
                template_create_time=template_create_time,
                template_update_time=template_update_time,
            )
            component_list.append(node_stat)
            
        elif act_type == "SubProcess":
            # 子流程节点，递归处理
            sub_pipeline = act.get("pipeline", {})
            if sub_pipeline:
                new_stack = deepcopy(subprocess_stack)
                new_stack.insert(0, act_id)
                sub_components = collect_template_nodes(
                    template_id=template_id,
                    space_id=space_id,
                    scope_type=scope_type,
                    scope_value=scope_value,
                    pipeline_tree=sub_pipeline,
                    template_creator=template_creator,
                    template_create_time=template_create_time,
                    template_update_time=template_update_time,
                    subprocess_stack=new_stack,
                    is_sub=True,
                )
                component_list.extend(sub_components)
    
    return component_list


@shared_task(bind=True, ignore_result=True)
def task_post_save_statistics_task(self, task_id: int, created: bool):
    """
    任务实例保存后的统计任务
    
    统计内容：
    TaskflowStatistics - 任务实例的统计数据
    
    Args:
        task_id: 任务 ID
        created: 是否新创建
    """
    try:
        # TODO: 根据 bk-flow 实际模型调整
        # task = Task.objects.get(id=task_id)
        task = None  # 占位，需要替换为实际模型查询
        
        if task is None:
            logger.warning(f"Task {task_id} not found")
            return False
        
        # 获取执行时的 pipeline_tree
        # 需要根据 bk-flow 的快照机制获取
        # execution_snapshot = TaskSnapshot.objects.get(id=task.execution_snapshot_id)
        # pipeline_tree = execution_snapshot.data
        pipeline_tree = {}  # 占位
        
        # 统计节点数量
        atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(pipeline_tree)
        
        # 计算执行耗时
        elapsed_time = calculate_elapsed_time(task.start_time, task.finish_time)
        
        kwargs = {
            "task_id": task.id,
            "instance_id": task.instance_id,
            "template_id": task.template_id,
            "space_id": task.space_id,
            "scope_type": task.scope_type,
            "scope_value": task.scope_value,
            "atom_total": atom_total,
            "subprocess_total": subprocess_total,
            "gateways_total": gateways_total,
            "creator": task.creator,
            "executor": task.executor,
            "create_time": task.create_time,
            "start_time": task.start_time,
            "finish_time": task.finish_time,
            "elapsed_time": elapsed_time,
            "create_method": getattr(task, "create_method", "API"),
        }
        
        if created:
            TaskflowStatistics.objects.create(**kwargs)
        else:
            TaskflowStatistics.objects.filter(task_id=task_id).update(**kwargs)
        
        logger.info(f"[task_post_save_statistics_task] task_id={task_id} statistics updated")
        return True
        
    except Exception as e:
        logger.exception(
            f"[task_post_save_statistics_task] task_id={task_id} error: {e}"
        )
        return False


@shared_task(bind=True, ignore_result=True)
def task_archive_statistics_task(self, instance_id: str):
    """
    任务归档统计任务（执行完成或撤销后触发）
    
    统计内容：
    1. TaskflowExecutedNodeStatistics - 节点执行详情
    2. TaskflowStatistics - 更新执行时间信息
    
    Args:
        instance_id: Pipeline 实例 ID
    """
    try:
        # TODO: 根据 bk-flow 实际模型调整查询方式
        # task = Task.objects.get(instance_id=instance_id)
        task = None  # 占位
        
        if task is None:
            logger.warning(f"Task with instance_id={instance_id} not found")
            return False
        
        # 1. 更新 TaskflowStatistics 的时间信息
        elapsed_time = calculate_elapsed_time(task.start_time, task.finish_time)
        TaskflowStatistics.objects.filter(task_id=task.id).update(
            start_time=task.start_time,
            finish_time=task.finish_time,
            elapsed_time=elapsed_time,
        )
        
        # 2. 获取任务状态树
        runtime = BambooDjangoRuntime()
        status_result = bamboo_engine_api.get_pipeline_states(
            runtime=runtime,
            root_id=instance_id,
        )
        
        if not status_result.result:
            logger.error(f"[task_archive_statistics_task] get_pipeline_states failed: {status_result.message}")
            return False
        
        status_tree = status_result.data
        
        # 3. 获取执行时的 pipeline_tree
        # execution_snapshot = TaskSnapshot.objects.get(id=task.execution_snapshot_id)
        # pipeline_tree = execution_snapshot.data
        pipeline_tree = {}  # 占位
        
        # 4. 删除旧的节点执行统计数据
        TaskflowExecutedNodeStatistics.objects.filter(task_id=task.id).delete()
        
        # 5. 收集节点执行数据
        executed_nodes = collect_executed_nodes(
            task=task,
            pipeline_tree=pipeline_tree,
            status_tree=status_tree,
        )
        
        # 6. 批量创建
        if executed_nodes:
            TaskflowExecutedNodeStatistics.objects.bulk_create(executed_nodes, batch_size=100)
        
        logger.info(f"[task_archive_statistics_task] task_id={task.id} statistics updated")
        return True
        
    except Exception as e:
        logger.exception(
            f"[task_archive_statistics_task] instance_id={instance_id} error: {e}"
        )
        return False


def collect_executed_nodes(
    task,  # Task 实例
    pipeline_tree: dict,
    status_tree: dict,
    subprocess_stack: list = None,
    is_sub: bool = False,
) -> List[TaskflowExecutedNodeStatistics]:
    """
    递归收集已执行节点的统计数据
    
    Args:
        task: 任务实例
        pipeline_tree: pipeline 树结构
        status_tree: 状态树
        subprocess_stack: 子流程堆栈
        is_sub: 是否子流程内的节点
        
    Returns:
        TaskflowExecutedNodeStatistics 对象列表
    """
    if subprocess_stack is None:
        subprocess_stack = []
    
    component_list = []
    activities = pipeline_tree.get("activities", {})
    children = status_tree.get("children", {})
    
    for act_id, act in activities.items():
        if act_id not in children:
            continue
        
        node_status = children[act_id]
        act_type = act.get("type", "")
        
        if act_type == "ServiceActivity":
            # 标准插件节点
            state = node_status.get("state", "")
            
            # 只统计已完成状态的节点
            # FINISHED, FAILED, REVOKED 等归档状态
            if state not in ("FINISHED", "FAILED", "REVOKED", "SUSPENDED"):
                continue
            
            component = act.get("component", {})
            component_code = component.get("code", "")
            component_version = component.get("version", "legacy")
            
            # 判断是否第三方插件
            is_remote = False
            if component_code == "remote_plugin":
                inputs = component.get("inputs", {})
                component_code = inputs.get("plugin_code", {}).get("value", component_code)
                component_version = inputs.get("plugin_version", {}).get("value", component_version)
                is_remote = True
            
            # 解析时间
            started_time = parse_datetime(node_status.get("start_time", ""))
            archived_time = parse_datetime(node_status.get("finish_time", ""))
            elapsed_time = node_status.get("elapsed_time")
            if elapsed_time is None and started_time and archived_time:
                elapsed_time = calculate_elapsed_time(started_time, archived_time)
            
            node_stat = TaskflowExecutedNodeStatistics(
                component_code=component_code,
                version=component_version,
                is_remote=is_remote,
                task_id=task.id,
                instance_id=task.instance_id,
                template_id=task.template_id,
                space_id=task.space_id,
                scope_type=task.scope_type,
                scope_value=task.scope_value,
                node_id=act_id,
                node_name=act.get("name", ""),
                template_node_id=act.get("template_node_id", ""),
                is_sub=is_sub,
                subprocess_stack=json.dumps(subprocess_stack),
                started_time=started_time,
                archived_time=archived_time,
                elapsed_time=elapsed_time,
                status=(state == "FINISHED"),
                state=state,
                is_skip=node_status.get("skip", False),
                is_retry=False,
                retry_count=node_status.get("retry", 0),
                task_create_time=task.create_time,
                task_start_time=task.start_time,
                task_finish_time=task.finish_time,
            )
            component_list.append(node_stat)
            
            # 处理重试记录
            retry_count = node_status.get("retry", 0)
            if retry_count > 0:
                # 获取历史执行记录
                runtime = BambooDjangoRuntime()
                history_result = bamboo_engine_api.get_node_short_histories(
                    runtime=runtime,
                    node_id=act_id,
                )
                if history_result.result:
                    for history in history_result.data:
                        hist_started = history.get("started_time")
                        hist_archived = history.get("archived_time")
                        hist_elapsed = history.get("elapsed_time")
                        if hist_elapsed is None and hist_started and hist_archived:
                            hist_elapsed = calculate_elapsed_time(hist_started, hist_archived)
                        
                        retry_stat = TaskflowExecutedNodeStatistics(
                            component_code=component_code,
                            version=component_version,
                            is_remote=is_remote,
                            task_id=task.id,
                            instance_id=task.instance_id,
                            template_id=task.template_id,
                            space_id=task.space_id,
                            scope_type=task.scope_type,
                            scope_value=task.scope_value,
                            node_id=act_id,
                            node_name=act.get("name", ""),
                            template_node_id=act.get("template_node_id", ""),
                            is_sub=is_sub,
                            subprocess_stack=json.dumps(subprocess_stack),
                            started_time=hist_started,
                            archived_time=hist_archived,
                            elapsed_time=hist_elapsed,
                            status=False,
                            state="FAILED",
                            is_skip=False,
                            is_retry=True,
                            retry_count=retry_count,
                            task_create_time=task.create_time,
                            task_start_time=task.start_time,
                            task_finish_time=task.finish_time,
                        )
                        component_list.append(retry_stat)
                        
        elif act_type == "SubProcess":
            # 子流程节点，递归处理
            sub_pipeline = act.get("pipeline", {})
            sub_status = node_status.get("children", {})
            if sub_pipeline and sub_status:
                new_stack = deepcopy(subprocess_stack)
                new_stack.insert(0, act_id)
                sub_components = collect_executed_nodes(
                    task=task,
                    pipeline_tree=sub_pipeline,
                    status_tree={"children": sub_status},
                    subprocess_stack=new_stack,
                    is_sub=True,
                )
                component_list.extend(sub_components)
    
    return component_list
```

---

## 五、应用配置

### 5.1 应用目录结构

```
bkflow/
└── analysis_statistics/
    ├── __init__.py
    ├── apps.py
    ├── models.py           # 统计模型定义
    ├── tasks.py            # Celery 统计任务
    ├── signals/
    │   ├── __init__.py
    │   └── handlers.py     # 信号处理器
    ├── admin.py            # Django Admin 配置（可选）
    ├── migrations/
    │   └── __init__.py
    └── utils.py            # 工具函数（可选）
```

### 5.2 apps.py 配置

```python
# -*- coding: utf-8 -*-
from django.apps import AppConfig


class AnalysisStatisticsConfig(AppConfig):
    name = "bkflow.analysis_statistics"
    verbose_name = "Analysis Statistics"
    
    def ready(self):
        # 导入信号处理器以注册信号
        from . import signals  # noqa
```

### 5.3 信号注册（signals/__init__.py）

```python
# -*- coding: utf-8 -*-
"""
信号注册

需要根据 bk-flow 的实际模型和信号进行调整
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

# 导入处理器
from .handlers import (
    template_post_save_handler,
    task_post_save_handler,
    pipeline_finish_handler,
    pipeline_revoke_handler,
)

# TODO: 根据 bk-flow 实际情况注册信号
# 示例：
# from bkflow.template.models import Template
# from bkflow.task.models import Task
# 
# post_save.connect(template_post_save_handler, sender=Template)
# post_save.connect(task_post_save_handler, sender=Task)
# 
# 对于 pipeline 完成/撤销信号，需要查看 bk-flow 或 bamboo_engine 的信号机制
# 可能需要使用 bamboo_engine 的信号或自定义信号
```

---

## 六、开发步骤清单

### 6.1 Phase 1: 模型创建

- [ ] 1.1 创建 `analysis_statistics` Django 应用
- [ ] 1.2 实现四个统计模型（参考第三章）
- [ ] 1.3 创建数据库迁移文件
- [ ] 1.4 执行数据库迁移

### 6.2 Phase 2: 任务实现

- [ ] 2.1 实现 `count_pipeline_tree_nodes` 工具函数
- [ ] 2.2 实现 `template_post_save_statistics_task` 任务
- [ ] 2.3 实现 `task_post_save_statistics_task` 任务
- [ ] 2.4 实现 `task_archive_statistics_task` 任务
- [ ] 2.5 实现节点收集辅助函数

### 6.3 Phase 3: 信号集成

- [ ] 3.1 确认 bk-flow 的 Template 和 Task 模型位置
- [ ] 3.2 确认 bk-flow/bamboo_engine 的 pipeline 完成信号
- [ ] 3.3 实现并注册信号处理器
- [ ] 3.4 在 apps.py 中配置信号自动加载

### 6.4 Phase 4: 测试验证

- [ ] 4.1 单元测试：统计逻辑测试
- [ ] 4.2 集成测试：信号触发测试
- [ ] 4.3 E2E 测试：完整流程测试
- [ ] 4.4 性能测试：大数据量统计性能

### 6.5 Phase 5: 文档与部署

- [ ] 5.1 编写开发者文档
- [ ] 5.2 配置 Celery Worker
- [ ] 5.3 部署验证

---

## 七、注意事项

### 7.1 需要确认的 bk-flow 实现细节

1. **模型位置确认**
   - Template 模型的完整路径
   - Task/TaskflowInstance 模型的完整路径
   - 快照（Snapshot）机制的实现

2. **信号机制确认**
   - bk-flow 是否有自定义信号
   - bamboo_engine 的 pipeline 完成信号如何接入
   - 是否需要通过 Celery 任务回调实现

3. **数据获取方式**
   - pipeline_tree 的获取方式（直接从模型还是快照）
   - 任务状态树的获取方式
   - 节点执行历史的获取方式

### 7.2 性能优化建议

1. **批量操作**
   - 使用 `bulk_create` 批量创建记录
   - 设置合理的 `batch_size`

2. **数据库索引**
   - 确保查询频繁的字段有索引
   - 复合索引优化多条件查询

3. **异步处理**
   - 统计任务通过 Celery 异步执行
   - 避免阻塞主业务流程

### 7.3 与 bk-sops 的差异处理

| 差异点 | bk-sops | bk-flow 处理方案 |
|--------|---------|------------------|
| 平台标识 | 无（单一平台） | `space_id` - bk-flow 新增，用于区分接入的不同平台 |
| 业务标识 | `bk_biz_id` | `scope_type` + `scope_value` - 在 space 内区分业务范围 |
| 项目标识 | `project_id` | 由接入方自行管理，统计表中可不保留或通过 `extra_info` 存储 |
| 模板分类 | `category` 字段 | 可通过 `extra_info` 扩展或忽略 |
| 引擎版本 | `engine_ver` (1/2) | bk-flow 统一使用 bamboo_engine |
| 公共模板 | `CommonTemplate` | 需确认 bk-flow 是否有类似概念 |

> **字段映射总结**：
> - bk-flow 统计表需要 `space_id` 字段（必需），用于区分不同接入平台
> - bk-flow 统计表使用 `scope_type` + `scope_value` 替代 bk-sops 的 `bk_biz_id`
> - bk-sops 的 `project_id` 在 bk-flow 中没有直接对应，根据实际需求决定是否保留

---

## 八、参考资料

### 8.1 bk-sops 相关代码

- 统计模型: `gcloud/analysis_statistics/models.py`
- 统计任务: `gcloud/analysis_statistics/tasks.py`
- 信号处理: `gcloud/analysis_statistics/signals/handlers.py`

### 8.2 bk-flow 文档

- Template API: `/apigw/docs/zh/create_template.md`
- Task API: `/apigw/docs/zh/create_task.md`
- Task States API: `/apigw/docs/zh/get_task_states.md`

### 8.3 bamboo_engine API

- `bamboo_engine.api.get_pipeline_states` - 获取 pipeline 状态
- `bamboo_engine.api.get_node_short_histories` - 获取节点执行历史
- `pipeline.eri.runtime.BambooDjangoRuntime` - Django 运行时

---

## 九、附录：完整模型代码

将以下代码保存到 `bkflow/analysis_statistics/models.py`:

```python
# -*- coding: utf-8 -*-
"""
BKFlow Analysis Statistics Models

统计模型定义，用于记录模板和任务的运营数据
"""

from django.db import models


class TemplateNodeStatistics(models.Model):
    """模板中标准插件节点的引用统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 组件信息
    component_code = models.CharField("组件编码", max_length=255, db_index=True)
    version = models.CharField("插件版本", max_length=255, default="legacy")
    is_remote = models.BooleanField("是否第三方插件", default=False)
    
    # 模板关联
    template_id = models.BigIntegerField("模板ID", db_index=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True, db_index=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True, db_index=True)
    
    # 节点信息
    node_id = models.CharField("节点ID", max_length=64)
    node_name = models.CharField("节点名称", max_length=255, null=True, blank=True)
    is_sub = models.BooleanField("是否子流程引用", default=False)
    subprocess_stack = models.TextField("子流程堆栈", default="[]")
    
    # 模板元信息
    template_creator = models.CharField("模板创建者", max_length=255, null=True, blank=True)
    template_create_time = models.DateTimeField("模板创建时间", null=True)
    template_update_time = models.DateTimeField("模板更新时间", null=True)
    
    class Meta:
        verbose_name = "模板节点统计"
        verbose_name_plural = "模板节点统计"
        indexes = [
            models.Index(fields=['space_id', 'component_code']),
            models.Index(fields=['template_id', 'node_id']),
        ]


class TemplateStatistics(models.Model):
    """模板维度的整体统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 模板关联
    template_id = models.BigIntegerField("模板ID", db_index=True, unique=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True, db_index=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True, db_index=True)
    
    # 节点统计
    atom_total = models.IntegerField("标准插件节点总数", default=0)
    subprocess_total = models.IntegerField("子流程节点总数", default=0)
    gateways_total = models.IntegerField("网关节点总数", default=0)
    
    # 变量统计
    input_count = models.IntegerField("输入变量数", default=0)
    output_count = models.IntegerField("输出变量数", default=0)
    
    # 模板元信息
    template_name = models.CharField("模板名称", max_length=255, null=True, blank=True)
    template_creator = models.CharField("模板创建者", max_length=255, null=True, blank=True)
    template_create_time = models.DateTimeField("模板创建时间", null=True, db_index=True)
    template_update_time = models.DateTimeField("模板更新时间", null=True)
    is_enabled = models.BooleanField("是否启用", default=True)
    
    class Meta:
        verbose_name = "模板统计"
        verbose_name_plural = "模板统计"
        indexes = [
            models.Index(fields=['space_id', 'template_create_time']),
        ]


class TaskflowStatistics(models.Model):
    """任务实例维度的统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 任务关联
    task_id = models.BigIntegerField("任务ID", db_index=True, unique=True)
    instance_id = models.CharField("Pipeline实例ID", max_length=64, db_index=True)
    template_id = models.BigIntegerField("关联模板ID", null=True, blank=True, db_index=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True, db_index=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True, db_index=True)
    
    # 节点统计
    atom_total = models.IntegerField("标准插件节点总数", default=0)
    subprocess_total = models.IntegerField("子流程节点总数", default=0)
    gateways_total = models.IntegerField("网关节点总数", default=0)
    
    # 执行信息
    creator = models.CharField("创建者", max_length=128, blank=True)
    executor = models.CharField("执行者", max_length=128, blank=True)
    create_time = models.DateTimeField("创建时间", db_index=True)
    start_time = models.DateTimeField("启动时间", null=True, blank=True)
    finish_time = models.DateTimeField("结束时间", null=True, blank=True)
    elapsed_time = models.IntegerField("执行耗时(秒)", null=True, blank=True)
    
    # 创建方式
    create_method = models.CharField("创建方式", max_length=32, default="API", db_index=True)
    
    class Meta:
        verbose_name = "任务统计"
        verbose_name_plural = "任务统计"
        indexes = [
            models.Index(fields=['space_id', 'create_time']),
            models.Index(fields=['template_id', 'create_time']),
        ]


class TaskflowExecutedNodeStatistics(models.Model):
    """任务执行过程中节点执行详情统计"""
    
    id = models.BigAutoField(primary_key=True)
    
    # 组件信息
    component_code = models.CharField("组件编码", max_length=255, db_index=True)
    version = models.CharField("插件版本", max_length=255, default="legacy")
    is_remote = models.BooleanField("是否第三方插件", default=False)
    
    # 任务关联
    task_id = models.BigIntegerField("任务ID", db_index=True)
    instance_id = models.CharField("Pipeline实例ID", max_length=64, db_index=True)
    template_id = models.BigIntegerField("关联模板ID", null=True, blank=True, db_index=True)
    
    # bk-flow 平台标识（新增字段，用于区分接入的不同平台）
    space_id = models.BigIntegerField("空间ID", db_index=True, help_text="bk-flow 接入平台标识")
    
    # 业务范围标识（对应 bk-sops 的 bk_biz_id）
    scope_type = models.CharField("范围类型", max_length=64, null=True, blank=True)
    scope_value = models.CharField("范围值", max_length=255, null=True, blank=True)
    
    # 节点信息
    node_id = models.CharField("节点ID", max_length=64, db_index=True)
    node_name = models.CharField("节点名称", max_length=255, null=True, blank=True)
    template_node_id = models.CharField("模板节点ID", max_length=64, null=True, blank=True)
    is_sub = models.BooleanField("是否子流程引用", default=False)
    subprocess_stack = models.TextField("子流程堆栈", default="[]")
    
    # 执行信息
    started_time = models.DateTimeField("节点执行开始时间", db_index=True)
    archived_time = models.DateTimeField("节点执行结束时间", null=True, blank=True)
    elapsed_time = models.IntegerField("节点执行耗时(秒)", null=True, blank=True)
    
    # 执行状态
    status = models.BooleanField("是否执行成功", default=False)
    state = models.CharField("节点状态", max_length=32, default="", db_index=True)
    is_skip = models.BooleanField("是否跳过", default=False)
    is_retry = models.BooleanField("是否重试记录", default=False)
    retry_count = models.IntegerField("重试次数", default=0)
    
    # 任务实例时间
    task_create_time = models.DateTimeField("任务创建时间", db_index=True)
    task_start_time = models.DateTimeField("任务启动时间", null=True, blank=True)
    task_finish_time = models.DateTimeField("任务结束时间", null=True, blank=True)
    
    class Meta:
        verbose_name = "节点执行统计"
        verbose_name_plural = "节点执行统计"
        indexes = [
            models.Index(fields=['space_id', 'component_code', 'started_time']),
            models.Index(fields=['task_id', 'node_id']),
            models.Index(fields=['component_code', 'status', 'started_time']),
        ]
```

---

**文档版本**: v1.0  
**创建日期**: 2026-01-15  
**基于分析**: bk-sops gcloud/analysis_statistics 模块

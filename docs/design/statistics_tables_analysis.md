# 统计表数据来源与触发逻辑分析

## 概述

本文档分析了 `gcloud.analysis_statistics` 模块中几个主要统计表的数据来源、统计逻辑和触发时机。

## 主要统计表

### 1. TaskflowExecutedNodeStatistics（标准插件执行数据）

**表作用**：记录每个标准插件（包括第三方插件）在流程实例中的执行情况。

**数据来源**：
- 主要代码：`gcloud/analysis_statistics/tasks.py` 中的 `pipeline_archive_statistics_task()` 函数
- 数据收集函数：`recursive_collect_components_execution()` 函数

**统计逻辑**：
1. 当流程实例完成（FINISHED）或撤销（REVOKED）时触发
2. 通过 `TaskCommandDispatcher.get_task_status()` 获取任务执行状态树
3. 递归遍历流程树，收集所有已归档（ARCHIVED_STATES）的标准插件节点
4. 对于每个插件节点，记录：
   - 插件码（component_code）和版本（version）
   - 执行时间（started_time, archived_time, elapsed_time）
   - 执行状态（status: 成功/失败）
   - 是否跳过（is_skip）、是否重试（is_retry）
   - 项目ID（project_id）、模板ID（template_id）等
   - 是否第三方插件（is_remote）
5. 对于有重试记录的节点，会从执行历史中获取每次重试的数据
6. 对于子流程中的插件，会记录子流程堆栈（subprocess_stack）

**触发时机**：
- 信号：`post_pipeline_finish`（流程完成）
- 信号：`post_pipeline_revoke`（流程撤销）
- 信号处理器：`gcloud/analysis_statistics/signals/handlers.py` 中的 `pipeline_instance_finish_handler()` 和 `pipeline_instance_revoke_handler()`
- 执行方式：异步 Celery 任务 `pipeline_archive_statistics_task.delay()`

**关键代码位置**：
```python
# 信号注册
@receiver(post_pipeline_finish, sender=PipelineInstance)
def pipeline_instance_finish_handler(sender, instance_id, **kwargs):
    pipeline_archive_statistics_task.delay(instance_id=instance_id)

# 数据收集
def recursive_collect_components_execution(activities, status_tree, task_instance, engine_ver=1, stack=None):
    # 递归收集插件执行数据
    # ...
    TaskflowExecutedNodeStatistics.objects.bulk_create(component_list)
```

---

### 2. TemplateNodeStatistics（标准插件被引用数据）

**表作用**：记录模板中引用的标准插件信息，包括直接引用和通过子流程间接引用。

**数据来源**：
- 主要代码：`gcloud/analysis_statistics/tasks.py` 中的 `tasktemplate_post_save_statistics_task()` 函数

**统计逻辑**：
1. 当模板保存时触发
2. 遍历模板的所有活动节点（activities）
3. 对于标准插件节点（ServiceActivity）：
   - 提取插件码和版本
   - 判断是否为第三方插件（component_code == "remote_plugin"）
   - 如果是第三方插件，提取实际的 plugin_code 和 plugin_version
   - 创建 TemplateNodeStatistics 记录
4. 对于子流程节点（SubProcess）：
   - 查找子流程模板中已统计的插件
   - 递归处理子流程中的插件，记录子流程堆栈
   - 标记为间接引用（is_sub=True）

**触发时机**：
- 信号：`task_template_signals.post_template_save_commit`（模板保存提交后）
- 信号处理器：`gcloud/analysis_statistics/signals/handlers.py` 中的 `task_template_post_save_commit_handler()`
- 执行方式：异步 Celery 任务 `tasktemplate_post_save_statistics_task.delay()`

**关键代码位置**：
```python
# 信号注册
@receiver(task_template_signals.post_template_save_commit, sender=TaskTemplate)
def task_template_post_save_commit_handler(sender, project_id, template_id, is_deleted, **kwargs):
    if not is_deleted:
        tasktemplate_post_save_statistics_task.delay(template_id)

# 数据收集
def tasktemplate_post_save_statistics_task(template_id):
    # 删除旧数据
    TemplateNodeStatistics.objects.filter(task_template_id=task_template_id).delete()
    # 收集插件引用数据
    # ...
    TemplateNodeStatistics.objects.bulk_create(component_list)
```

---

### 3. TaskflowStatistics（Pipeline实例引用数据）

**表作用**：记录流程实例的基本统计信息，包括插件总数、子流程总数、网关总数等。

**数据来源**：
- 主要代码：`gcloud/analysis_statistics/tasks.py` 中的 `taskflowinstance_post_save_statistics_task()` 函数

**统计逻辑**：
1. 当任务实例（TaskFlowInstance）创建或更新时触发
2. 统计流程中的节点数量：
   - 标准插件总数（atom_total）
   - 子流程总数（subprocess_total）
   - 网关总数（gateways_total）
3. 记录实例的基本信息：
   - 创建时间、启动时间、结束时间
   - 执行耗时（elapsed_time）
   - 创建方式（create_method）
   - 项目ID、模板ID等

**触发时机**：
- 信号：`post_save`（TaskFlowInstance 保存时）
- 信号处理器：`gcloud/analysis_statistics/signals/handlers.py` 中的 `task_flow_post_save_handler()`
- 执行方式：异步 Celery 任务 `taskflowinstance_post_save_statistics_task.delay()`

**关键代码位置**：
```python
# 信号注册
@receiver(post_save, sender=TaskFlowInstance)
def task_flow_post_save_handler(sender, instance, created, **kwargs):
    taskflowinstance_post_save_statistics_task.delay(instance.id, created)

# 数据统计
def taskflowinstance_post_save_statistics_task(task_instance_id, created):
    # 统计节点数量
    atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(
        pipeline_instance.execution_data
    )
    if created:
        TaskflowStatistics.objects.create(**kwargs)
    else:
        TaskflowStatistics.objects.filter(task_instance_id=task_instance_id).update(**kwargs)
```

---

### 4. TemplateStatistics（Pipeline模板引用数据）

**表作用**：记录模板的基本统计信息，包括插件总数、子流程总数、网关总数、变量数量等。

**数据来源**：
- 主要代码：`gcloud/analysis_statistics/tasks.py` 中的 `tasktemplate_post_save_statistics_task()` 函数

**统计逻辑**：
1. 当模板保存时触发（与 TemplateNodeStatistics 同时触发）
2. 统计模板中的节点数量：
   - 标准插件总数（atom_total）
   - 子流程总数（subprocess_total）
   - 网关总数（gateways_total）
3. 统计模板中的变量数量：
   - 输入变量数（input_count）
   - 输出变量数（output_count）
4. 记录模板的基本信息：
   - 创建时间、编辑时间
   - 创建者、项目ID等

**触发时机**：
- 信号：`task_template_signals.post_template_save_commit`（模板保存提交后）
- 信号处理器：`gcloud/analysis_statistics/signals/handlers.py` 中的 `task_template_post_save_commit_handler()`
- 执行方式：异步 Celery 任务 `tasktemplate_post_save_statistics_task.delay()`

**关键代码位置**：
```python
# 数据统计（在 tasktemplate_post_save_statistics_task 函数中）
atom_total, subprocess_total, gateways_total = count_pipeline_tree_nodes(data)
# 统计变量数量
for constant in data[PE.constants].values():
    if constant["source_type"] == "component_outputs":
        output_count += 1
    else:
        input_count += 1
# 更新或创建记录
TemplateStatistics.objects.update_or_create(
    task_template_id=task_template_id,
    defaults={...}
)
```

---

### 5. TemplateVariableStatistics（流程模板变量统计数据）

**表作用**：记录模板中使用的变量信息。

**数据来源**：
- 主要代码：`gcloud/analysis_statistics/variable.py` 中的 `update_statistics()` 函数
- 定时任务：`gcloud/analysis_statistics/tasks.py` 中的 `backfill_template_variable_statistics_task()`

**统计逻辑**：
1. 当模板保存时，通过 `tasktemplate_post_save_statistics_task()` 间接调用
2. 分析模板中的变量（constants）
3. 记录变量的类型、来源、被引用次数等

**触发时机**：
- 模板保存时（通过 `tasktemplate_post_save_statistics_task()`）
- 定时任务：每天凌晨1点执行 `backfill_template_variable_statistics_task()` 进行数据补充

---

## 信号注册机制

所有信号处理器都在应用启动时自动注册：

**注册位置**：`gcloud/analysis_statistics/apps.py`

```python
class AnalysisStatisticsConfig(AppConfig):
    def ready(self):
        # 导入信号处理器，触发装饰器注册
        from gcloud.analysis_statistics.signals.handlers import (
            task_flow_post_save_handler,
            task_template_post_save_commit_handler,
            pipeline_instance_finish_handler,
            pipeline_instance_revoke_handler,
        )
```

## 数据流程总结

### 模板相关统计（TemplateNodeStatistics, TemplateStatistics）

```
用户保存模板
    ↓
TaskTemplate.save()
    ↓
发送信号: post_template_save_commit
    ↓
task_template_post_save_commit_handler()
    ↓
异步任务: tasktemplate_post_save_statistics_task()
    ↓
统计模板中的插件引用 → TemplateNodeStatistics
统计模板基本信息 → TemplateStatistics
```

### 实例相关统计（TaskflowStatistics, TaskflowExecutedNodeStatistics）

```
创建/更新任务实例
    ↓
TaskFlowInstance.save()
    ↓
发送信号: post_save
    ↓
task_flow_post_save_handler()
    ↓
异步任务: taskflowinstance_post_save_statistics_task()
    ↓
统计实例基本信息 → TaskflowStatistics

流程完成/撤销
    ↓
PipelineInstance 状态变更
    ↓
发送信号: post_pipeline_finish / post_pipeline_revoke
    ↓
pipeline_instance_finish_handler() / pipeline_instance_revoke_handler()
    ↓
异步任务: pipeline_archive_statistics_task()
    ↓
收集插件执行数据 → TaskflowExecutedNodeStatistics
```

## 第三方插件识别逻辑

在统计第三方插件时，系统会识别 `component_code == "remote_plugin"` 的节点，然后：

1. **在模板统计中**（TemplateNodeStatistics）：
   ```python
   if component_code == "remote_plugin":
       component_code = act["component"]["data"]["plugin_code"]["value"]
       component_version = act["component"]["data"]["plugin_version"]["value"]
       is_remote = True
   ```

2. **在执行统计中**（TaskflowExecutedNodeStatistics）：
   ```python
   if component_code == "remote_plugin":
       component_code = act["component"]["data"]["plugin_code"]["value"]
       component_version = act["component"]["data"]["plugin_version"]["value"]
       is_remote = True
   ```

这样，第三方插件的实际插件码会被记录在 `component_code` 字段中，`is_remote` 字段标记为 `True`。

## 注意事项

1. **异步执行**：所有统计任务都是异步执行的（通过 Celery），不会阻塞主业务流程
2. **数据删除**：在更新统计前，会先删除旧数据，确保数据一致性
3. **错误处理**：所有统计任务都有异常处理，失败不会影响主业务流程
4. **性能优化**：使用 `bulk_create()` 批量插入数据，提高性能
5. **子流程处理**：递归处理子流程中的插件，记录完整的子流程堆栈信息

## 相关文件清单

- `gcloud/analysis_statistics/models.py` - 统计表模型定义
- `gcloud/analysis_statistics/tasks.py` - 统计任务实现
- `gcloud/analysis_statistics/signals/handlers.py` - 信号处理器
- `gcloud/analysis_statistics/apps.py` - 应用配置（信号注册）
- `gcloud/analysis_statistics/variable.py` - 变量统计逻辑





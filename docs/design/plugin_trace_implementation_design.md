# 插件 Trace 链路追踪实现设计文档

> 本文档汇总 `feat/plugin_trace`、`feat/plugin_trace_v2`、`feat/plugin_trace_v3` 三个分支的实现内容，用于留档记录并作为其他项目实施方案的参考。
>
> 需求 Story: 130572156

## 一、概述

### 1.1 背景与目标

在蓝鲸标准运维（bk-sops）的分布式任务执行系统中，需要为每个插件（节点）构建可观测的 Trace 链路，以实现：

1. **性能监控**：追踪插件执行耗时，定位性能瓶颈
2. **问题排查**：串联 execute 与 schedule 调用，便于失败原因分析
3. **链路连通**：与外部请求的 Trace Context 建立父子关系，实现端到端追踪

### 1.2 核心挑战

- **Trace Context 跨进程传递**：任务启动与插件执行可能不在同一进程，需通过 Pipeline Data 传递
- **跨 Schedule 调用**：异步插件需多次 `schedule` 调用才能完成，需在多次调用间保持同一 Span
- **Span 层级正确性**：Plugin Span 与 Execute/Schedule 方法 Span 需形成正确的父子关系

---

## 二、分支实现演进总结

### 2.1 feat/plugin_trace（V1 - 基础实现）

**主要提交**：`178a60ee95` feat: 构建节点执行的Span

#### 实现内容

| 模块 | 变更说明 |
|------|----------|
| **gcloud/core/trace.py** | 新增 `create_execution_span`、`start_plugin_span`、`end_plugin_span`、`plugin_method_span` 等函数 |
| **gcloud/taskflow3/domains/dispatchers/task.py** | 任务启动时创建 execution span，将 `_trace_id`、`_parent_span_id` 注入 `root_pipeline_data` |
| **pipeline_plugins/base.py** | 新增 `BasePluginService` 基类，统一封装 execute/schedule 的 span 构建逻辑 |
| **内置插件** | 约 40 个插件迁移至 `BasePluginService`（Job、CC、GSE、Notify、Controller、Subprocess 等） |

#### 核心设计

1. **Execution Span**：任务启动时创建 `bk_sops.execution` 作为所有插件 span 的根 span
2. **Trace Context 注入**：`start_v2` 中调用 `create_execution_span`，将返回的 `trace_id`、`execution_span_id` 写入 `root_pipeline_data`
3. **跨 Schedule 持久化**：通过 `data.outputs` 保存 span 起止时间、trace_id、parent_span_id 等，支持多次 schedule 调用
4. **方法级 Span**：`plugin_method_span` 为 execute/schedule 方法创建子 span，用于记录每次调用的执行情况

#### 遗留问题

- execute/schedule 方法 span 的父 span 为 execution span，与 plugin span 同级，层级不符合预期
- 部分插件未继承 `BasePluginService`，无法享受 span 追踪
- `create_execution_span` 缺少业务属性（bk_biz_id、operator、executor）

---

### 2.2 feat/plugin_trace_v2（V2 - 层级与命名修复）

**主要提交**：`db4c2523b8` refactor: 修复内置插件span名称不对的问题 & span层级问题修复

#### 实现内容

| 模块 | 变更说明 |
|------|----------|
| **gcloud/core/trace.py** | 引入 `PLUGIN_SPAN_ID_KEY`、`_generate_span_id()`、`_CustomSpan`、`_create_span_with_custom_id`；`plugin_method_span` 增加 `plugin_span_id` 参数 |
| **pipeline_plugins/base/core.py** | `_get_trace_context` 增加 `plugin_span_id`；execute/schedule 调用时传入 `plugin_span_id` |
| **start_plugin_span** | 预生成 plugin span 的 span_id，写入 `data.outputs`，供 method span 作为父 span 使用 |
| **end_plugin_span** | 使用预生成的 span_id 创建 span（`_create_span_with_custom_id`），保证 method span 的父 span_id 指向正确 |
| **插件覆盖** | Job、CC、Monitor、NodeMan 等插件统一继承 `BasePluginService`，修正 span 名称（驼峰转下划线） |

#### 核心设计

1. **Span 层级修正**：
   - 在 `start_plugin_span` 中预生成 `plugin_span_id`
   - execute/schedule 的 method span 优先使用 `plugin_span_id` 作为父 span
   - 形成 `execution → plugin → execute/schedule` 的三层结构

2. **自定义 Span ID**：
   - OpenTelemetry SDK 的 `Span.__new__` 不允许直接实例化，通过 `_CustomSpan` 子类绕过
   - 使用 `_create_span_with_custom_id` 创建带指定 span_id 的 span，保证父子关系正确

3. **Span 命名规范**：
   - `_get_span_name()` 使用 `_camel_to_snake` 将类名转换（如 `JobExecuteTaskService` → `job_execute_task`）
   - 格式：`{platform_code}.plugin.{plugin_name}`

---

### 2.3 feat/plugin_trace_v3（V3 - 兼容性与清理）

**主要提交**：
- `e62b8dcbed` 修复部分插件没有继承 BasePluginService & 修复 execute/schedule 返回 None 导致误判失败
- `dac8c9c4fc` 修复 execute 和 schedule 的父 span 不对的问题
- `cf4f84799c` approve 插件补充调用 finish_schedule
- `59fa41056d` 调整 span 属性的内容
- `6e67741cd9` 流程结束后清理 span 相关内置属性

#### 实现内容

| 模块 | 变更说明 |
|------|----------|
| **CC 插件** | `batch_transfer_host_module`、`host_lock`、`transfer_host_module` 等改为继承 `BasePluginService` |
| **Job 插件** | `local_content_upload`、`job/base` 等确保继承 `BasePluginService` |
| **NodeMan 插件** | `nodeman/base`、`create_task/legacy` 等补充继承关系 |
| **Approve 插件** | 在 `plugin_schedule` 回调中补充 `self.finish_schedule()` 调用 |
| **BasePluginService** | 修正 `is_schedule_finished` 判断逻辑，兼容 `return None` 与 `__need_schedule__` |
| **gcloud/core/trace.py** | `create_execution_span` 增加 bk_biz_id、operator、executor；移除冗余 success/error 属性；新增 `clean_plugin_span_outputs` |
| **pipeline_plugins/base/core.py** | `_end_plugin_span` 后调用 `clean_plugin_span_outputs(data)` 清理 outputs |

#### 核心设计

1. **finish_schedule 规范**：需要 schedule 的插件，在调度完成时必须调用 `self.finish_schedule()`，否则 `BasePluginService` 无法正确结束 plugin span

2. **Span 属性精简**：
   - `create_execution_span` 支持 `bk_biz_id`、`operator`、`executor`
   - 移除 span 上的 `plugin.success`、`plugin.error` 等冗余属性，仅保留 Status

3. **Output 清理**：流程结束后，从 `data.outputs` 中移除 `_plugin_span_*` 等内部属性，避免污染用户可见的任务输出

---

## 三、技术架构设计

### 3.1 整体链路

```
外部请求 / 定时任务 / API 网关
    ↓ [可选的 Trace Context]
任务启动 (TaskCommandDispatcher.start_v2)
    ↓ create_execution_span()
Execution Span (bk_sops.execution) [立即结束，作为根 span]
    ↓ 注入 _trace_id, _parent_span_id 到 root_pipeline_data
节点执行 (BasePluginService.execute / schedule)
    ↓ _start_plugin_span() → start_plugin_span()
Plugin Span 信息写入 data.outputs（跨 schedule 持久化）
    ↓ plugin_method_span(plugin_span_id=...)
Execute/Schedule 方法 Span (bk_sops.plugin.{name}.execute|schedule)
    ↓ _end_plugin_span() → end_plugin_span()
Plugin Span 创建并结束
    ↓ clean_plugin_span_outputs()
清理 data.outputs 中的 span 内部属性
```

### 3.2 核心组件

#### 3.2.1 create_execution_span

**位置**：`gcloud/core/trace.py`

**作用**：在任务启动时创建 execution span，作为所有插件 span 的根。

**参数**：task_id, project_id, pipeline_instance_id, bk_biz_id, operator, executor

**返回**：`(trace_id_hex, span_id_hex)`，供注入 `root_pipeline_data` 使用。

**注意**：该 span 创建后立即结束，仅用于建立 trace 根和传递 context。

#### 3.2.2 start_plugin_span / end_plugin_span

**作用**：
- `start_plugin_span`：记录开始时间、trace context，预生成 `plugin_span_id`，写入 `data.outputs`
- `end_plugin_span`：从 `data.outputs` 恢复信息，创建并结束 plugin span

**跨 Schedule 机制**：span 元数据保存在 `data.outputs`，随节点数据持久化，多次 schedule 调用可共享同一 span。

**Output Keys**：
- `_plugin_span_start_time_ns`
- `_plugin_span_name`
- `_plugin_span_trace_id`
- `_plugin_span_parent_span_id`
- `_plugin_span_id`（预生成的 plugin span ID）
- `_plugin_span_attributes`
- `_plugin_span_ended`
- `_plugin_schedule_count`

#### 3.2.3 plugin_method_span

**作用**：为 `plugin_execute` 和 `plugin_schedule` 创建方法级 span。

**父 Span 选择**：优先使用 `plugin_span_id`，缺失时使用 `parent_span_id`（execution span）。

**Span 名称**：`{platform_code}.plugin.{plugin_name}.{execute|schedule}`

#### 3.2.4 BasePluginService

**位置**：`pipeline_plugins/base/core.py`

**职责**：
- 统一 execute/schedule 的 span 构建流程
- 提供 `_get_span_name`、`_get_span_attributes` 等可覆盖方法
- 通过 `enable_plugin_span` 控制是否启用追踪

**子类约定**：
- 实现 `plugin_execute`、`plugin_schedule` 而非重写 `execute`、`schedule`
- 需要 schedule 的插件，完成时需调用 `self.finish_schedule()`

---

## 四、实施指南（供其他项目参考）

### 4.1 前置条件

- 使用 OpenTelemetry 进行链路追踪
- 已配置 `ENABLE_OTEL_TRACE`
- 存在「任务启动 → 节点执行」的 pipeline 模型，且支持通过 data 传递上下文

### 4.2 实施步骤

1. **任务启动注入 Trace Context**
   - 在任务启动入口创建 execution span 或从外部获取 trace context
   - 将 `trace_id`、`parent_span_id` 写入 root pipeline data（如 `_trace_id`、`_parent_span_id`）

2. **引入 BasePluginService**
   - 定义插件基类，在 execute/schedule 中调用 `_start_plugin_span`、`_end_plugin_span`
   - 使用 `plugin_method_span` 包裹 `plugin_execute`、`plugin_schedule`

3. **跨 Schedule 持久化**
   - 将 span 起止时间、trace_id、parent_span_id、plugin_span_id 等写入 `data.outputs`
   - 在 `end_plugin_span` 时从 outputs 恢复并创建 span

4. **Span 层级处理**
   - 预生成 plugin span 的 span_id
   - execute/schedule 的 method span 以 plugin span 为父 span
   - 如 SDK 限制直接实例化 Span，可采用 `_CustomSpan` 等方式创建带自定义 span_id 的 span

5. **Output 清理**
   - 在 plugin span 结束后，从 `data.outputs` 中移除 span 相关内部 key，避免暴露给用户

### 4.3 插件迁移清单

| 类型 | 操作 |
|------|------|
| 同步插件 | 继承 BasePluginService，实现 `plugin_execute`，无需 `finish_schedule` |
| 异步插件 | 继承 BasePluginService，实现 `plugin_execute` 与 `plugin_schedule`，完成时调用 `self.finish_schedule()` |
| 基类插件 | 若插件有共同基类，确保基类继承 BasePluginService，或各实现类显式继承 |

### 4.4 注意事项

- **finish_schedule**：异步插件必须在调度完成时调用，否则 plugin span 无法正确结束
- **返回值**：`plugin_execute`/`plugin_schedule` 返回 `None` 时，需结合 `__need_schedule__` 等逻辑，避免误判为失败
- **Python 兼容**：使用 `time.time_ns()` 时注意 Python 版本兼容（可用 `int(time.time() * 1e9)` 替代）
- **属性序列化**：写入 `data.outputs` 的属性需可序列化，建议转为字符串

---

## 五、核心文件清单

| 文件路径 | 职责 |
|----------|------|
| `gcloud/core/trace.py` | execution span、plugin span、method span 的创建与结束；`clean_plugin_span_outputs` |
| `gcloud/taskflow3/domains/dispatchers/task.py` | 任务启动时调用 `create_execution_span`，注入 trace context |
| `pipeline_plugins/base/core.py` | `BasePluginService` 基类，封装 span 生命周期 |

---

## 六、分支提交摘要

| 分支 | 关键提交 | 说明 |
|------|----------|------|
| feat/plugin_trace | 178a60ee95 | 构建节点执行的 Span，引入 BasePluginService |
| feat/plugin_trace | 65842b2e05 | plugin execute/schedule 的 span 名称格式调整 |
| feat/plugin_trace | 8b8df64352 | Python 版本兼容修复 |
| feat/plugin_trace_v2 | db4c2523b8 | 修复 span 层级与内置插件 span 名称 |
| feat/plugin_trace_v3 | e62b8dcbed | 修复插件继承与 return None 误判 |
| feat/plugin_trace_v3 | dac8c9c4fc | 修复 execute/schedule 父 span 不正确 |
| feat/plugin_trace_v3 | cf4f84799c | Approve 插件补充 finish_schedule |
| feat/plugin_trace_v3 | 59fa41056d | 调整 span 属性内容 |
| feat/plugin_trace_v3 | 6e67741cd9 | 流程结束后清理 span 相关 output |

---

## 七、版本与参考

- **项目**：蓝鲸标准运维 (bk-sops)
- **需求**：Story 130572156
- **分支**：feat/plugin_trace → feat/plugin_trace_v2 → feat/plugin_trace_v3
- **文档日期**：2026-02

---

*本文档基于 feat/plugin_trace_v3 及后续演进整理，可作为其他流程/工作流项目引入插件 Trace 的参考实现。*

# 基于 Span 的 Trace 事件异步上报实现

## 一、背景与需求

在 `feat/plugin_trace`、`feat/plugin_trace_v2`、`feat/plugin_trace_v3` 分支已实现流程自身的 Span（`{platform_code}.execution`）和节点级 Span 的基础上，需要将以下事件通过 Celery 异步上报到蓝鲸监控：

- 流程开始执行
- 流程的操作（pause/resume/revoke）
- 流程结束（成功执行）
- 流程某个节点失败导致的中断
- 每个节点开始和结束（成功或失败）

**约束**：Celery 异步上报需使用**独立队列**（`trace_event_report`），与业务队列隔离。

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        事件触发点（同步）                                │
├─────────────────────────────────────────────────────────────────────────┤
│  taskflow_started  │  TaskCommandDispatcher  │  post_set_state  │       │
│  execute_interrupt │  schedule_interrupt     │                   │       │
└────────────────────────────┬────────────────────────────────────────────┘
                             │ report_trace_event_async()
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Celery 队列: trace_event_report                        │
│                    （与 er_execute、task_callback 等隔离）                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    report_trace_event 任务                                │
│                    → bk_monitor_report.report_event()                    │
│                    → 蓝鲸监控自定义事件上报                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 三、涉及文件与变更

### 3.1 新增文件

| 文件路径 | 说明 |
|---------|------|
| `gcloud/core/trace_report.py` | Trace 事件上报模块：trace context 存储、事件异步上报入口 |
| `gcloud/taskflow3/signals/trace_report_handlers.py` | `taskflow_started` 信号处理，上报 flow_start |

### 3.2 修改文件

| 文件路径 | 变更说明 |
|---------|----------|
| `gcloud/taskflow3/celery/settings.py` | 新增 `trace_event_report` 队列 |
| `gcloud/taskflow3/celery/tasks.py` | 新增 `report_trace_event` Celery 任务 |
| `config/default.py` | 新增 `report_trace_event` 的 Celery 路由 |
| `gcloud/taskflow3/domains/dispatchers/task.py` | 存储 trace context、发送 taskflow_started 时传入 trace 信息、flow_operation 成功后上报 |
| `gcloud/taskflow3/signals/handlers.py` | post_set_state、execute_interrupt、schedule_interrupt 中增加 trace 事件上报 |
| `gcloud/taskflow3/apps.py` | 注册 `taskflow_started_trace_report_handler` |
| `app_desc.yaml` | CELERY_EXPORTER_QUEUE 和 cworker 增加 `trace_event_report` |
| `support-files/supervisord.conf` | celery_addtional_task worker 增加 `trace_event_report` 队列 |

---

## 四、事件类型与埋点

### 4.1 事件类型常量

| 常量名 | 事件类型 | 说明 |
|-------|----------|------|
| `EVENT_FLOW_START` | flow_start | 流程开始执行 |
| `EVENT_FLOW_OPERATION` | flow_operation | 流程操作（pause/resume/revoke）|
| `EVENT_FLOW_FINISH_SUCCESS` | flow_finish_success | 流程成功结束 |
| `EVENT_FLOW_INTERRUPT` | flow_interrupt | 流程中断（节点失败导致）|
| `EVENT_NODE_START` | node_start | 节点开始执行 |
| `EVENT_NODE_FINISH` | node_finish | 节点结束（成功或失败）|

### 4.2 埋点映射

| 事件类型 | 触发信号/位置 | 条件 |
|---------|----------------|------|
| **flow_start** | `taskflow_started` | 流程启动成功（start_v1/start_v2）|
| **flow_operation** | `TaskCommandDispatcher.dispatch()` | pause/resume/revoke 操作成功且返回 `result=True` |
| **flow_finish_success** | `post_set_state` | `to_state=FINISHED` 且 `node_id=root_id` |
| **flow_interrupt** | `execute_interrupt` | 节点 execute 阶段异常 |
| **flow_interrupt** | `schedule_interrupt` | 节点 schedule 阶段异常 |
| **flow_interrupt** | `post_set_state` | `to_state=FAILED` 且 `node_id=root_id` |
| **node_start** | `post_set_state` | `to_state=RUNNING` |
| **node_finish** | `post_set_state` | `to_state=FINISHED` 或 `FAILED` |

### 4.3 事件维度（dimension）

通用维度：

- `task_id`：任务 ID
- `project_id`：项目 ID
- `pipeline_instance_id` / `root_id`：根 Pipeline 实例 ID
- `trace_id`：Trace ID（来自 execution span）
- `execution_span_id`：Execution Span ID
- `node_id`：节点 ID（节点相关事件）
- `node_name`：节点名称（节点相关事件）

事件特有维度：

- **flow_operation**：`operation`（pause/resume/revoke）
- **flow_interrupt**：`cause`（execute_interrupt/schedule_interrupt/node_failed）、`process_id`、`traceback`
- **node_finish**：`success`（true/false）
- **node_start / node_finish**：`version`（节点版本）

---

## 五、Trace Context 存储

由于 `post_set_state` 等场景无法直接从 `parent_data` 获取 trace context，采用 Redis 存储：

- **Key**：`trace_context:{root_id}`（root_id 即 pipeline_instance_id）
- **Value**：`{"trace_id": "...", "execution_span_id": "..."}`
- **TTL**：7 天（86400 * 7 秒）

**写入时机**：`create_execution_span` 成功时（`start_v2` 中）

**读取时机**：`report_trace_event_async` 中，当未直接传入 `trace_id` 且存在 `root_id` 时

---

## 六、队列与 Worker 配置

### 6.1 队列定义

```python
# gcloud/taskflow3/celery/settings.py
Queue(
    "trace_event_report",
    Exchange("default", type="direct"),
    routing_key="trace_event_report",
    queue_arguments={"x-max-priority": 255},
)
```

### 6.2 任务路由

```python
# config/default.py
CELERY_ROUTES.update(
    {"gcloud.taskflow3.celery.tasks.report_trace_event": {"queue": "trace_event_report"}}
)
```

### 6.3 Worker 消费

`trace_event_report` 由 `cworker`（common_worker）消费，与以下队列一起处理：

- pipeline_additional_task
- pipeline_additional_task_priority
- node_auto_retry
- timeout_node_execute
- timeout_nodes_record
- task_callback
- **trace_event_report**（新增）

---

## 七、蓝鲸监控上报格式

- **事件名称**：`{platform_code}.trace.{event_type}`（如 `bk_sops.trace.flow_start`）
- **上报方式**：`bk_monitor_report.MonitorReporter.report_event()`
- **前置条件**：`env.BK_MONITOR_REPORT_ENABLE == True`

蓝鲸监控相关环境变量（`env.py`）：

- `MONITOR_REPORT_ENABLE`
- `MONITOR_REPORT_URL`
- `MONITOR_REPORT_DATA_ID`
- `MONITOR_REPORT_ACCESS_TOKEN`
- `MONITOR_REPORT_TARGET`

---

## 八、调用流程示例

### 8.1 流程开始

```
start_v2()
  → create_execution_span()
  → store_trace_context(root_id, trace_id, execution_span_id)
  → run_pipeline()
  → taskflow_started.send(trace_id=..., execution_span_id=...)
  → taskflow_started_trace_report_handler
  → report_trace_event_async(EVENT_FLOW_START, ...)
  → report_trace_event.apply_async(queue="trace_event_report")
```

### 8.2 节点状态变更

```
post_set_state(node_id, to_state=RUNNING/FINISHED/FAILED, root_id, ...)
  → bamboo_engine_eri_post_set_state_handler
  → _get_taskflow_and_node_name(root_id, node_id)
  → report_trace_event_async(EVENT_NODE_START / NODE_FINISH / FLOW_FINISH_SUCCESS / FLOW_INTERRUPT, ...)
  → get_trace_context(root_id)  # 从 Redis 获取 trace_id
  → report_trace_event.apply_async(queue="trace_event_report")
```

### 8.3 流程中断（execute/schedule 异常）

```
execute_interrupt / schedule_interrupt
  → execute_interrupt_handler / schedule_interrupt_handler
  → _report_interrupt_event(...)  # 保留原有同步上报
  → Process.objects.filter(id=event.process_id).values_list("root_pipeline_id")
  → report_trace_event_async(EVENT_FLOW_INTERRUPT, ...)
  → report_trace_event.apply_async(queue="trace_event_report")
```

---

## 九、依赖关系

- **bk-monitor-report**：`requirements.txt` 中 `bk-monitor-report==1.2.1`
- **Span 能力**：依赖 `create_execution_span`、`store_trace_context`（仅在 v2 引擎且 `ENABLE_OTEL_TRACE` 时创建 trace context）
- **Redis**：用于 trace context 缓存

---

## 十、部署与启用

1. 配置蓝鲸监控上报：`MONITOR_REPORT_ENABLE=1` 及对应 URL、Data ID、Token、Target
2. 确认 cworker / celery_addtional_task 已包含 `trace_event_report` 队列
3. 重启 Celery worker 后生效

---

## 十一、与原有监控上报的关系

| 对比项 | 原有 `_report_interrupt_event` | 新增 Trace 事件上报 |
|--------|-------------------------------|---------------------|
| 触发事件 | execute_interrupt、schedule_interrupt | 上述 + flow_start、flow_operation、flow_finish、node_start、node_finish |
| 执行方式 | 同步（信号处理器内直接调用） | 异步（Celery `trace_event_report` 队列） |
| 队列 | 无 | `trace_event_report` |
| 事件命名 | `execute_interrupt` / `schedule_interrupt` | `{platform_code}.trace.{event_type}` |

原有 `_report_interrupt_event` 逻辑保持不变，新增的 trace 事件上报与其并行存在。

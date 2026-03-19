# PR 593: 构建节点调用的span - 技术实现总结

## 一、背景与问题

### 1.1 问题描述
在分布式任务执行系统中，需要追踪每个节点（插件）的执行情况，以便进行性能监控、问题排查和链路追踪。原有的实现存在以下问题：

1. **Trace Context 传递不完整**：节点执行时无法正确获取父级 trace context，导致 span 之间无法建立正确的父子关系
2. **跨 Schedule 调用追踪困难**：节点可能需要多次 schedule 调用才能完成，需要在多次调用间保持 trace 连续性
3. **Span 构建逻辑分散**：节点调用的 span 构建逻辑不够统一，难以维护和扩展

### 1.2 目标
- 建立完整的 trace context 传递链路
- 支持跨 schedule 调用的 span 追踪
- 统一节点调用的 span 构建逻辑
- 支持自定义 span 属性

## 二、技术实现

### 2.1 整体架构

```
外部请求 (带 Trace Context)
    ↓
任务启动 (TaskOperation.start)
    ↓ [捕获 Trace Context]
注入到 Pipeline Data (_trace_id, _parent_span_id)
    ↓
节点执行 (BKFlowBaseService.execute/schedule)
    ↓ [获取 Trace Context]
构建节点 Span (start_plugin_span)
    ↓ [保存到 data.outputs]
跨 Schedule 调用保持连续性
    ↓ [重建 Parent Context]
结束节点 Span (end_plugin_span)
```

### 2.2 核心组件

#### 2.2.1 Trace Context 传递机制

**位置**: `bkflow/task/operations.py`

在任务启动时捕获外部的 trace context，并注入到 pipeline 的执行数据中：

```python
@trace_task_operation("start")
def start(self, operator: str, *args, **kwargs):
    # 捕获当前 trace context，传递给 pipeline 执行环境
    if settings.ENABLE_OTEL_TRACE:
        # 优先使用外部传入的 trace context（在装饰器创建 span 之前获取的）
        trace_context = kwargs.get("_external_trace_context")
        if trace_context:
            root_pipeline_data["_trace_id"] = trace_context["trace_id"]
            root_pipeline_data["_parent_span_id"] = trace_context["span_id"]
```

**关键点**：
- 使用装饰器 `trace_task_operation` 在创建新 span 之前获取外部 trace context
- 通过 `_external_trace_context` 参数传递，避免使用装饰器创建的 span 的 context
- 将 trace_id 和 parent_span_id 注入到 `root_pipeline_data` 中

#### 2.2.2 节点 Span 构建

**位置**: `bkflow/pipeline_plugins/components/collections/base.py`

在插件基类 `BKFlowBaseService` 中实现统一的 span 构建逻辑：

**1. 获取 Trace Context**
```python
def _get_trace_context(self, parent_data):
    """从 parent_data 中获取 trace context"""
    return {
        "trace_id": parent_data.get_one_of_inputs("_trace_id"),
        "parent_span_id": parent_data.get_one_of_inputs("_parent_span_id"),
    }
```

**2. 启动节点 Span**
```python
def _start_plugin_span(self, data, parent_data):
    """启动插件执行 Span"""
    if not self.enable_plugin_span or not settings.ENABLE_OTEL_TRACE:
        return

    span_name = self._get_span_name()
    attributes = self._get_span_attributes(data, parent_data)

    trace_id = parent_data.get_one_of_inputs("_trace_id")
    parent_span_id = parent_data.get_one_of_inputs("_parent_span_id")

    start_plugin_span(
        span_name=span_name,
        data=data,
        trace_id=trace_id,
        parent_span_id=parent_span_id,
        **attributes,
    )
    data.set_outputs(PLUGIN_SPAN_ENDED_KEY, False)
```

**3. 结束节点 Span**
```python
def _end_plugin_span(self, data, success, error_message=None):
    """结束插件执行 Span（确保只调用一次）"""
    if not self.enable_plugin_span or not settings.ENABLE_OTEL_TRACE:
        return

    if data.get_one_of_outputs(PLUGIN_SPAN_ENDED_KEY, False):
        return  # 幂等保护

    end_plugin_span(data, success=success, error_message=error_message)
    data.set_outputs(PLUGIN_SPAN_ENDED_KEY, True)
```

**4. Execute 方法集成**
```python
def execute(self, data, parent_data):
    self._start_plugin_span(data, parent_data)

    trace_context = self._get_trace_context(parent_data)
    method_attrs = self._get_method_span_attributes(data, parent_data)

    if self.enable_plugin_span and settings.ENABLE_OTEL_TRACE:
        with plugin_method_span(
            method_name="execute",
            trace_id=trace_context.get("trace_id"),
            parent_span_id=trace_context.get("parent_span_id"),
            **method_attrs,
        ) as span_result:
            result = self.plugin_execute(data, parent_data)
            if not result:
                span_result.set_error(self._get_error_message(data))
    else:
        result = self.plugin_execute(data, parent_data)

    if not result:
        self._end_plugin_span(data, success=False, error_message=self._get_error_message(data))
    elif not self.need_schedule():
        self._end_plugin_span(data, success=True)

    return result
```

**5. Schedule 方法集成**
```python
def schedule(self, data, parent_data, callback_data=None):
    trace_context = self._get_trace_context(parent_data)
    method_attrs = self._get_method_span_attributes(data, parent_data)

    if self.enable_plugin_span and settings.ENABLE_OTEL_TRACE:
        schedule_count = data.get_one_of_outputs(PLUGIN_SCHEDULE_COUNT_KEY, 0) + 1
        data.set_outputs(PLUGIN_SCHEDULE_COUNT_KEY, schedule_count)
        method_attrs["schedule_count"] = schedule_count

        with plugin_method_span(
            method_name="schedule",
            trace_id=trace_context.get("trace_id"),
            parent_span_id=trace_context.get("parent_span_id"),
            **method_attrs,
        ) as span_result:
            result = self.plugin_schedule(data, parent_data, callback_data)
            if not result:
                span_result.set_error(self._get_error_message(data))
    else:
        result = self.plugin_schedule(data, parent_data, callback_data)

    if not result:
        self._end_plugin_span(data, success=False, error_message=self._get_error_message(data))
    elif self.is_schedule_finished():
        self._end_plugin_span(data, success=True)

    return result
```

#### 2.2.3 Span 生命周期管理

**位置**: `bkflow/utils/trace.py`

**1. 启动 Span（跨 Schedule 支持）**
```python
def start_plugin_span(
    span_name: str,
    data,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
    **attributes,
) -> int:
    """
    记录插件Span的开始时间，将相关信息保存到data outputs中，用于跨schedule调用追踪
    """
    start_time_ns = time.time_ns()

    # 将span信息保存到data outputs中，以便在schedule中使用
    data.set_outputs(PLUGIN_SPAN_START_TIME_KEY, start_time_ns)
    data.set_outputs(PLUGIN_SPAN_NAME_KEY, span_name)

    # 保存 trace context，用于在 end_plugin_span 时重建 parent 关系
    if trace_id:
        data.set_outputs(PLUGIN_SPAN_TRACE_ID_KEY, trace_id)
    if parent_span_id:
        data.set_outputs(PLUGIN_SPAN_PARENT_SPAN_ID_KEY, parent_span_id)

    # 确保属性值可以序列化
    serializable_attributes = {k: str(v) if v is not None else "" for k, v in attributes.items()}
    data.set_outputs(PLUGIN_SPAN_ATTRIBUTES_KEY, serializable_attributes)

    return start_time_ns
```

**关键点**：
- 将 span 信息保存到 `data.outputs` 中，实现跨 schedule 调用的持久化
- 保存 trace_id 和 parent_span_id，用于后续重建 parent context
- 属性值序列化为字符串，确保可以持久化

**2. 结束 Span**
```python
def end_plugin_span(
    data,
    success: bool = True,
    error_message: Optional[str] = None,
    end_time_ns: Optional[int] = None,
):
    """
    结束插件Span，创建完整的Span并立即结束
    """
    # 从 data.outputs 中获取保存的 span 信息
    start_time_ns = data.get_one_of_outputs(PLUGIN_SPAN_START_TIME_KEY)
    span_name = data.get_one_of_outputs(PLUGIN_SPAN_NAME_KEY)
    attributes = data.get_one_of_outputs(PLUGIN_SPAN_ATTRIBUTES_KEY) or {}
    trace_id_hex = data.get_one_of_outputs(PLUGIN_SPAN_TRACE_ID_KEY)
    parent_span_id_hex = data.get_one_of_outputs(PLUGIN_SPAN_PARENT_SPAN_ID_KEY)

    if not start_time_ns or not span_name:
        return

    if end_time_ns is None:
        end_time_ns = time.time_ns()

    tracer = trace.get_tracer(__name__)

    # 尝试重建 parent context
    parent_context = _build_parent_context(trace_id_hex, parent_span_id_hex)

    # 创建 span，如果有 parent context 则使用
    span = tracer.start_span(
        name=span_name,
        context=parent_context,  # 如果为 None，则创建新的 trace
        start_time=start_time_ns,
        kind=SpanKind.CLIENT,
    )

    # 设置属性
    platform_code = getattr(settings, "PLATFORM_CODE", "bkflow")
    for key, value in attributes.items():
        span.set_attribute(f"{platform_code}.plugin.{key}", value)

    # 设置执行结果状态
    if success:
        span.set_status(Status(StatusCode.OK))
        span.set_attribute(f"{platform_code}.plugin.success", True)
    else:
        span.set_status(Status(StatusCode.ERROR, error_message or "Plugin execution failed"))
        span.set_attribute(f"{platform_code}.plugin.success", False)
        if error_message:
            span.set_attribute(f"{platform_code}.plugin.error", str(error_message)[:1000])

    # 手动结束span，设置结束时间
    span.end(end_time=end_time_ns)
```

**关键点**：
- 从 `data.outputs` 中恢复 span 信息，支持跨 schedule 调用
- 使用保存的开始时间，确保 span 的持续时间准确
- 重建 parent context，维护 trace 链的完整性

**3. 重建 Parent Context**
```python
def _build_parent_context(trace_id_hex: Optional[str], parent_span_id_hex: Optional[str]):
    """
    根据保存的 trace_id 和 parent_span_id 重建 parent context
    """
    if not trace_id_hex or not parent_span_id_hex:
        return None

    try:
        # 将十六进制字符串转换为整数
        trace_id_int = int(trace_id_hex, 16)
        parent_span_id_int = int(parent_span_id_hex, 16)

        # 创建 SpanContext
        parent_span_context = SpanContext(
            trace_id=trace_id_int,
            span_id=parent_span_id_int,
            is_remote=True,
            trace_flags=TraceFlags(0x01),  # SAMPLED
        )

        if not parent_span_context.is_valid:
            return None

        parent_span = NonRecordingSpan(parent_span_context)
        parent_context = trace.set_span_in_context(parent_span)
        return parent_context

    except (ValueError, TypeError) as e:
        logger.debug(f"[plugin_span] Failed to parse trace context: {e}")
        return None
```

**关键点**：
- 将十六进制字符串转换为整数，创建 `SpanContext`
- 使用 `NonRecordingSpan` 创建只读的 parent span
- 设置 `is_remote=True` 和 `SAMPLED` 标志

**4. 方法级别 Span（Execute/Schedule）**
```python
@contextmanager
def plugin_method_span(
    method_name: str,
    trace_id: Optional[str] = None,
    parent_span_id: Optional[str] = None,
    **attributes,
):
    """
    追踪 plugin_execute 和 plugin_schedule 方法的 Span 上下文管理器
    """
    start_time_ns = time.time_ns()

    plugin_name = attributes.get("plugin_name", "unknown")
    task_id = attributes.get("task_id", "unknown")
    node_id = attributes.get("node_id", "unknown")
    schedule_count = attributes.get("schedule_count")

    # 构建 span 名称
    platform_code = getattr(settings, "PLATFORM_CODE", "bkflow")
    span_name = f"{platform_code}.{plugin_name}.{method_name}"

    # 用于存储执行结果的容器
    class SpanResult:
        def __init__(self):
            self.success = True
            self.error_message = None

        def set_error(self, message: str):
            self.success = False
            self.error_message = message

    result = SpanResult()

    try:
        yield result
    finally:
        end_time_ns = time.time_ns()
        tracer = trace.get_tracer(__name__)

        # 尝试重建 parent context
        parent_context = _build_parent_context(trace_id, parent_span_id)

        # 创建 span
        span = tracer.start_span(
            name=span_name,
            context=parent_context,
            start_time=start_time_ns,
            kind=SpanKind.INTERNAL,
        )

        # 设置属性
        platform_code = getattr(settings, "PLATFORM_CODE", "bkflow")
        span.set_attribute(f"{platform_code}.plugin.method", method_name)
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(f"{platform_code}.plugin.{key}", str(value))

        # 设置执行结果状态
        if result.success:
            span.set_status(Status(StatusCode.OK))
            span.set_attribute(f"{platform_code}.plugin.success", True)
        else:
            span.set_status(Status(StatusCode.ERROR, result.error_message or f"{method_name} failed"))
            span.set_attribute(f"{platform_code}.plugin.success", False)
            if result.error_message:
                span.set_attribute(f"{platform_code}.plugin.error", str(result.error_message)[:1000])

        # 结束 span
        span.end(end_time=end_time_ns)
```

**关键点**：
- 使用上下文管理器，确保 span 在方法执行完成后正确结束
- 通过 `SpanResult` 对象收集执行结果，在 finally 块中设置 span 状态
- 支持记录 schedule_count，用于追踪多次 schedule 调用

#### 2.2.4 自定义 Span 属性支持

**位置**: `bkflow/pipeline_plugins/components/collections/base.py`

```python
def _get_span_attributes(self, data, parent_data):
    """获取 Span 属性，子类可以覆盖此方法来添加自定义属性"""
    attributes = {
        "space_id": parent_data.get_one_of_inputs("task_space_id"),
        "task_id": parent_data.get_one_of_inputs("task_id"),
        "node_id": self.id,
    }

    # 从 parent_data 中获取 custom_span_attributes，并合并到 Span 属性中
    # custom_span_attributes 通过 TaskContext 从 extra_info.custom_context 传递过来
    custom_span_attributes = parent_data.get_one_of_inputs("custom_span_attributes")
    if custom_span_attributes and isinstance(custom_span_attributes, dict):
        # 将自定义属性合并到基础属性中，自定义属性优先级更高
        attributes.update(custom_span_attributes)

    return attributes
```

**使用示例**（在创建任务时传递自定义属性）：
```python
# 在 create_task API 中
custom_span_attributes = ser.data.get("custom_span_attributes", {})
if custom_span_attributes:
    create_task_data.setdefault("extra_info", {}).setdefault("custom_context", {})["custom_span_attributes"] = custom_span_attributes
```

## 三、解决的问题

### 3.1 Trace Context 传递问题
**问题**：节点执行时无法获取父级 trace context，导致 span 之间无法建立正确的父子关系。

**解决方案**：
- 在任务启动时捕获外部 trace context
- 将 trace_id 和 parent_span_id 注入到 pipeline data 中
- 节点执行时从 parent_data 中获取 trace context

### 3.2 跨 Schedule 调用追踪问题
**问题**：节点可能需要多次 schedule 调用才能完成，需要在多次调用间保持 trace 连续性。

**解决方案**：
- 使用 `start_plugin_span` 将 span 信息保存到 `data.outputs` 中
- 在 `end_plugin_span` 时从 `data.outputs` 恢复 span 信息
- 使用保存的 trace_id 和 parent_span_id 重建 parent context

### 3.3 Span 构建逻辑分散问题
**问题**：节点调用的 span 构建逻辑不够统一，难以维护和扩展。

**解决方案**：
- 在插件基类 `BKFlowBaseService` 中统一实现 span 构建逻辑
- 提供可覆盖的方法（`_get_span_name`, `_get_span_attributes`）支持自定义
- 使用 `enable_plugin_span` 属性控制是否启用 span 追踪

### 3.4 方法级别追踪问题
**问题**：需要追踪 execute 和 schedule 方法的执行情况。

**解决方案**：
- 使用 `plugin_method_span` 上下文管理器追踪方法执行
- 支持记录执行结果和错误信息
- 支持记录 schedule_count，用于追踪多次 schedule 调用

## 四、技术要点总结

### 4.1 设计模式
1. **模板方法模式**：在基类中定义 span 构建的骨架，子类可以覆盖特定方法
2. **上下文管理器模式**：使用 `@contextmanager` 确保 span 的正确创建和结束
3. **策略模式**：通过 `enable_plugin_span` 属性控制是否启用 span 追踪

### 4.2 关键技术点
1. **Trace Context 传递**：通过 pipeline data 传递 trace_id 和 parent_span_id
2. **跨 Schedule 持久化**：使用 data.outputs 保存 span 信息
3. **Parent Context 重建**：使用 `NonRecordingSpan` 和 `SpanContext` 重建 parent context
4. **幂等性保护**：使用 `PLUGIN_SPAN_ENDED_KEY` 确保 span 只结束一次
5. **错误处理**：在 span 创建和结束过程中添加异常处理，确保不影响业务逻辑

### 4.3 可扩展性
1. **自定义 Span 名称**：覆盖 `_get_span_name` 方法
2. **自定义 Span 属性**：覆盖 `_get_span_attributes` 方法或通过 `custom_span_attributes` 传递
3. **禁用 Span 追踪**：设置 `enable_plugin_span = False`

## 五、适用场景

### 5.1 适用项目类型
- 分布式任务执行系统
- 工作流引擎
- 插件化系统
- 需要链路追踪的系统

### 5.2 使用条件
- 使用 OpenTelemetry 进行链路追踪
- 有跨进程/跨调用的 trace context 传递需求
- 需要追踪异步任务的执行情况

## 六、最佳实践

### 6.1 实现步骤
1. **在任务启动时捕获 Trace Context**
   ```python
   trace_context = get_current_trace_context()
   if trace_context:
       pipeline_data["_trace_id"] = trace_context["trace_id"]
       pipeline_data["_parent_span_id"] = trace_context["span_id"]
   ```

2. **在节点基类中实现 Span 构建**
   ```python
   def execute(self, data, parent_data):
       self._start_plugin_span(data, parent_data)
       # ... 执行逻辑 ...
       self._end_plugin_span(data, success=True)
   ```

3. **使用 data.outputs 保存 Span 信息**
   ```python
   data.set_outputs("_plugin_span_start_time_ns", start_time_ns)
   data.set_outputs("_plugin_span_trace_id", trace_id)
   data.set_outputs("_plugin_span_parent_span_id", parent_span_id)
   ```

4. **重建 Parent Context**
   ```python
   parent_context = _build_parent_context(trace_id_hex, parent_span_id_hex)
   span = tracer.start_span(name=span_name, context=parent_context)
   ```

### 6.2 注意事项
1. **确保 Trace Context 格式正确**：trace_id 为 32 位十六进制字符串，span_id 为 16 位十六进制字符串
2. **处理异常情况**：当无法获取或重建 trace context 时，应该创建新的 trace，而不是失败
3. **幂等性保护**：确保 span 只结束一次，避免重复创建
4. **性能考虑**：span 创建和结束不应该影响业务逻辑的执行性能

## 七、参考代码

### 7.1 核心文件
- `bkflow/utils/trace.py`：Trace 工具函数
- `bkflow/pipeline_plugins/components/collections/base.py`：插件基类
- `bkflow/task/operations.py`：任务操作类

### 7.2 测试文件
- `tests/engine/utils/test_trace.py`：Trace 工具函数测试
- `tests/engine/task/test_bkflow_base_plugin_service.py`：插件基类测试
- `tests/engine/task/test_task_operations.py`：任务操作测试

## 八、总结

PR 593 通过以下方式解决了节点调用 span 构建的问题：

1. **建立完整的 Trace Context 传递链路**：从任务启动到节点执行，完整传递 trace context
2. **支持跨 Schedule 调用追踪**：使用 data.outputs 持久化 span 信息，支持多次 schedule 调用
3. **统一 Span 构建逻辑**：在插件基类中统一实现，提供可扩展的接口
4. **支持自定义属性**：通过 `custom_span_attributes` 支持自定义 span 属性

该实现具有良好的可扩展性和可维护性，可以作为其他项目的参考实现。

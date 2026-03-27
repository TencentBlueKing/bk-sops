### 功能描述

统计任务的有效执行时间（排除人工节点）

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   是   |  模板所属业务ID   |
|   task_id     |   string   |   是   |  任务实例ID     |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "task_instance_id": 123456,
        "instance_id": 789012,
        "template_id": "abc123",
        "task_template_id": "456",
        "project_id": 2,
        "creator": "admin",
        "create_method": "app",
        "create_time": "2024-01-01 10:00:00",
        "start_time": "2024-01-01 10:01:00",
        "finish_time": "2024-01-01 10:30:00",
        "total_elapsed_time": 1740,
        "effective_time": 1310,
        "excluded_node_count": 2,
        "total_node_count": 10,
        "excluded_component_codes": ["bk_approve", "pause_node", "sleep_timer", "bot-approval"],
        "category": "Default"
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  code     |    int     |      错误码，0表示成功     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  task_instance_id      |    int    |      任务实例ID    |
|  instance_id      |    int    |      Pipeline实例ID    |
|  template_id      |    string    |      Pipeline模板ID    |
|  task_template_id      |    string    |      任务模板ID    |
|  project_id      |    int    |      项目ID    |
|  creator      |    string    |      创建者    |
|  create_method      |    string    |      任务创建方式（app/api/app_maker/periodic/clocked/mobile）    |
|  create_time      |    string    |      创建时间，格式：YYYY-MM-DD HH:MM:SS    |
|  start_time      |    string    |      启动时间，格式：YYYY-MM-DD HH:MM:SS    |
|  finish_time      |    string    |      结束时间，格式：YYYY-MM-DD HH:MM:SS    |
|  total_elapsed_time      |    int    |      总执行时间（秒）    |
|  effective_time      |    int    |      有效执行时间（秒），排除人工节点后的耗时    |
|  excluded_node_count      |    int    |      排除节点数量（人工节点数量）    |
|  total_node_count      |    int    |      总节点数量    |
|  excluded_component_codes      |    list    |      排除的节点组件代码列表，从环境变量 MANUAL_WAITING_COMPONENT_CODES 中获取，如果未配置则使用默认值：["bk_approve", "pause_node", "sleep_timer", "bot-approval"]    |
|  category      |    string    |      任务分类    |

### 说明

1. **排除节点**：人工节点（审批节点、暂停节点、定时节点等）的耗时会被排除。排除的节点类型通过环境变量 `MANUAL_WAITING_COMPONENT_CODES` 配置，多个组件代码用逗号分隔。如果未配置，则使用默认值：`bk_approve`（审批节点）、`pause_node`（暂停节点）、`sleep_timer`（定时节点）、`bot-approval`（机器人审批节点）。

2. **被终止的任务**：如果任务有终止操作（revoke），接口会返回错误，因为被终止的任务无法准确计算有效执行时间。

3. **任务状态要求**：只有已完成的任务才能统计有效执行时间，如果任务尚未完成，接口会返回错误。


### 功能描述

获取任务节点的插件执行日志

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   plugin_code  |   string     |   是   |  插件服务编码 |
|   trace_id     |   string     |   是   |  Trace ID |
|   scroll_id    |   string     |   否   |  翻页标识字段，获取下一页时传入上一次返回的该值 |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "plugin_code": "sleep_timer",
    "trace_id": "aaa0ce51d2143aa9b0dbc27cb7df",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "logs": "[2026-03-11 10:00:01]INFO-execute: 插件开始执行\n[2026-03-11 10:00:05]INFO-execute: 插件执行完成",
        "total": 2,
        "scroll_id": "abc123"
    },
    "message": "",
    "trace_id": "xxx"
}
```

### 返回结果说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  trace_id |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  logs      |    string  |      日志内容（格式化后的纯文本）     |
|  total     |    int     |      日志总条数     |
|  scroll_id |    string  |      翻页标识符，获取下一页时传入该值     |

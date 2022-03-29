### 功能描述

操作任务，如开始、暂停、继续、终止等

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string     |   是   |  模板所属业务ID |
|   task_id     |   string     |   是   |  任务ID         |
|   action      |   string     |   是   |  操作类型       |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### action

| 值        | 描述     |
|-----------|----------|
| start     | 开始任务，等效于调用 start_task 接口 |
| pause     | 暂停任务，任务处于执行状态时调用  |
| resume    | 继续任务，任务处于暂停状态时调用  |
| revoke    | 终止任务  |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "action": "start",
    "bk_biz_id": "2",
    "task_id": "10",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {},
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时返回数据      |
|  message     |    string  |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

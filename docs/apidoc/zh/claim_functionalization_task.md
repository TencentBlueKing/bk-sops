### 功能描述

职能化任务认领

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   task_id      |   string     |   是   |  任务ID，需要任务状态是未开始的 |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   constants    |   dict       |   是   |  任务全局参数，详细信息见下面说明 |
|   name         |   string     |   否   |  任务新名称  |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username":"xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    },
    "name": "xxx",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "data": "success",
    "result": true, 
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    string  |      result=true 时成功数据, "success" |
|  code        |    int     |      结果状态码                  |
|  message     |    string  |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

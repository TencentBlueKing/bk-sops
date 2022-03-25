### 功能描述

查询任务或任务节点执行状态

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string   |   是   |  模板所属业务ID   |
|   task_id     |   string   |   是   |  任务或节点ID     |
|   subprocess_id |   string   |   否   |  任务中的子流程节点 ID   |
|   with_ex_data     |   bool   |   否   |  是否返回错误节点异常数据 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "subprocess_id": "xxx",
    "with_ex_data": true,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "id": "ndf194ddb9e6365da1902dbd51610e9a",
        "state": "FAILED",
        "name": "<class 'pipeline.core.pipeline.Pipeline'>",
        "retry": 0,
        "loop": 1,
        "skip": false,
        "error_ignorable": false,
        "version": "",
        "state_refresh_at": "2020-08-17T12:13:53.320Z",
        "elapsed_time": 55035,
        "children": {
            "n00e3a0396403a19a4517d8e2eb0b015": {
                "id": "n00e3a0396403a19a4517d8e2eb0b015",
                "state": "FINISHED",
                "name": "<class 'pipeline.core.flow.event.EmptyStartEvent'>",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "22daf98a558737e39a5ae8d3876fac7d",
                "state_refresh_at": "2020-08-17T12:13:53.254Z",
                "elapsed_time": 0,
                "children": {},
                "start_time": "2020-08-17 20:13:53 +0800",
                "finish_time": "2020-08-17 20:13:53 +0800"
            },
            "nb346e202d17387082189f95dd3f80ca": {
                "id": "nb346e202d17387082189f95dd3f80ca",
                "state": "FAILED",
                "name": "定时",
                "retry": 0,
                "loop": 1,
                "skip": false,
                "error_ignorable": false,
                "version": "e74df19258f535509cb104ad1ca94f00",
                "state_refresh_at": "2020-08-17T12:13:53.279Z",
                "elapsed_time": 0,
                "children": {},
                "start_time": "2020-08-17 20:13:53 +0800",
                "finish_time": "2020-08-17 20:13:53 +0800"
            }
        },
        "start_time": "2020-08-17 20:13:53 +0800",
        "finish_time": "",
        "ex_data": {
            "nb346e202d17387082189f95dd3f80ca": "定时时间需晚于当前时间"
        }
    },
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  state      |    string    |      任务或节点状态，详细信息见下面说明    |
|  id      |    string    |      任务或节点执行态ID，不等于 task_id    |
|  skip      |    bool    |      是否跳过执行    |
|  retry      |    int    |      重试和跳过总次数   |
|  start_time      |    string    |      任务或节点执行开始时间   |
|  finish_time      |    string    |      任务或节点执行结束时间    |
|  children      |    dict   |      任务节点执行详情，详细信息见下面说明   |
|  name      |    string    |      节点名称    |
|  ex_data  |  dict  | key为失败节点ID，value为失败节点错误数据 |

#### data.state

| 返回值    | 描述      |
|----------|-----------|
| CREATED   | 未执行   |  
| RUNNING   | 执行中   |
| FAILED    | 失败     |
| SUSPENDED | 暂停     |
| REVOKED   | 已终止   |
| FINISHED  | 已完成   |  

#### data.children KEY

任务节点执行态ID

#### data.children VALUE

同 data 格式

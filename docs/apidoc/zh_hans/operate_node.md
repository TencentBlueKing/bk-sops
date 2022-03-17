### 功能描述

操作节点

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   task_id       |   int     |   是   |  任务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| node_id        | string     | 是         | 节点 ID                        |
| action        | string     | 是         | 操作类型，可选值有：callback（节点回调）, skip_exg（跳过执行失败的分支网关）, retry（重试失败节点）, skip（跳过失败的节点）, pause_subproc（暂停正在执行的子流程）, resume_subproc（继续暂停的子流程） |
| data | object   | 否         | action 为 callback 时传入的数据    |
| inputs | object   | 否         | action 为 retry 时重试节点时节点的输入数据    |
| flow_id | string   | 否         | action 为 skip_exg 时选择执行的分支 id    |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "12",
    "node_id": "node_id",
    "action": "skip",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": "success",
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | string     | result=true 时返回的信息 |
|  message      | string     | result=false 时错误信息        |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

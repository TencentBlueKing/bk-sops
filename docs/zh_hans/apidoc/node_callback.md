### 功能描述

回调指定的节点（通常用于暂停等待类节点的人工审批回调场景）

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点 ID |
|   callback_data |  dict       |   否   |  回调数据，传递给节点的回调参数 |
|   version      |   string     |   否   |  节点版本号，用于指定回调的节点版本 |
|   scope        |   string     |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "app_code",
    "bk_app_secret": "app_secret",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "callback_data": {
        "data": {}
    },
    "version": "23ac8c29f62b3337aafcf1f538d277f8",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 操作成功与否     |
|  message  |    string  |      result=false 时错误信息     |
|  trace_id |    string  |      open telemetry trace_id     |

### 功能描述

获取任务节点的JOB平台执行日志

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点ID |
|   target_ip    |   string     |   否   |  目标IP，用于过滤指定机器的日志 |
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
    "node_id": "node0df0431f8f553925af01a94854bd",
    "target_ip": "127.0.0.1",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "logs": "[127.0.0.1] GSE AGENT 正常\n[127.0.0.1] 开始执行脚本...\n[127.0.0.1] 脚本执行完成，返回码: 0"
}
```

### 返回结果说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  logs     |    string  |      JOB平台执行日志内容     |
|  message  |    string  |      result=false 时错误信息     |

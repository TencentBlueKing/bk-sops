### 功能描述

获取任务节点的执行日志

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id      |   string     |   是   |  任务ID |
|   node_id      |   string     |   是   |  节点ID |
|   version      |   string     |   是   |  节点执行版本号 |
|   page         |   int        |   否   |  页码，默认为 1 |
|   page_size    |   int        |   否   |  每页条目数，默认为 30 |
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
    "version": "23ac8c29f62b3337aafcf1f538d277f8",
    "page": 1,
    "page_size": 30,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "data": "2026-03-11 10:00:01: 开始执行脚本...\n2026-03-11 10:00:05: 脚本执行完成，返回码: 0",
    "page": {
        "page": 1,
        "page_size": 30,
        "total": 2
    },
    "trace_id": "xxx"
}
```

### 返回结果说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    string  |      日志内容（纯文本格式）     |
|  message  |    string  |      result=false 时错误信息     |
|  page     |    dict    |      分页信息     |
|  trace_id |    string  |      open telemetry trace_id     |

#### page

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  page      |    int    |      当前页码     |
|  page_size |    int    |      每页条目数   |
|  total     |    int    |      总条目数     |

### 功能描述

查询公共模板列表

### 请求参数

#### 接口参数

无

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
}
```

### 返回结果示例

```
{
    "data": [
        {
            "category": "Other",
            "name": "父流程",
            "creator": "admin",
            "edit_time": "2019-07-15 15:13:22 +0800",
            "create_time": "2019-07-15 15:13:22 +0800",
            "editor": "admin",
            "id": 10014,
            "auth_actions": [
                "common_flow_create_task",
                "common_flow_edit",
                "common_flow_delete",
                "common_flow_view",
                "common_flow_create",
                "common_flow_create_periodic_task"
            ]
        },
        {
            "category": "Other",
            "name": "子流程",
            "creator": "admin",
            "edit_time": "2019-07-15 15:13:22 +0800",
            "create_time": "2019-07-15 15:13:22 +0800",
            "editor": "admin",
            "id": 10013,
            "auth_actions": [
                "common_flow_create_task",
                "common_flow_edit",
                "common_flow_delete",
                "common_flow_view",
                "common_flow_create",
                "common_flow_create_periodic_task"
            ]
        },
    ],
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | list     | result=true时模板列表，item 信息见下面说明 |
| message   | string   | result=false时错误信息 |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  id      |    int    |      模板ID    |
|  name      |    string    |      模板名称    |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator      |    string    |      模板创建人   |
|  create_time      |    string    |      模板创建时间   |
|  editor      |    string 或者 null    |      模板编辑人   |
|  edit_time      |    string   |      模板最新编辑时间   |
|  auth_actions      |    array   |      用户对该资源有权限的操作   |

#### data.category

| 返回值        | 描述     |
|--------------|----------|
| OpsTools     | 运维工具  |
| MonitorAlarm | 监控告警  |
| ConfManage   | 配置管理  |
| DevTools     | 开发工具  |
| EnterpriseIT | 企业IT   |
| OfficeApp    | 办公应用  |
| Other        | 其它     |

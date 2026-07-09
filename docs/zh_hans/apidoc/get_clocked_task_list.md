### 功能描述

查询业务下的计划任务列表

### 请求参数

#### 接口参数

| 字段                 | 类型      | 必选 | 描述                                                                                                                              |
|--------------------|---------|----|---------------------------------------------------------------------------------------------------------------------------------|
| bk_biz_id          | string  | 是  | 项目唯一 ID，项目 ID 或 CMDB 业务 ID                                                                                                        |
| scope              | string  | 否  | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |
| id                 | integer | 否  | 根据计划任务ID过滤列表，默认不过滤                                                                                                              |
| task_name          | string  | 否  | 根据计划任务名称关键词过滤列表，支持模糊搜索，默认不过滤                                                                                                    |
| creator            | string  | 否  | 根据创建者过滤列表，支持模糊搜索，默认不过滤                                                                                                          |
| editor             | string  | 否  | 根据编辑者过滤列表，支持模糊搜索，默认不过滤                                                                                                          |
| state              | string  | 否  | 根据计划任务状态过滤列表，默认不过滤                                                                                                              |
| expected_timezone  | string  | 否  | 时间相关字段期望返回的时区，形如 Asia/Shanghai                                                                                                  |
| limit              | integer | 否  | 分页，返回列表条目数，默认为 100                                                                                                              |
| offset             | integer | 否  | 分页，返回列表起始条目下标，默认为 0                                                                                                              |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "id": 1,
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 1,
            "task_parameters": {
                "constants": {},
                "template_schemes_id": []
            },
            "creator": "xxxx",
            "editor": "",
            "state": "not_started",
            "plan_start_time": "2026-04-11 00:00:00+0800",
            "create_time": "2026-04-10 17:01:20+0800",
            "edit_time": "2026-04-10 17:01:20+0800",
            "project_id": 1,
            "task_id": null,
            "task_name": "xxxx",
            "template_id": 1,
            "template_name": "xxxx",
            "template_source": "project",
            "clocked_task_id": 15,
            "auth_actions": [
                "clocked_task_view",
                "clocked_task_edit",
                "clocked_task_delete",
                "flow_view"
            ]
        }
    ],
    "count": 1,
    "code": 0,
    "trace_id": "xxxx"
}
```

### 返回结果参数说明

| 字段        | 类型      | 描述                           |
|-----------|---------|------------------------------|
| result    | bool    | true/false 查询成功与否             |
| data      | list    | result=true 时计划任务列表，item 信息见下面说明 |
| count     | integer | data 列表数量                     |
| code      | integer | 错误码                          |
| message   | string  | result=false 时错误信息            |
| trace_id  | string  | open telemetry trace_id      |

#### data

| 字段              | 类型      | 描述                |
|-----------------|---------|-------------------|
| id              | integer | 任务唯一标识符           |
| clocked_task_id | integer | 计划任务 Celery 任务 ID |
| auth_actions    | list    | 当前用户对该任务所拥有的操作权限  |
| creator         | string  | 创建者               |
| create_time     | string  | 任务创建时间            |
| editor          | string  | 编辑者               |
| edit_time       | string  | 任务编辑时间            |
| plan_start_time | string  | 计划开始时间            |
| project_id      | integer | 项目 ID             |
| state           | string  | 计划任务状态            |
| task_id         | integer | taskflow 任务 ID（可能为 null） |
| task_name       | string  | 计划任务名称            |
| task_parameters | object  | 任务参数，详见下方说明       |
| template_id     | integer | 模板 ID             |
| template_name   | string  | 模板名称              |
| template_source | string  | 模板来源              |

#### data.task_parameters

| 字段                  | 类型     | 描述         |
|---------------------|--------|------------|
| constants           | object | 计划任务参数     |
| template_schemes_id | list   | 计划任务使用的执行方案列表 |

### MCP 请求说明

当请求来源于网关 MCP 时，以下字段会在响应中被过滤，不会返回：

- `data.[].auth_actions` - 数组中每个计划任务项的权限操作列表

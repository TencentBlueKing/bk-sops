### 功能描述

创建计划任务

### 请求参数

#### 接口参数

| 字段               | 类型     | 必选  | 描述                                                                                                       |
|------------------|--------|-----|----------------------------------------------------------------------------------------------------------|
| bk_biz_id        | string | 是   | 任务所属业务ID                                                                                                 |
| template_id      | string | 是   | 用于创建任务的模板ID                                                                                              |
| task_name        | string | 是   | 要创建的计划任务名称                                                                                               |
| plan_start_time  | string | 是   | 计划任务开始时间，推荐带上时区信息，格式如 `2022-05-16 20:26:40+0800`                                                         |
| task_parameters  | dict   | 否   | 任务参数, 详见下面说明                                                                                             |
| scope            | string | 否   | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

#### task_parameters

| 参数名称          | 参数类型  | 必须 |     参数说明     |
|---------------|-------|--| ---------------- |
| constants     | dict  | 否 |  计划任务参数，对应变量key和value，默认为 `{}` |
| template_schemes_id    | list     | 否 | 计划任务使用的执行方案列表，默认为 `[]`，代表执行所有流程节点 |

#### constants KEY

变量 KEY，${key} 格式

#### constants VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "app_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_id": "1",
    "bk_biz_id": "2",
	"scope":"cmdb_biz",
    "task_name": "test_clocked_task",
    "plan_start_time": "2022-05-16 20:26:40+0800",
    "task_parameters": {
        "constants": {},
        "template_schemes_id": []
    },
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "id": 72,
        "task_parameters": {
            "constants": {},
            "template_schemes_id": []
        },
        "creator": "",
        "plan_start_time": "2022-05-16 20:26:40+0800",
        "project_id": 1,
        "task_id": null,
        "task_name": "test_clocked_task",
        "template_id": 508,
        "template_name": "测试模版",
        "template_source": "project",
        "clocked_task_id": 88
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 名称         | 类型     | 说明                           |
|------------|--------|------------------------------|
| result     | bool   | true/false 操作是否成功            |
| data       | dict   | result=true 时成功数据，详细信息请见下面说明 |
| message    | string | result=false 时错误信息           |
| trace_id   | string | open telemetry trace_id      |

#### data

| 名称               | 类型     | 说明                 |
|------------------|--------|--------------------|
| id               | int    | 计划任务 ID            |
| task_id          | int    | 任务 ID，任务未创建时为 null |
| task_name        | string | 任务名                |
| task_parameters  | dict   | 任务参数               |
| creator          | string | 创建者                |
| plan_start_time  | string | 计划任务开始时间           |
| project_id       | int    | 项目 ID              |
 | template_id      | int    | 模板 ID              |
| template_name    | string | 模板名称               |
| template_source  | string | 模板来源               |

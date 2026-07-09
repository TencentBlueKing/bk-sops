### 功能描述

获取业务下的轻应用列表

### 请求参数

#### 接口参数

| 字段        | 类型     | 必选  | 描述                                                                                                       |
|-----------|--------|-----|----------------------------------------------------------------------------------------------------------|
| bk_biz_id | string | 是   | 任务所属业务ID                                                                                                 |
| scope     | string | 否   | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |
| limit     | int    | 否   | 分页，返回任务列表任务数，默认为100，最大为200                                                                               |
| offset    | int    | 否   | 分页，返回任务列表起始任务下标，默认为0                                                                                     |

### 请求参数示例

```
{
    "bk_app_code": "app_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
	"scope":"cmdb_biz",
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "auth_actions": [
                "mini_app_view",
                "mini_app_edit",
                "mini_app_delete",
                "mini_app_create_task"
            ],
            "id": 1,
            "name": "new20210813065242",
            "code": "bk_sops20210816112820",
            "link": "xxxx",
            "category": "OpsTools",
            "task_template_id": 155,
            "template_scheme_id": ""
        }
    ],
    "count": 1,
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
| count      | int    | data列表数量                     |
| trace_id   | string | open telemetry trace_id      |

#### data

| 名称                 | 类型     | 说明           |
|--------------------|--------|--------------|
| id                 | int    | 轻应用 ID       |
| name               | string | 轻应用名         |
| code               | string | 轻应用编码        |
| link               | string | 轻应用链接        |
| task_template_id   | int    | 轻应用对应流程 ID   |
| template_scheme_id | string | 轻应用对应执行方案 ID |
| auth_actions       | array  | 用户对该资源有权限的操作 |

### Functional description

Create a clocked task

### Request Parameters

#### Interface Parameters

| Field        |  Type       | Required | Description |
|--------------|------------|----------|--|
| bk_biz_id    |   string     | YES      | business ID |
| template_id  |   string     | YES      | ID of template which used to create task |
| task_name         | string | YES      | name of task |
| plan_start_time   | string | YES      | time to start task, recommended to bringing timezone, such as `2022-05-16 20:26:40+0800` |
| task_parameters | dict   | NO        | parameters of task, details are described below |
| scope | string | NO       | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project' |

#### task_parameters

| Field               | Type | Required | Description                                                                                |
|---------------------|------|----------|--------------------------------------------------------------------------------------------|
| constants           | dict | NO       | global variables of task, default value is `{}`                                            |
| template_schemes_id | list | NO       | list of template scheme id, default value is `[]`, representing all nodes will be executed |

#### constants KEY

constant KEY, the format is like ${key}

#### constants VALUE

constant value

### Request Parameters Example

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

### Return Result Example

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
        "template_name": "default test template",
        "template_source": "project",
        "clocked_task_id": 88
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type   | Description                                                    |
|------------|--------|----------------------------------------------------------------|
| result     | bool   | true or false, indicate success or failure                     |
| data       | dict   | data returned when result is true, details are described below |
| message    | string | error message returned when result is false                    |
| trace_id   | string | open telemetry trace_id                                        |

#### data

| Field            | Type   | Description                                         |
|------------------|--------|-----------------------------------------------------|
| id               | int    | clocked task ID                                     |
| task_id          | int    | task ID, value is null when the task is not created |
| task_name        | string | task name                                           |
| task_parameters  | dict   | parameters of task                                  |
| creator          | string | creator                                             |
| plan_start_time  | string | start time of clocked task                          |
| project_id       | int    | project ID                                          |
 | template_id      | int    | template ID                                         |
| template_name    | string | template name                                       |
| template_source  | string | template source                                     |

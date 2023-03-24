### Functional description

Get a list of mini apps

### Request Parameters

#### Interface Parameters

| Field     | Type   | Required | Description                                                                                                                                                                 |
|-----------|--------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bk_biz_id | string | YES      | the business ID                                                                                                                                                             |
| scope     | string | NO       | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
| limit     | int    | NO       | pagination, the number of tasks in the task list in each result. default is 100, max is 200                                                                                 |
| offset    | int    | NO       | pagination, the start index of task in the task list in each result. default is 0                                                                                           |

### Request Parameters Example

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

### Return Result Example

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

### Return Result Description

| Field      | Type   | Description                                                    |
|------------|--------|----------------------------------------------------------------|
| result     | bool   | true or false, indicate success or failure                     |
| data       | list   | data returned when result is true, details are described below |
| message    | string | error message returned when result is false                    |
| count      | int    | amount of data list                                            |
| trace_id   | string | open telemetry trace_id                                        |

#### data[item]

| Field              | Type   | Description                                   |
|--------------------|--------|-----------------------------------------------|
| id                 | int    | mini app ID                                   |
| name               | string | mini app name                                 |
| code               | string | mini app code                                 |
| link               | string | mini app link                                 |
| task_template_id   | int    | corresponding template ID of mini app         |
| template_scheme_id | string | corresponding template scheme ID of mini app  |                                  
| auth_actions       | array  | actions with permissions for the current user |                          

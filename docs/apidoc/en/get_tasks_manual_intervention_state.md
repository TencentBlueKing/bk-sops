### Functional description

Get tasks manual intervention state

Manual intervention is needed when any of these condition is meet:

- has running pause node
- has failed node
- has suspended subprocess
- root task is suspended

#### Interface Parameters

| Field        | Type   | Required | Description                                                                                                                                                                 |
| ------------ | ------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bk_biz_id    | string | YES      | the business ID                                                                                                                                                             |
| task_id_list | array  | YES      | task id list                                                                                                                                                                |
| scope        | string | NO       | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id_list": [30000105, 30000101, 30000100],
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": [
        {
            "id": 81,
            "manual_intervention_required": false
        },
        {
            "id": 80,
            "manual_intervention_required": true
        },
        {
            "id": 79,
            "manual_intervention_required": true
        },
        {
            "id": 78,
            "manual_intervention_required": false
        },
        {
            "id": 77,
            "manual_intervention_required": false
        }
    ],
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field   | Type   | Description                                                    |
| ------- | ------ | -------------------------------------------------------------- |
| result  | bool   | true or false, indicate success or failure                     |
| data    | list   | data returned when result is true, details are described below |
| message | string | error message returned when result is false                    |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |


#### data
| Field                        | Type | Description                      |
| ---------------------------- | ---- | -------------------------------- |
| id                           | int  | task ID                          |
| manual_intervention_required | bool | whether need manual intervention |
### Functional description

Task actions such as start, pause, resume, revoke, etc.

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string     |   YES   |  the business ID |
|   task_id     |   string     |   YES   |  the task ID     |
|   action      |   string     |   YES   |  action type, the value is described below |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

#### action

| Value        | Description     |
|-----------|----------|
| start     | start a task, which is same with calling API[start_task] |
| pause     | suspended a running task  |
| resume    | resume a suspended task   |
| revoke    | revoke a task, task revoked could not be operated again |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "action": "start",
    "bk_biz_id": "2",
    "task_id": "10",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {},
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure   |
|  data     |    dict    |      data returned when result is true            |
|  message  |    string  |      error message returned when result is false  |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

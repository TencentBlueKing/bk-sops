### Functional description

Get the plugin execution log of a task node

#### Interface Parameters

| Field          | Type       | Required | Description             |
|----------------|------------|----------|-------------------------|
| bk_biz_id      | string     | YES      | the business ID |
| task_id        | string     | YES      | the task ID |
| plugin_code    | string     | YES      | plugin service code |
| trace_id       | string     | YES      | Trace ID |
| scroll_id      | string     | NO       | scroll identifier for pagination, pass the value returned from previous request to get next page |
| scope          | string     | NO       | bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "plugin_code": "sleep_timer",
    "trace_id": "aaa0ce51d2143aa9b0dbc27cb7df",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "logs": "[2026-03-11 10:00:01]INFO-execute: Plugin started\n[2026-03-11 10:00:05]INFO-execute: Plugin execution completed",
        "total": 2,
        "scroll_id": "abc123"
    },
    "message": "",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure     |
|  data     |    dict    |      data returned when result is true, details are described below     |
|  message  |    string  |      error message returned when result is false     |
|  trace_id |    string  |      open telemetry trace_id     |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  logs      |    string  |      log content in formatted plain text     |
|  total     |    int     |      total number of log entries     |
|  scroll_id |    string  |      scroll identifier for getting next page     |

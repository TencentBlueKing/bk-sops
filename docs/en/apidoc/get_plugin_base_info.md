### Functional description

Get the base info list of available plugins under a specific business (returns only plugin code and name), no user authentication required

#### Interface Parameters

| Field          | Type       | Required | Description             |
|----------------|------------|----------|-------------------------|
| bk_biz_id      | string     | YES      | the unique ID of the project, project ID or CMDB business ID |
| scope          | string     | NO       | bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": [
        {
            "code": "sleep_timer",
            "name": "Timer"
        },
        {
            "code": "job_fast_execute_script",
            "name": "Fast Execute Script"
        },
        {
            "code": "pause_node",
            "name": "Pause"
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure     |
|  data     |    array   |      data returned when result is true, details are described below     |
|  message  |    string  |      error message returned when result is false     |
|  trace_id |    string  |      open telemetry trace_id     |

#### data[]

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  code     |    string  |      plugin code     |
|  name     |    string  |      plugin name     |

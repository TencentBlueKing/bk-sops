### Functional description

Callback a specific node (typically used for manual approval callback on pause/wait nodes)

#### Interface Parameters

| Field          | Type       | Required | Description             |
|----------------|------------|----------|-------------------------|
| bk_biz_id      | string     | YES      | the business ID |
| task_id        | string     | YES      | the task ID |
| node_id        | string     | YES      | the node ID |
| callback_data  | dict       | NO       | callback data to pass to the node |
| version        | string     | NO       | node version, used to specify which version of the node to callback |
| scope          | string     | NO       | bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "app_code",
    "bk_app_secret": "app_secret",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "callback_data": {
        "data": {}
    },
    "version": "23ac8c29f62b3337aafcf1f538d277f8",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "message": "success",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure     |
|  message  |    string  |      error message returned when result is false     |
|  trace_id |    string  |      open telemetry trace_id     |

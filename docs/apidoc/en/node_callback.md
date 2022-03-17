### Functional description

callback specific node

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
| ------------ | ------------ | ------ | ---------------- |
|   bk_biz_id    |   string     |   YES   |  the business ID |
|   task_id     |   string   |   YES   |  the task ID     |
|   node_id        | string     | YES         | node id                        |
|   callback_data        | dict     | NO         | callback data          |           |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

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
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "message": "success",
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  result   |    bool    |      true or false, indicate success or failure   |
|  message  |    string  |      error message returned when result is false  |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

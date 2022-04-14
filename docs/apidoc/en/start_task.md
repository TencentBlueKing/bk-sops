### Functional description

Start a task

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required   |  Description  |
|---------------|------------|--------|------------------|
|   bk_biz_id   |   string     |   YES   |  the business ID |
|   task_id     |   string     |   YES   |  the task ID     |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "task_url": "http://paas_url/taskflow/execute/xxx/?instance_id=xxx",
    "data": {
            "task_url": task_url
    },
    "message": "success",
    "code": 3545100,
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
|  task_url |    string  |      url of the task  |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

### Functional description

modify global parameters and name for a task

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
|---------------|------------|--------|------------------|
|   task_id     |   string     |   YES   |  task ID |
|   bk_biz_id   |   string     |   YES   |  business ID |
|   constants   |   dict       |   NO    |  global variables，details are described below |
|   name        |   string     |   NO    |  new name of the task |
|   scope       |   string     |   NO    |  bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

#### constants KEY

constant KEY, the format is like ${key}

#### constants VALUE

constant value

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    },
    "name":"",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "data": "success",
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure              |
|  data     |    string  |      data returned when result is true, "success"            |
|  message  |    string  |      error message returned when result is false             |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

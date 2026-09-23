### Functional description

Create an execution scheme for a flow template

### Request Parameters

#### Interface Parameters

|   Field         |  Type        | Required |  Description     |
|-----------------|--------------|----------|------------------|
|   bk_biz_id     |   string     |   YES    | the business ID, can be a project ID or a CMDB business ID |
|   template_id   |   int        |   YES    | template ID |
|   scope         |   string     |   NO     | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent project id. default is "cmdb_biz" |
|   name          |   string     |   YES    | execution scheme name, no longer than 64 characters |
|   data          |   string/list |  YES    | node id list contained in the execution scheme, accepts a JSON string or a string list, e.g. `["node19fe67fe8e59c75a63b3a639a605d8"]`; each node must **exist and be optional (optional=true)** in the template pipeline_tree, and the list can not be empty, otherwise a parameter error is returned |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "1",
    "template_id": "96",
    "scope": "cmdb_biz",
    "name": "scheme one",
    "data": "[\"node19fe67fe8e59c75a63b3a639a605d8\"]"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "id": 1,
        "unique_id": "96-scheme one",
        "name": "scheme one",
        "data": "[\"node19fe67fe8e59c75a63b3a639a605d8\"]"
    },
    "code": 0,
    "message": "success",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result      |    bool    |      true or false, indicate success or failure     |
|  data        |    dict    |      data returned when result is true, details are described below     |
|  message     |    string  |      error message returned when result is false     |
|  code        |    int     |      return code, 0 means success     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  id      |    int     |      execution scheme ID     |
|  unique_id     |    string     |    unique ID of the execution scheme, in the format of `{template_id}-{scheme_name}`     |
|  name     |    string     |    execution scheme name     |
|  data     |    string     |    node id list contained in the scheme (JSON string)     |

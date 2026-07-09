### Function Description

Modify the executor proxy (executor_proxy) of a flow template

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
|---------------|------------|--------|------------------|
|   template_id    |   string     |   Yes   |  Template ID |
|   bk_biz_id    |   string     |   Yes   |  Business ID that the template belongs to |
|   executor_proxy    |   string     |   Yes   | Username of the executor proxy. Can only be set to the currently logged-in user; passing an empty string means clearing the executor proxy |
| scope | string | No | The search scope of bk_biz_id. The default is cmdb_biz, in which case the project whose bound CMDB business ID is bk_biz_id is searched; when the value is project, the project whose project ID is bk_biz_id is searched |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "1",
    "executor_proxy": "11111",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "template_id": 1,
        "executor_proxy": "11111"
    },
    "code": 0,
    "trace_id": "xxx"
}
```

### Return Result Parameter Description

|   Name   |  Type  |           Description             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false indicates whether the operation was successful     |
|  data        |    dict    |      Success data when result=true, see below for details     |
|  code        |    int     |      Error code     |
|  message     |    string  |      Error message when result=false     |
|  trace_id    |    string  |      open telemetry trace_id     |

#### data

|   Name   |  Type  |           Description             |
| ------------ | ---------- | ------------------------------ |
|  template_id      |    int    |      Template ID    |
|  executor_proxy   |    string |      Updated executor proxy username    |

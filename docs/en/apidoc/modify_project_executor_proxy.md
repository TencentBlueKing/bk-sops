### Functional description

Modify project executor proxy configuration

### Request Parameters

#### Interface Parameters

| Field                      |  Type      | Required | Description                                                                                                                                                                                                   |
|----------------------------|------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   bk_biz_id                |   string   |   YES    |  business ID the template belongs to                                                                                                                                                                          |
|   executor_proxy           |   string   |   YES    |  executor proxy; can only be set to the caller's own username, empty string is allowed to clear this configuration                                                                                            |
|   executor_proxy_exempts   |   string   |   YES    |  executor proxy exemption list, multiple values separated by English commas; empty string is allowed to clear the exemption list                                                                              |
|   scope                    |   string   |   NO     |  search scope for bk_biz_id. Default is cmdb_biz, in which case the project whose bound CMDB business ID equals bk_biz_id is searched; when the value is project, the project whose project ID equals bk_biz_id is searched |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "admin",
    "executor_proxy": "admin",
    "executor_proxy_exempts": "user1,user2"
}
```

### Return Result Example

```
{
    "code": 0,
    "data": {
        "executor_proxy": "admin",
        "executor_proxy_exempts": "user1,user2",
        "project_id": 123
    },
    "result": true,
    "message": "",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field     | Type      | Description                                              |
|-----------|-----------|----------------------------------------------------------|
|  code     |  integer  |  error code                                              |
|  result   |  bool     |  true or false, indicate success or failure              |
|  data     |  object   |  data returned when result is true                       |
|  message  |  string   |  error message returned when result is false             |
|  trace_id |  string   |  open telemetry trace_id                                 |

#### data Field Description

| Field                     | Type      | Description                                                            |
|---------------------------|-----------|------------------------------------------------------------------------|
|  executor_proxy           |  string   |  executor proxy (can only be the caller's own username)                |
|  executor_proxy_exempts   |  string   |  executor proxy exemption list, multiple values separated by English commas |
|  project_id               |  integer  |  project ID                                                            |

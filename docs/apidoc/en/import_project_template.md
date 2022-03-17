### Functional description

Import project templates

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
|   template_data    |   string     |   YES   |  flow data, the content of file which download from bk-sops - templates - export  |
|   project_id    |   string     |   YES   |  project ID |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|
### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_data": "xxx",
    "project_id": "3",
    "bk_username": "cmdb_biz",
    "scope":"cmdb_biz"
}
```

### Return Result Example


```
{
    "message": "Successfully imported 2 flows",
    "data": {
        "flows": {
              11: "flowA",
              12: "flowB",
              ...
        },
        "count": 2
    },
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    dict    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

#### data

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  count      |    int    |    the number of flows had been imported    |
|  flows      |    dict |      mapping of import flow ID and name |
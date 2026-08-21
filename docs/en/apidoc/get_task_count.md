### Functional description

Get tasks count for a business, support task name keyword searching

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----|------------------|
|   bk_biz_id   |   string   | YES |  the business ID             |
|   scope       |   string     | NO | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
|   keyword     |   string     | NO |  keyword to filter the task count based on the task name. default is no filter |
|   is_started  |   bool       | NO |  task status to filter the task count based on the start status. default is no filter |
|   is_finished |   bool       | NO |  task status to filter the task count based on the finish status. default is no filter |
| executor    | string | NO | task executor to filter the task count. default is no filter |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "keyword": "定时",
    "is_started": true,
    "is_finished": "false",
    "scope":"cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": 1,
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    dict    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  trace_id     |    string  | open telemetry trace_id       |

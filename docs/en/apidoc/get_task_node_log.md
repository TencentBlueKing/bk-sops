### Functional description

Get the execution log of a task node

#### Interface Parameters

| Field          | Type       | Required | Description             |
|----------------|------------|----------|-------------------------|
| bk_biz_id      | string     | YES      | the business ID |
| task_id        | string     | YES      | the task ID |
| node_id        | string     | YES      | the node ID |
| version        | string     | YES      | execution version of the node |
| page           | int        | NO       | page number, default is 1 |
| page_size      | int        | NO       | number of items per page, default is 30 |
| scope          | string     | NO       | bk_biz_id scope. default is cmdb_biz, and bk_biz_id means bindded CMDB business ID of a project; when set to project, bk_biz_id means the project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "version": "23ac8c29f62b3337aafcf1f538d277f8",
    "page": 1,
    "page_size": 30,
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "message": "success",
    "data": "2026-03-11 10:00:01: Start executing script...\n2026-03-11 10:00:05: Script execution completed, return code: 0",
    "page": {
        "page": 1,
        "page_size": 30,
        "total": 2
    },
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure     |
|  data     |    string  |      log content in plain text format     |
|  message  |    string  |      error message returned when result is false     |
|  page     |    dict    |      pagination info     |
|  trace_id |    string  |      open telemetry trace_id     |

#### page

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  page      |    int    |      current page number     |
|  page_size |    int    |      number of items per page   |
|  total     |    int    |      total number of items     |

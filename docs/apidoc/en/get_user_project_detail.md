### Functional description

Get project detail

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|---------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "project_id": 13,
        "project_name": "blueking",
        "bk_biz_id": 2,
        "from_cmdb": true,
        "bk_biz_name": "blueking",
        "bk_biz_developer": "",
        "bk_biz_maintainer": "admin,gcloudadmin",
        "bk_biz_tester": "",
        "bk_biz_productor": "",
        "auth_actions": [
            "project_view",
            "project_edit",
            "project_fast_create_task"
        ]
    },
    "code": 0,
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

#### data
| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | project ID       |
|  project_name  | string     | project name           |
|  bk_biz_id | int        | bound cmdb business ID       |
|  from_cmdb | bool        | whether this business is sync from cmdb       |
|  bk_biz_name  | string     | project name           |
|  bk_biz_developer  | string     | business developers           |
|  bk_biz_maintainer  | string     | business operators           |
|  bk_biz_tester  | string     | business testers           |
|  bk_biz_productor  | string     | business productors           |
|  auth_actions  | list     | authorized actions on this project for current user           |

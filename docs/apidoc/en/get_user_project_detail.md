### Functional description

Get project detail

### Request Parameters

{{ common_args_desc }}

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2"
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
        "bk_biz_productor": ""
    },
    "code": 0
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    dict    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |

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

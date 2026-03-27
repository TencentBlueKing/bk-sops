### Functional description

Register bk_sops project from cmdb

#### Interface Parameters

| Field          |  Type       | Required   |  Description  | 
|-----------------|-------------|---------|------------------|
|   bk_biz_id    |   string     |   YES   |  CMDB business ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": 6,
}
```

### Return Result Example

```
{
    "data": {
        "project_id": 10,
        "project_name": "test"
    },
    "result": true,
    "code": 0
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    dict    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false    

#### data
| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  project_id |    int    | bk_sops project ID |
|  project_name |    string | bk_sops project name |

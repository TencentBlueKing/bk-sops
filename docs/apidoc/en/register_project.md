### Functional description

Register bk_sops project from cmdb

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

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

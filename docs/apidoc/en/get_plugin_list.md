### Functional description

Get all plugins info for a business

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
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
    "data": [
        {
            "inputs": [],
            "outputs": [
                {
                    "name": "result",
                    "key": "_result",
                    "type": "bool",
                    "schema": {
                        "type": "boolean",
                        "description": "success",
                        "enum": []
                    }
                },
                {
                    "name": "loop_time",
                    "key": "_loop",
                    "type": "int",
                    "schema": {
                        "type": "int",
                        "description": "loop_time",
                        "enum": []
                    }
                }
            ],
            "desc": "",
            "code": "job_push_local_files",
            "name": "push local file",
            "group_name": "(JOB)",
            "version": "1.0.0"
        }
    ]
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |

##### data[item] 说明

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  inputs      |    array    |      plugin inputs list    |
|  outputs      |    array    |      plugin output list    |
|  desc      |    string    |      plugin description    |
|  code      |    string    |      plugin code    |
|  name      |    string    |      plugin name    |
|  group_name      |    string    |      plugin group name    |
|  version      |    name    |      plugin version    |
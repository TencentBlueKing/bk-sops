### Request Address

/v2/sops/get_task_node_data/

### Request Method

GET

### Functional description

Get task node data

#### General Parameters

|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|---------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
| node_id        | string     | YES         | node id                        |
| component_code| string     | YES         | plugin code                       |
| subprocess_stack| string   | NO         | subprocess stack, json array string    |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": 11,
    "node_id": "ndfbcbdc77e9350ba18222dc4a0a435f",
    "component_code": "sleep_timer",
    "scope": "cmdb_biz"
    "subprocess_stack":"[1, 2]"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "inputs": {
            "bk_timing": "123"
        },
        "outputs": [
            {
                "name": "result",
                "key": "_result",
                "value": "",
                "preset": true
            },
            {
                "name": "loop time",
                "key": "_loop",
                "value": "",
                "preset": true
            }
        ],
        "ex_data": ""
    },
    "message": "",
    "code": 0,
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
| ------------  | ---------- | ------------------------------ |
|  inputs       | dict       | inputs parameters, format is key：value      |
|  outputs      | list       | outputs info of this node，details are described below    |
|  ex_data      | string     | failure detail of this node，format is json or HTML、string |

#### data.outputs[]

| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | name of output variable                   |
|  value        | string、int、bool、dict、list | value  |
|  key          | string     | KEY                   |
|  preset       | bool       | where to display in Standard Plugins   |


### Request Address

/v2/sops/get_plugin_detail/

### Request Method

GET

### Functional description

Get plugin info based on plugin code for a business

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
|   code        |   string     |  YES   |  plugin code |
|   version     |   string     |   NO   |  plugin version, default is "legacy" | 


### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_username": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "code": "sleep_timer",
    "version": "legacy",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": {
        "inputs": [
            {
                "name": "Timing",
                "key": "bk_timing",
                "type": "string",
                "schema": {
                    "type": "string",
                    "description": "Timing, seconds(s) or datetime(%%Y-%%m-%%d %%H:%%M:%%S)",
                    "enum": []
                },
                "required": true
            },
            {
                "name": "force to be later than current time",
                "key": "force_check",
                "type": "bool",
                "schema": {
                    "type": "string",
                    "description": "",
                    "enum": []
                },
                "required": true
            }
        ],
        "outputs": [
            {
                "name": "Execution Result",
                "key": "_result",
                "type": "bool",
                "schema": {
                    "type": "boolean",
                    "description": "Boolean result，True or False",
                    "enum": []
                }
            },
            {
                "name": "Loop Times",
                "key": "_loop",
                "type": "int",
                "schema": {
                    "type": "int",
                    "description": "Loop execution times",
                    "enum": []
                }
            }
        ],
        "desc": "",
        "code": "sleep_timer",
        "name": "Timing",
        "group_name": "BK Service(BK)",
        "version": "legacy",
        "form": "/static/components/atoms/bk/timer.js"
    },
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

##### data

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  inputs      |    array    |      plugin inputs list    |
|  outputs      |    array    |      plugin output list    |
|  desc      |    string    |      plugin description    |
|  code      |    string    |      plugin code    |
|  name      |    string    |      plugin name    |
|  group_name      |    string    |      plugin group name    |
|  version      |  string  |  plugin version    |
|  form         |    string    | plugin form url |

##### inputs

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
| required | bool | whether the input is required |
| type | string | input type |
| name | string | input name |
| key | string | input unique key |
| schema | dict | input schema |

###### inputs.schema

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
| type | string | input type |
| enum | list | value enumeration |
|  description      |    string    |   input description   |
| properties | dict | object attribute schema, only exist when type is 'object' |
| items | dict | array item schema, only exist when type is 'array' |

##### outputs

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
| type | string | output type |
| name | string | output name |
| key | string | output unique key |
| schema | dict | output schema |

###### outputs.schema

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
| type | string | output type |
| enum | list | value enumeration |
|  description      |    string    |   output description   |
| properties | dict | object attribute schema, only exist when type is 'object' |
| items | dict | array item schema, only exist when type is 'array' |
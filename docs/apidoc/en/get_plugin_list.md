### Functional description

Get all plugins info for a business

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
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "scope": "cmdb_biz"
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
            "version": "1.0.0",
            "form": "/static/components/atoms/job/job_push_local_files.js"
        }
    ],
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

##### data[item]

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
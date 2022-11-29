### Functional description

Get task node data

#### Interface Parameters

| Field            | Type   | Required | Description                                                                                                                                                                 |
|------------------|--------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| bk_biz_id        | string | YES      | the business ID                                                                                                                                                             |
| scope            | string | NO       | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
| node_id          | string | YES      | node id                                                                                                                                                                     |
| component_code   | string | YES      | plugin code                                                                                                                                                                 |
| subprocess_stack | string | NO       | subprocess stack, json array string                                                                                                                                         |
| template_node_id | string | NO       | template node id, history execution time will be returned when it is offered                                                                                                |

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
    "subprocess_stack":"[1, 2]",
    "template_node_id":"node3b8d4f3b06b1dc37cf1a748c77ed"
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
        "ex_data": "",
        "execution_time": [
            {
                "archived_time": "2022-11-17T19:10:27+08:00",
                "elapsed_time": 40
            },
            {
                "archived_time": "2022-11-17T17:35:56+08:00",
                "elapsed_time": 20
            }
        ]
    },
    "message": "",
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

| Field      | Type      | Description                                                     |
| ------------  | ---------- |-----------------------------------------------------------------|
|  inputs       | dict       | inputs parameters, format is key：value                          |
|  outputs      | list       | outputs info of this node，details are described below           |
|  ex_data      | string     | failure detail of this node，format is json or HTML、string       |
| execution_time | list     | history execution time of this node，details are described below |

#### data.outputs[]

| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | name of output variable                   |
|  value        | string、int、bool、dict、list | value  |
|  key          | string     | KEY                   |
|  preset       | bool       | where to display in Standard Plugins   |

#### data.execution_time[]
| Field         | Type   | Description               |
|---------------|--------|---------------------------|
| archived_time | string | archived time of the node |
| elapsed_time  | int    | elapsed time of the node  |

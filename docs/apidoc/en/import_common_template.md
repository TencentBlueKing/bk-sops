### Functional description

import common flow template

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
| ------------ | ------------ | ------ | ---------------- |
|   template_data    |   string     |   YES   |  flow data, the content of file which download from bk-sops - common templates - export |
|   override        | bool     | NO         | whether to override flows which has same ID           |           |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "template_data": "xxx",
    "override": true
}
```

### Return Result Example

```
{
    "message": "Successfully imported 2 common flows",
    "data": {
        "count": 2,
        "flows": {
              11: "flowA",
              12: "flowB",
              ...
        },
    },
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  result   |    bool    |      true or false, indicate success or failure   |
|  message  |    string  |      error message returned when result is false  |
|  data         | dict        |    return data                |
|  request_id     |    string  | esb request id         |
|  trace_id     |    string  | open telemetry trace_id       |

#### data

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  count      |    int    |       the number of flows had been imported    |
|  flows      |    dict |      mapping of import flow ID and name |
### Functional description

Get template execution scheme list

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|---------|------------------|
|   bk_biz_id   |   string   |   YES   |  the business ID             |
|   scope       |   string     |   NO   | id scope, can be "cmdb_biz" or "project". if scope is "cmdb_biz" then bk_biz_id represent cmdb business ID, otherwise bk_biz_id represent proejct id. default is "cmdb_biz" |
|   template_id       |   int     |   YES   |  template ID |
|   with_constants       |   string     |   NO   |  whether to return scheme constants detail, can be "true" or "false". default is "false" |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "12",
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "result": true,
    "data": [
        {
            "id": "47-1",
            "name": "1",
            "data": "[\"node7082deed0725aed8c72ecff079ba\",\"node88d9050f288765b94a15cbe023ab\"]",
            "detail": {
                "constants": {
                    "key1": {
                        "key": "key1",
                        "name": "Parameter 1",
                        "value": "default value"
                    }
                }
            }
        },
        {
            "id": "47-2",
            "name": "2",
            "data": "[\"node7082deed0725aed8c72ecff079ba\"]",
            "detail": {
                "constants": {
                    "key2": {
                        "key": "key2",
                        "name": "Parameter 2",
                        "value": "default value"
                    }
                }
            }
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### Return Result Description

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  result   |    bool    |      true or false, indicate success or failure                      |
|  data     |    list    |      data returned when result is true, details are described below  |
|  message  |    string  |      error message returned when result is false                     |
|  trace_id     |    string  | open telemetry trace_id       |

#### data
| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  id  | string     | scheme id           |
|  name  | string     | scheme name           |
|  data  | string     | node id list in scheme (JSON string)  |
|  detail  | object     | scheme detail, contains input parameters info. returned when with_constants is true  |

#### detail
| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  constants  | object     | input parameters corresponding to the scheme, same structure as template constants  |
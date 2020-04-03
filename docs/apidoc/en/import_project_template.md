### Functional description

Import project templates

### Request Parameters

{{ common_args_desc }}

#### Interface Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
|   template_data    |   string     |   YES   |  flow data, the content of file which download from bk-sops - templates - export  |
|   project_id    |   string     |   YES   |  project ID |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "template_data": "xxx",
    "project_id": "3,
}
```

### Return Result Example


```
{
    "message": "Successfully imported 2 flows",
    "data": {
        "count": 2
    },
    "result": true
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
| ------------ | ---------- | ------------------------------ |
|  count      |    int    |    the number of flows had been imported    |

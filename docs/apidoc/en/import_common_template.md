### Functional description

import common flow template

### Request Parameters

#### General Parameters
|   Field         |  Type       | Required |  Description    |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field          |  Type       | Required   |  Description             |
| ------------ | ------------ | ------ | ---------------- |
|   data_file    |   file     |   YES   |  flow data file |
|   override        | bool     | NO         | whether to override flows which has same ID           |           |

### Request Parameters Example

```
import requests
kwargs = {
    "app_code": "app_code",
    "app_secret": "app_secret",
    "access_token": "access_token",
    "data_file": data_file
}
response = requests.post("http://{stageVariables.domain}/apigw/import_common_template/", kwargs)
result = response.json()
```

### Return Result Example

```
{
    "message": "Successfully imported 2 common flows",
    "data": 2,
    "result": true
}
```

### Return Result Description

| Field      | Type      | Description      |
| ------------  | ---------- | ------------------------------ |
|  result   |    bool    |      true or false, indicate success or failure   |
|  message  |    string  |      error message returned when result is false  |
|  data         | int        | the number of flows had been imported                    |

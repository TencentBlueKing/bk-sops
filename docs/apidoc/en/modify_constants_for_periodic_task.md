### Request Address

/v2/sops/modify_constants_for_periodic_task/

### Request Method

POST

### Functional description

modify global parameters for periodic task

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
|---------------|------------|--------|------------------|
|   task_id    |   string     |   YES   |  task ID |
|   bk_biz_id    |   string     |   YES   |  business ID |
|   constants    |   dict       |   NO    |  global variables，details are described below |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to bk_biz_id. otherwise, bk_sops will find a project which id equal to bk_biz_id when scope value is 'project'|

#### constants KEY

constant KEY, the format is like ${key}

#### constants VALUE

constant value

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    },
    "scope": "cmdb_biz"
}
```

### Return Result Example

```
{
    "data": {
        "${bk_timing}": {
            "source_tag": "sleep_timer.bk_timing",
            "source_info": {
                "node76393dcfedcf73dbc726f1c4786d": [
                    "bk_timing"
                ]
            },
            "name": "time",
            "custom_type": "",
            "index": 0,
            "value": "15",
            "show_type": "show",
            "source_type": "component_inputs",
            "key": "${bk_timing}",
            "validation": "",
            "desc": ""
        }
    },
    "result": true,
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

#### data KEY

KEY, the format is like ${key}

#### data VALUE

| Field      | Type      | Description      |
|-----------|----------|-----------|
|  key      |    string    |      same with KEY     |
|  name      |    string    |     name    |
|  index      |    int    |       display order at the front end   |
|  desc      |    string    |     description   |
|  source_type  | string   |      source of variable, custom mean manual variable, component_inputs means variables comes from task node inputs parameters, component_outputs means variables comes from task node outputs parameters   |
|  custom_type  | string   |      custom type, which is not empty when source_type is custom,  the value is input ,or textarea, or datetime, or int |
|  source_tag   | string   |      source tag and standard plugin info, which is not empty when source_type is  component_inputs or component_outputs  |
|  source_info | dict    |        source info about task node ID  |

### Functional description

Query plugin list for project

### Request Parameters

#### General Parameters

|   Field         |  Type       | Required |  Description     |
|-----------------|-------------|----------|------------------|
|   bk_app_code   |   string    |   YES    |  APP ID |
|   bk_app_secret |   string    |   YES    |  APP Secret(APP TOKEN), which can be got via BlueKing Developer Center -> Click APP ID -> Basic Info |
|   bk_token      |   string    |   NO     |  Current user login token, bk_token or bk_username must be valid, bk_token can be got by Cookie      |
|   bk_username   |   string    |   NO     |  Current user username, APP in the white list, can use this field to specify the current user        |

#### Interface Parameters

| Field         |  Type      | Required |  Description     |
|---------------|------------|----------|------------------|
|   project_id  |   int      |  YES     |  the project ID  |
| scope | string | NO | bk_biz_id scope. default value is 'cmdb_biz' and bk_sops will find a project which relate cmdb business id equal to project_id. otherwise, bk_sops will find a project which id equal to project_id when scope value is 'project'|

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "project_id": "2"
}
```

### Return Result Example

```
{
    "data": [
        {
            "inputs": [
                {
                    "required": true,
                    "type": "string",
                    "name": "business ID",
                    "key": "biz_cc_id",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "current operation's business ID"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "periodic task name",
                    "key": "job_cron_name",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "periodic task name"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "cron",
                    "key": "job_cron_expression",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "cron"
                    }
                },
                {
                    "required": true,
                    "type": "string",
                    "name": "status",
                    "key": "job_cron_status",
                    "schema": {
                        "enum": [
                            1,
                            2
                        ],
                        "type": "int",
                        "description": "status"
                    }
                }
            ],
            "code": "job_cron_task",
            "name": "create cron job",
            "group_name": "JOB",
            "output": [
                {
                    "type": "int",
                    "name": "cron job id",
                    "key": "cron_id",
                    "schema": {
                        "enum": [],
                        "type": "int",
                        "description": "cron job id"
                    }
                },
                {
                    "type": "string",
                    "name": "cron job status",
                    "key": "status",
                    "schema": {
                        "enum": [],
                        "type": "string",
                        "description": "cron job status"
                    }
                },
                {
                    "type": "bool",
                    "name": "execution result",
                    "key": "_result",
                    "schema": {
                        "enum": [],
                        "type": "boolean",
                        "description": "execution result"
                    }
                }
            ],
            "desc": ""
        }
    ],
    "result": true
}
```

### Return Result Description

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  result    | bool      | true or false, indicate success or failure |
|  data      | dict      | data returned when result is true, details are described below |
|  message   | string    | error message returned when result is false |

#### data

| Field      | Type      | Description      |
| ------------ | ---------- | ------------------------------ |
|  inputs      |    list    |      plugin's inputs    |
|  code      |    string    |    plugin's code   |
|  name      |    string    |   plugin's name    |
|  group_name      |    string    |   plugin's group name   |
|  outputs      |    list    |   plugin's outputs   |
|  desc      |    string    |   plugin's description   |

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

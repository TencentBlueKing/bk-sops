### Functional description

modify crontab for periodic task

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
|   cron    |   dict     |   YES   |  crontab dict |

#### cron
 
 | Field          |  Type       | Required   |  Description             |
| ------------ | ------------ | ------ | ---------------- |
|   minute    |   string     |   NO   |  minute, default value is * |
|   hour    |   string     |   NO   |  hour, default value is * |
|   day_of_week    |   string     |   NO   |  day of week, default value is * |
|   day_of_month    |   string     |   NO   |  day of month, default value is * |
|   month_of_year    |   string     |   NO   |  month of year, default value is * |

### Request Parameters Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "cron" : {
        "minute": "*/1", 
        "hour": "15", 
        "day_of_week":"*", 
        "day_of_month":"*", 
        "month_of_year":"*"
    }
}
```

### Return Result Example

```
{
    "data": {
        "cron": "*/1 15 * * * (m/h/d/dM/MY)"
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
|  cron      |    string    |      crontab expression    |

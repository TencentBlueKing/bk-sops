### Function Description

Modify template notification configuration

**Request Method**: POST

### Request Parameters

#### Interface Parameters

| Field          |  Type       | Required |  Description             |
|---------------|------------|----------|-------------------------|
| template_id    |  string     |   Yes    |  Template ID |
| bk_biz_id     |  string     |   Yes    |  Project ID |
| notify_type     |  dict     |   Yes    |  Process event notification method, contains success and fail keys, see details below |
| notify_receivers     |  dict     |   Yes    |  Notification receiver configuration, see details below |
| common     |  bool     |   No    |  Whether it is a common process template, default false |
|   scope                    |   string   |   NO     |  search scope for bk_biz_id. Default is cmdb_biz, in which case the project whose bound CMDB business ID equals bk_biz_id is searched; when the value is project, the project whose project ID equals bk_biz_id is searched |

#### notify_type

| Field      | Type      | Description      |
|-----------|----------|------------------|
| success      |  list    |  Notification type list for successful execution     |
| fail      |  list    |  Notification type list for failed execution    |

#### notify_receivers

| Field      | Type      | Description      |
|-----------|----------|------------------|
| receiver_group      |  list    |  Receiver user group list     |
| more_receiver      |  string    |  Additional receivers    |
| extra_info      |  dict    |  Additional notification configuration information, see details below    |

#### notify_receivers.extra_info

| Field      | Type      | Description      |
|-----------|----------|------------------|
| bkchat      |  dict    |  BlueKing chat notification configuration, contains success and fail keys    |

#### notify_receivers.extra_info.bkchat

| Field      | Type      | Description      |
|-----------|----------|------------------|
| success      |  string    |  BlueKing chat notification configuration for successful execution     |
| fail      |  string    |  BlueKing chat notification configuration for failed execution    |

### Request Parameter Example

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx", 
    "bk_username": "xxx",
    "notify_type": {
        "success": [
            "bkchat",
            "rtx"],
        "fail": [
            "weixin",
            "voice",
            "mail",
            "sms"
        ]
    },
    "notify_receivers": {
        "receiver_group": ["Developer", "Maintainers"],
        "more_receiver": "",
        "extra_info": {
            "bkchat": {
                "success": "3654",
                "fail": "123"
            }
        }
    },
    "common": false
}
```

### Response Result Example

```
{
    "result": true,
    "data": {
        "notify_type": {
            "success": [
                "bkchat",
                "rtx"],
            "fail": [
                "weixin",
                "voice",
                "mail",
                "sms"
            ]
        },
        "notify_receivers": {
            "receiver_group": ["Developer", "Maintainers"],
            "more_receiver": "",
            "extra_info": {
                "bkchat": {
                    "success": "3654",
                    "fail": "123"
                }
            }
        },
        "template_id": 123
    },
    "code": 0
}
```

### Response Result Parameter Description

| Field      | Type      | Description      |
|-----------|----------|------------------|
| result      |  bool    |  true/false whether the operation is successful     |
| data        |  dict  |  Success data when result=true, see details below      |
| message     |  string  |  Error message when result=false     |
| code     |  int  |  Return code, 0 indicates success     |
| trace_id     |  string  |  open telemetry trace_id     |

#### data

| Field      | Type      | Description      |
|-----------|----------|------------------|
| notify_type      |  dict    |  Set notification type configuration     |
| notify_receivers     |  dict     |  Set notification receiver configuration     |
| template_id     |  int     |  Template ID     |

### Error Code Description

| Error Code      | Description      |
|-----------|------------------|
| 0      |  Success     |
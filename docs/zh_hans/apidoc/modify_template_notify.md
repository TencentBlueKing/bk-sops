### 功能描述

修改模板通知配置

**请求方法**: POST

### 请求参数

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|------------------|
|   template_id    |   string     |   是   |  模板ID |
|   bk_biz_id     |   string     |   是   |  项目ID |
|   notify_type     |   dict     |   是   |  流程事件通知方式，包含success和fail两个key，详细信息见下面说明 |
|   notify_receivers     |   dict     |   是   |  通知接收人配置，详细信息见下面说明 |
|   common     |   bool     |   否   |  是否为公共流程模板，默认false |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|


#### notify_type

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  success      |    list    |      执行成功时发送的通知类型列表     |
|  fail      |    list    |      执行失败时发送的通知类型列表    |

#### notify_receivers

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  receiver_group      |    list    |      接收用户组列表     |
|  more_receiver      |    string    |      额外接收人    |
|  extra_info      |    dict    |      额外通知配置信息，详细信息见下面说明    |

#### notify_receivers.extra_info

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  bkchat      |    dict    |      蓝鲸聊天通知配置，包含success和fail两个key    |

#### notify_receivers.extra_info.bkchat

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  success      |    string    |      执行成功时的蓝鲸聊天通知配置     |
|  fail      |    string    |      执行失败时的蓝鲸聊天通知配置    |

### 请求参数示例

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

### 返回结果示例

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

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |
|  code     |    int  |      返回码，0表示成功     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  notify_type      |    dict    |      设置的通知类型配置     |
|  notify_receivers     |    dict     |      设置的通知接收人配置     |
|  template_id     |    int     |      模板ID     |

### 错误码说明

| 错误码      | 描述      |
|-----------|----------|
|  0      |      成功     |
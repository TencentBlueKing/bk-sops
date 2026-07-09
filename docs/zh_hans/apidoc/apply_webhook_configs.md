### 功能描述

批量修改模板的webhook配置

### 请求参数

#### 接口参数

| 字段              | 类型      | 必选     | 描述                 |
|-----------------|---------|--------|--------------------|
| endpoint        | string  | 是      | webhook请求地址        |
| events          | list    | 是      | 订阅事件               |
| extra_info      | dict    | 否      | 额外参数，包含认证、请求头和重试信息 |
| enable_webhook  | bool    | 否      | webhook配置开关，默认开启   |
| template_ids    | list    | 是      | 需要修改的模板id列表        |

#### events 目前的订阅事件 task_failed（任务失败）和 task_finished（任务完成）

### 请求参数示例

```
{
     "endpoint": "https://xxx.com",
     "events": ["*"],
     "extra_info": {
          "authorization": {
               "type": "basic",  # bearer:token认证，basic：密码认证
               "username": "xxx",
               "password": "xxx",
               "token": "xxx"
          },
          "headers": [
               {
                    "key": "Content-Type",
                    "value": "application/json",
                    "doc": ""
               }
          ],
          "timeout": 10,
          "retry_times": 2,
          "interval": 60
     },
     "template_ids": [1]
}
```

关闭并清空指定模板的所有 webhook 配置
```json

{
   "enable_webhook": false,
   "template_ids": [1, 2]
}
```

### 返回结果示例

```
{
    "result": true,
    "message": "success",
    "code": 0,
    "trace_id": "00-3ada3cec713520ede2ab03b156d1a33d-66b28b7e5e7f59fe-01"
}
```

### 返回结果参数说明

| 字段         | 类型       | 描述                        |
|------------|----------|---------------------------|
| result     | bool     | true/false 操作是否成功         |
| message    | string   | result=false 时错误信息        |
| trace_id   | string   | open telemetry trace_id   |
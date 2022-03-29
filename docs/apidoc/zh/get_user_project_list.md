### 功能描述

查询用户有权限的项目列表


### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "project_id": 13,
            "bk_biz_id": 2,
            "name": "蓝鲸"
        },
        {
            "project_id": 14,
            "bk_biz_id": 3,
            "name": "la"
        }
    ],
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | 项目 ID       |
|  bk_biz_id | int        | 绑定的 CMDB 业务 ID       |
|  name  | string     | 项目名           |

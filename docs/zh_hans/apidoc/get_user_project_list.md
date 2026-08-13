### 管理员只读请求头及说明

管理员只读调用仅供已配置的 PO 后端使用。调用方必须同时发送 `X-BkSops-Admin-Read: true` 与 `X-BkSops-Audit-Operator: <已认证用户名>`。

该模式只跳过查看权限，不改变 `auth_actions`，不提供任何编辑、创建、操作或下载权限。非法声明返回 `REQUEST_FORBIDDEN_INVALID`；未发送声明时沿用原 IAM 鉴权。

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
    "trace_id": "xxx"
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | dict       | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  project_id | int        | 项目 ID       |
|  bk_biz_id | int        | 绑定的 CMDB 业务 ID       |
|  name  | string     | 项目名           |

### MCP 请求说明

当请求来源于网关MCP时，响应中不会过滤任何字段。

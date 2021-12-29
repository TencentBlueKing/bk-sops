### 请求地址

/v2/sops/node_callback/

### 请求方法

POST

### 功能描述

回调指定的节点

### 请求参数

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   bk_biz_id    |   string     |   是   |  所属业务ID |
|   task_id     |   string   |   是   |  任务ID     |
|   node_id        | string     | 是         | 节点 ID                        |
|   callback_data        | dict     | 否         | 回调数据           |           |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "app_code",
    "bk_app_secret": "app_secret",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node0df0431f8f553925af01a94854bd",
    "callback_data": {
        "data": {}
    },
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "message": "success",
    "result": true,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

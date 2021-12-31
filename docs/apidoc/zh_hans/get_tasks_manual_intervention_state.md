### 请求地址

/v2/sops/get_tasks_manual_intervention_state/

### 请求方法

POST

### 功能描述

获取一批任务的是否需要人工干预的判断状态

当流程中存在以下情况时，就判定为需要人工介入：

- 存在运行中的暂停插件节点
- 存在失败的节点
- 存在处于暂停状态的子流程
- 流程处于暂停状态

#### 通用参数

| 字段          | 类型   | 必选 | 描述                                                                             |
| ------------- | ------ | ---- | -------------------------------------------------------------------------------- |
| bk_app_code   | string | 是   | 应用ID                                                                           |
| bk_app_secret | string | 是   | 安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
| bk_token      | string | 否   | 当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取    |
| bk_username   | string | 否   | 当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户             |

#### 接口参数

| 字段         | 类型   | 必选 | 描述                                                                                                                     |
| ------------ | ------ | ---- | ------------------------------------------------------------------------------------------------------------------------ |
| bk_biz_id    | string | 是   | 模板所属业务ID                                                                                                           |
| task_id_list | array  | 是   | 任务 ID 列表                                                                                                             |
| scope        | string | 否   | 唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id_list": [30000105, 30000101, 30000100],
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": 81,
            "manual_intervention_required": false
        },
        {
            "id": 80,
            "manual_intervention_required": true
        },
        {
            "id": 79,
            "manual_intervention_required": true
        },
        {
            "id": 78,
            "manual_intervention_required": false
        },
        {
            "id": 77,
            "manual_intervention_required": false
        }
    ],
    "code": 0,
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 名称    | 类型   | 说明                                       |
| ------- | ------ | ------------------------------------------ |
| result  | bool   | true/false 查询成功与否                    |
| data    | dict   | result=true 时返回数据，详细信息见下面说明 |
| message | string | result=false 时错误信息                    |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data 说明
| 名称                         | 类型 | 说明             |
| ---------------------------- | ---- | ---------------- |
| id                           | int  | 任务 ID          |
| manual_intervention_required | bool | 是否需要人工干预 |

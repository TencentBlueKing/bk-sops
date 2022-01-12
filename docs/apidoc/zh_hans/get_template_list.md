### 请求地址

/v2/sops/get_template_list/

### 请求方法

GET

### 功能描述

查询业务下的模板列表

### 请求参数

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|---------------|------------|--------|-------------------|
| bk_biz_id     |  string    | 是     | 模板所属业务ID     |
| template_source | string   | 否     | 流程模板来源，business:默认值，业务流程，common：公共流程 |
| id_in         |  string    | 否     | 流程模板id来源列表，以逗号`,`分隔 |
| name_keyword  |  string    | 否     | 流程模板名称关键词，英文不区分大小写 |
| scope | string | 否 | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目|

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "id_in": "1, 2, 3"
    "template_source": "business",
    "scope": "cmdb_biz",
    "name_keyword": "xxx"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "category": "Other",
            "edit_time": "2018-04-23 17:30:48 +0800",
            "create_time": "2018-04-23 17:26:40 +0800",
            "name": "快速执行脚本",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "id": 32,
            "editor": "admin",
            "creator":"admin",
            "auth_actions": [
                "flow_create",
                "flow_view",
                "flow_edit",
                "flow_delete",
                "flow_create_task",
                "flow_create_mini_app",
                "flow_create_periodic_task",
                "flow_create_clocked_task"
            ]
        },
        {
            "category": "Other",
            "edit_time": "2018-04-19 12:04:42 +0800",
            "create_time": "2018-04-19 12:04:42 +0800",
            "name": "new201804191218",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "id": 31,
            "editor": null,
            "creator": "admin",
            "auth_actions": [
                "flow_create",
                "flow_view",
                "flow_edit",
                "flow_delete",
                "flow_create_task",
                "flow_create_mini_app",
                "flow_create_periodic_task",
                "flow_create_clocked_task"
            ]
        },
        {
            "category": "Other",
            "edit_time": "2018-04-18 17:09:39 +0800",
            "create_time": "2018-04-16 21:43:15 +0800",
            "name": "new20180416213944",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "id": 30,
            "editor": "admin",
            "creator": "admin",
            "auth_actions": [
                "flow_create",
                "flow_view",
                "flow_edit",
                "flow_delete",
                "flow_create_task",
                "flow_create_mini_app",
                "flow_create_periodic_task",
                "flow_create_clocked_task"
            ]
        },
    ],
    "request_id": "xxx",
    "trace_id": "xxx"
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
| result    | bool     | true/false 查询成功与否 |
| data      | list     | result=true时模板列表，item 信息见下面说明 |
| message   | string   | result=false时错误信息 |
|  request_id     |    string  |      esb 请求 id     |
|  trace_id     |    string  |      open telemetry trace_id     |

#### data

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  bk_biz_id      |    string    |      模板所属业务ID     |
|  bk_biz_name      |    string    |      模板所属业务名称    |
|  id      |    int    |      模板ID    |
|  name      |    string    |      模板名称    |
|  category      |    string    |      模板分类，分类信息见下面说明    |
|  creator      |    string    |      模板创建人   |
|  create_time      |    string    |      模板创建时间   |
|  editor      |    string 或者 null    |      模板编辑人   |
|  edit_time      |    string   |      模板最新编辑时间   |
|  auth_actions      |    array   |      用户对该资源有权限的操作   |

#### data.category

| 返回值        | 描述     |
|--------------|----------|
| OpsTools     | 运维工具  |
| MonitorAlarm | 监控告警  |
| ConfManage   | 配置管理  |
| DevTools     | 开发工具  |
| EnterpriseIT | 企业IT   |
| OfficeApp    | 办公应用  |
| Other        | 其它     |

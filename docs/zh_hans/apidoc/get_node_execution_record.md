### 功能描述

获取节点最近执行记录

#### 接口参数

| 字段               | 类型     | 必选  | 描述                                                                                                       |
|------------------|--------|-----|----------------------------------------------------------------------------------------------------------|
| bk_biz_id        | string | 是   | 项目唯一 ID，项目 ID 或 CMDB 业务 ID                                                                               |
| template_id      | string | 是   | 流程ID                                                                                                     |
| template_node_id | string | 是   | 查询节点对应的流程节点 ID                                                                                           |
| scope            | string | 否   | bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "10",
    "template_node_id": "node0df0431f8f553925af01a94854bd",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "execution_time": [
            {
                "archived_time": "2019-01-17 22:02:46 +0800",
                "elapsed_time": 9
            },
            {
                "archived_time": "2019-01-16 15:30:12 +0800",
                "elapsed_time": 12
            }
        ],
        "total": 2
    },
    "message": "",
    "code": 0
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result   |    bool    |      true/false 查询成功与否     |
|  data     |    dict    |      result=true 时返回数据，详细信息见下面说明     |
|  message  |    string  |      result=false 时错误信息     |
|  code     |    int     |      错误码，0 表示成功     |

#### data

| 字段             | 类型     | 描述               |
|----------------|--------|------------------|
| execution_time | list   | 节点最近执行记录列表，详情见下面说明 |
| total          | int    | 节点执行总次数          |

#### data.execution_time[]

| 字段            | 类型     | 描述                 |
|---------------|--------|--------------------|
| archived_time | string | 归档时间               |
| elapsed_time  | int    | 执行耗时，单位秒           |

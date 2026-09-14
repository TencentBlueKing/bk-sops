### 功能描述

获取任务操作记录

#### 接口参数

| 字段          |  类型       | 必选   |  描述            |
|---------------|------------|--------|------------------|
|   task_id     |   string   |   是   |  任务 ID |
|   bk_biz_id   |   string   |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   node_id     |   string   |   否   |  任务节点 ID，不传则返回任务下所有操作记录 |
|   scope       |   string   |   否   |  bk_biz_id 检索的作用域。默认为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "task_id": "10",
    "node_id": "node_id",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "project_id": 2,
            "instance_id": 10,
            "operator": "admin",
            "operate_type": "retry",
            "operate_type_name": "重试",
            "operate_source": "app",
            "operate_source_name": "app 页面",
            "node_id": "n03f24c7017b3b6f95fbd3aa9ef6bf18",
            "operate_date": "2026-07-31T10:50:00+08:00",
            "extra_info": {}
        },
        {
            "project_id": 2,
            "instance_id": 10,
            "operator": "admin",
            "operate_type": "nodes_action",
            "operate_type_name": "节点操作",
            "operate_source": "api",
            "operate_source_name": "api 接口",
            "node_id": "na4e7a1439ba3037af5bcf8c22a5967f",
            "operate_date": "2026-07-31T10:55:00+08:00",
            "extra_info": {}
        }
    ],
    "code": 0,
    "trace_id": "xxx"
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 操作是否成功        |
|  data         | array      | result=true 时返回的操作记录列表 |
|  message      | string     | result=false 时错误信息        |
|  trace_id     | string     | open telemetry trace_id        |

#### data

|      名称           |     类型   |               说明             |
| ------------------- | ---------- | ------------------------------ |
|  project_id         | int        | 项目ID                        |
|  instance_id        | int        | 任务实例ID                     |
|  operator           | string     | 操作人                         |
|  operate_type       | string     | 操作类型                       |
|  operate_type_name  | string     | 操作类型中文名                  |
|  operate_source     | string     | 操作来源                       |
|  operate_source_name| string     | 操作来源中文名                  |
|  node_id            | string     | 任务实例节点ID，为空表示任务级操作 |
|  operate_date       | string     | 操作时间                       |
|  extra_info         | object     | 任务实例节点拓展信息             |

#### data.operate_type

| 返回值         | 描述           |
|----------------|----------------|
| none           | 无操作         |
| create         | 创建           |
| task_clone     | 克隆(创建)     |
| start          | 执行           |
| pause          | 暂停           |
| resume         | 继续           |
| revoke         | 撤消           |
| delete         | 删除           |
| update         | 修改           |
| callback       | 回调           |
| retry          | 重试           |
| skip           | 跳过           |
| skip_exg       | 跳过失败网关    |
| pause_subproc  | 暂停子流程      |
| resume_subproc | 继续子流程      |
| nodes_action   | 节点操作        |
| forced_fail    | 强制失败        |

#### data.operate_source

| 返回值  | 描述           |
|---------|----------------|
| app     | app 页面       |
| api     | api 接口       |
| parent  | 父任务         |

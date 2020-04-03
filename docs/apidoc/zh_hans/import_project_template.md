### 功能描述

导入项目流程

### 请求参数

{{ common_args_desc }}

#### 接口参数

|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   template_data    |   string     |   是   |  项目流程数据，即从标准运维 - 项目流程 - 导出功能下载的文件的内容 |
|   project_id    |   string     |   是   |  项目 ID |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "template_data": "xxx",
    "project_id": "3,
}
```

### 返回结果示例

```
{
    "message": "Successfully imported 2 flows",
    "data": {
        "count": 2
    },
    "result": true
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  data         | dict        | 返回数据                    |

#### data

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  count      |    int    |      导入的流程数    |

### 功能描述

获取模板的执行方案列表

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   template_id       |   int     |   是   |  模板 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "bk_biz_id": "2",
    "template_id": "12",
    "scope": "cmdb_biz"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "id": "47-1",
            "name": "1",
            "data": "[\"node7082deed0725aed8c72ecff079ba\",\"node88d9050f288765b94a15cbe023ab\"]"
        },
        {
            "id": "47-2",
            "name": "2",
            "data": "[\"node7082deed0725aed8c72ecff079ba\"]"
        },
        {
            "id": "47-3",
            "name": "3",
            "data": "[\"node88d9050f288765b94a15cbe023ab\"]"
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

#### data说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  id  | string     | 执行方案 ID           |
|  name  | string     | 执行方案名           |
|  data  | string     | 执行方案中包含的节点 ID 列表  |
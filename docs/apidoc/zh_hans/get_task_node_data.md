### 功能描述

获取任务节点的数据

### 请求参数

{{ common_args_desc }}

#### 接口参数

|   参数名称   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   app_code      |   string     |   是   |  蓝鲸应用编码    |
|   app_secret    |   string     |   是   |  蓝鲸应用私密key |
|   access_token |   string     |   否   |  用户登录票据，bk_token 为空时必填 |
|   bk_token       |   string     |   否   |  用户登录票据，access_token 为空时必填 |
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   task_id       |   int     |   是   |  任务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |
| node_id        | string     | 是         | 节点 ID                        |
| component_code| string     | 是         | 原子编码                       |
| subprocess_stack| string   | 否         | 子流程堆栈，json 格式的列表    |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": 11,
    "node_id": "ndfbcbdc77e9350ba18222dc4a0a435f",
    "component_code": "sleep_timer"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": {
        "inputs": {
            "bk_timing": "123"
        },
        "outputs": [
            {
                "name": "执行结果",
                "key": "_result",
                "value": "",
                "preset": true
            },
            {
                "name": "循环次数",
                "key": "_loop",
                "value": "",
                "preset": true
            }
        ],
        "ex_data": ""
    },
    "message": "",
    "code": 0
}
```

### 返回结果说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  data         | object     | result=true 时返回数据，详情见下面说明 |
|  message      | string     | result=false 时错误信息        |

#### data说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  inputs       | object     | 输入参数，key：value格式       |
|  outputs      | array      | 输出参数，详情见下面说明       |
|  ex_data      | string     | 节点执行失败详情，json字符串或者HTML字符串、普通字符串 |

##### outputs[]说明
|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  name         | string     | 输出参数名称                   |
|  value        | string、int、bool、dict、list | 输出参数值  |
|  key          | string     | 输出参数 KEY                   |
|  preset       | bool       | 是否是原子定义中预设输出变量   |

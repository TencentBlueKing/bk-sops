### 功能描述

修改周期任务的全局参数

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
|---------------|------------|--------|------------------|
|   task_id    |   string     |   是   |  周期任务ID |
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   constants    |   dict     |   否   | 任务全局参数，详细信息见下面说明 |

#### constants.KEY

变量 KEY，${key} 格式

#### constants.VALUE

变量值

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2",
    "task_id": "8",
    "constants": {
        "${bk_timing}": "100"
    }
}
```

### 返回结果示例

```
{
    "data": {
        "${bk_timing}": {
            "source_tag": "sleep_timer.bk_timing",
            "source_info": {
                "node76393dcfedcf73dbc726f1c4786d": [
                    "bk_timing"
                ]
            },
            "name": "定时时间",
            "custom_type": "",
            "index": 0,
            "value": "15",
            "show_type": "show",
            "source_type": "component_inputs",
            "key": "${bk_timing}",
            "validation": "",
            "desc": ""
        }
    },
    "result": true
}
```

### 返回结果参数说明

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

#### data.KEY
全局变量 KEY，${key} 格式

#### data.VALUE

|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  key      |    string    |      同 KEY     |
|  name      |    string    |      变量名字    |
|  index      |    int    |      变量在模板中的显示顺序    |
|  desc      |    string    |      变量说明   |
|  source_type      |    string    |      变量来源, 取值范围 custom: 自定义变量，component_inputs: 从标准插件输入参数勾选，component_outputs：从标准插件输出结果中勾选   |
|  custom_type      |    string    |      source_type=custom 时有效，自定义变量类型， 取值范围 input: 输入框，textarea: 文本框，datetime: 日期时间，int: 整数|
|  source_tag      |    string    |      source_type=component_inputs/component_outputs 时有效，变量的来源标准插件   |
|  source_info   |   dict  |  source_type=component_inputs/component_outputs 时有效，变量的来源节点信息 |

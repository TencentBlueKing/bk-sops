### 功能描述

获取某个业务下所有的可用插件

#### 通用参数

|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

| 字段          |  类型       | 必选   |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_biz_id       |   string     |   是   |  项目唯一 ID，项目 ID 或 CMDB 业务 ID |
|   scope       |   string     |   否   |  唯一 ID 的范围，取值为 cmdb_biz 或 project，为 cmdb_biz 时 bk_biz_id 代表业务 ID，反之代表项目 ID，不传时默认为 cmdb_biz |


### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_biz_id": "2"
}
```

### 返回结果示例

```
{
    "result": true,
    "data": [
        {
            "inputs": [],
            "outputs": [
                {
                    "name": "执行结果",
                    "key": "_result",
                    "type": "bool",
                    "schema": {
                        "type": "boolean",
                        "description": "是否执行成功",
                        "enum": []
                    }
                },
                {
                    "name": "循环次数",
                    "key": "_loop",
                    "type": "int",
                    "schema": {
                        "type": "int",
                        "description": "循环执行次数",
                        "enum": []
                    }
                }
            ],
            "desc": "",
            "code": "job_push_local_files",
            "name": "分发本地文件",
            "group_name": "作业平台(JOB)",
            "version": "1.0.0"
        }
    ]
}
```

### 返回结果说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict      |      result=true 时成功数据，详细信息请见下面说明     |
|  message        |    string      |      result=false 时错误信息     |

##### data[item] 说明
|   名称   |  类型  |           说明             |
| ------------ | ---------- | ------------------------------ |
|  inputs      |    array    |      插件输入参数列表    |
|  outputs      |    array    |      插件输出参数列表    |
|  desc      |    string    |      插件描述    |
|  code      |    string    |      插件代码    |
|  name      |    string    |      插件名    |
|  group_name      |    string    |      插件组名    |
|  version      |    name    |      插件版本    |
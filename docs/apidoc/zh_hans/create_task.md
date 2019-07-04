### 功能描述

通过流程模板创建任务

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
|   bk_biz_id    |   string     |   是   |  模板所属业务ID |
|   template_id     |   string     |   是   |  模板ID |
|   name     |   string     |   是   |  任务名称 |
|   flow_type     |   string     |   否   |  任务流程类型，common: 常规流程，common_func：职能化流程 |
|   constants     |   dict     |   否   |  任务全局参数，详细信息见下面说明 |

#### constants.KEY

变量 KEY，${key} 格式

#### constants.VALUE

变量值，value 的类型和从模板获取的全局变量中 value 类型保持一致

### 请求参数示例

```python
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "name": "tasktest",
    "flow_type": "common",
    "constants": {
        "${content}: "echo 1",
        "${params}": "",
        "${script_timeout}": 20
    }
}
```

### 返回结果示例

```python
{
    "result": true,
    "data": {
        "task_id": 10
    }
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |

####  data 说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  task_id      |    int    |      任务实例ID     |

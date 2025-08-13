### 功能描述

插件请求转发

### 请求参数

#### 接口参数

| 字段     | 类型     | 必选 | 描述                             |
|--------|--------|----|--------------------------------|
| url    | string | 是  | 实际要请求的插件接口路径                   |
| method | string | 否  | HTTP方法，支持"GET"或"POST", 默认"GET" |
| data   | dict   | 否  | 当method为POST时, 需要传递的请求数据       |

### 请求参数示例

```
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_username": "xxx",
    "url": "/pipeline/xxxxxxx/xxx/",
    "method": "GET"
}
```

### 返回结果示例

```
{
   "result": true/false
   "data":{
      无固定返回结构，以请求的后端接口返回为准
   }
}
```

### 返回结果参数说明

| 字段      | 类型      | 描述      |
|-----------|----------|-----------|
|  result      |    bool    |      true/false 操作是否成功     |
|  data        |    dict  |      result=true 时成功数据，详细信息请见下面说明      |
|  message     |    string  |      result=false 时错误信息     |

#### data
无固定返回结构，以请求的后端接口返回为准

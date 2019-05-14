### 功能描述

导入公共流程

### 请求参数

#### 通用参数
|   字段           |  类型       | 必选     |  描述             |
|-----------------|-------------|---------|------------------|
|   bk_app_code   |   string    |   是    |  应用ID |
|   bk_app_secret |   string    |   是    |  安全密钥(应用 TOKEN)，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取 |
|   bk_token      |   string    |   否    |  当前用户登录态，bk_token与bk_username必须一个有效，bk_token可以通过Cookie获取  |
|   bk_username   |   string    |   否    |  当前用户用户名，应用免登录态验证白名单中的应用，用此字段指定当前用户              |

#### 接口参数

|   字段   |    参数类型  |  必须  |     参数说明     |
| ------------ | ------------ | ------ | ---------------- |
|   data_file    |   file     |   是   |  公共流程数据文件 |
|   override        | bool     | 否         | 是否覆盖 ID 相同的流程           |           |

### 请求参数示例

```
import requests
kwargs = {
    "app_code": "app_code",
    "app_secret": "app_secret",
    "access_token": "access_token",
    "data_file": data_file
}
response = requests.post("http://{stageVariables.domain}/apigw/import_common_template/", kwargs)
result = response.json()
```

### 返回结果示例

```
{
    "message": "Successfully imported 2 common flows",
    "data": 2,
    "result": true
}
```

### 返回结果参数说明

|      名称     |     类型   |               说明             |
| ------------  | ---------- | ------------------------------ |
|  result       | bool       | true/false 成功与否            |
|  message      | string     | result=false 时错误信息        |
|  data         | int        | 导入的流程数                    |

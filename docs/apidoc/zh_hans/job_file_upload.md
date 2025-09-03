### 功能描述

插件【作业平台(JOB)-分发本地文件】上传文件

### 请求头参数

| 字段          |  类型       | 必选   | 描述             |
|---------------|------------|--------|----------------|
| UPLOAD-TICKET     | string     |   是   | 申请的Job文件临时上传凭证 |
| APP-PROJECT-SCOPE     | string     |   是   | bk_biz_id 检索的作用域。当值为 cmdb_biz，此时检索的是绑定的 CMDB 业务 ID 为 bk_biz_id 的项目；当值为 project 时则检索项目 ID 为 bk_biz_id 的项目 |

### 请求参数

要上传的文件

### 路径参数

| 字段          |  类型       | 必选   | 描述          |
|---------------|------------|--------|-------------|
| bk_biz_id     | string     |   是   | JOB文件上传业务ID |

### 请求示例

```
import json
import requests

url = "http://{apigw_host}/job_file_upload/{bk_biz_id}/"

headers = {
    'UPLOAD-TICKET': '40f7f7546a7e358a99e7f856882a7e15',
    'APP-PROJECT-SCOPE': 'cmdb_biz',
    "X-Bkapi-Authorization": json.dumps(
        {
            "bk_app_code": "xxx",
            "bk_app_secret": "xxs",
            "bk_username": "xxx"
        }
    ),
}

files = [
    ('file', ('a.log', open('a.log', 'rb'), 'application/octet-stream'))
]

response = requests.request("POST", url, headers=headers, files=files)

print(response.text)
```

### 返回结果示例

```
{
    "result": true,
    "tag": {
        "type": "job_repo",
        "tags": {
            "file_path": "2/639ba64d-6e69-4f7e-8f52-96bc45cb6243/admin/a.log",
            "name": "a.log"
        }
    },
    "md5": "b0ac23ae783ea58bb52c6bcd62b3246f"
}
```

### 返回结果说明

| 名称      | 类型     | 说明                     |
|---------|--------|------------------------|
| result  | bool   | true/false 操作是否成功      |
| tag    | object | result=true 时成功上传文件信息  |
| md5    | string | result=true 时成功上传文件md5 |
| message | string | result=false 时错误信息     |



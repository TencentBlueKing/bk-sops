### Function Description

Upload files for the plugin "JOB-Push Local File"

### Request Header Parameters

| Field          |  Type       | Required | Description             |
|---------------|------------|----------|------------------------|
| UPLOAD-TICKET     | string     |   Yes    | Temporary upload credential for Job files |
| APP-PROJECT-SCOPE     | string     |   Yes    | The scope for retrieving bk_biz_id. When the value is cmdb_biz, it retrieves the project with the bound CMDB business ID as bk_biz_id; when the value is project, it retrieves the project with the project ID as bk_biz_id |

### Request Parameters

The file to be uploaded

### Path Parameters

| Field          |  Type       | Required | Description          |
|---------------|------------|----------|---------------------|
| bk_biz_id     | string     |   Yes    | Business ID for JOB file upload |

### Request Example


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

### Response Example

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

### Response Description

| Name      | Type     | Description                     |
|---------|--------|--------------------------------|
| result  | bool   | true/false whether the operation was successful      |
| tag    | object | Successfully uploaded file information when result=true  |
| md5    | string | MD5 of the successfully uploaded file when result=true |
| message | string | Error message when result=false     |




### 功能描述

申请插件【作业平台(JOB)-分发本地文件】的文件上传临时凭证

### 请求参数

无

### 路径参数

无

### 返回结果示例

```
{
    "result": true,
    "data": {
        "ticket": "d8f8255a783639459f35c182c6671a89"
    }
}
```

### 返回结果说明

| 名称      | 类型     | 说明                           |
|---------|--------|------------------------------|
| result  | bool   | true/false 操作是否成功            |
| data    | object | result=true 时成功数据，详细信息请见下面说明 |
| data.ticket   | string | Job文件上传临时凭证                          |
| message | string | result=false 时错误信息           |



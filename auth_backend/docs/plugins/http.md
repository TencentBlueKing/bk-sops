# Http plugins

## HttpResponseAuthFailed

`HttpResponseAuthFailed` 继承自 `django.http.HttpResponse`，是用于表示用户没有权限进行当前操作的响应，其特点如下：

- 状态码为 `499`
- 返回当前用户所缺少的权限相关信息

其返回的数据示例如下：

```JSON
{
   "message":"you have no permission to operate",
   "code":9900403,
   "data":{

   },
   "result":false,
   "permission":[
      {
         "system_name":"标准运维",
         "scope_type":"system",
         "action_name":"查看",
         "scope_id":"bk_sops",
         "scope_name":"标准运维",
         "system_id":"bk_sops",
         "resources":[
            [
               {
                  "resource_type_name":"项目",
                  "resource_name":"secret_project",
                  "resource_type":"project",
                  "resource_id":8
               }
            ]
         ],
         "action_id":"view"
      }
   ]
}
```


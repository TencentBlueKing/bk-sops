# Tastypie Resource

auth backend 提供了与 tastypie 中 Resource 相关的一些插件，这些插件能够帮助你处理与 Resource 相关的权限数据的问题。

## BkSaaSLabeledDataResourceMixin

`auth_backend.plugins.tastypie.resources.BkSaaSLabeledDataResourceMixin` 提供了以下功能：

- 在返回资源实例列表时添加当前资源相关的权限数据及用户对每个资源的权限信息：
  - `meta.auth_operations`：当前请求的资源所对应的权限模型中 operation 及其依赖的 action 的相关信息
  - `meta.auth_resource`：当前请求的资源所对应的权限模型的相关信息
  - `objects.{instance}.auth_actions`：对于 `instance` 这个资源实例，当前用户拥有权限的 action 列表 
- 在返回资源实例详情时添加当前资源相关的权限数据及用户对当前实例的权限信息：
  - `auth_actions`：对于当前资源实例，当前用户拥有权限的 action 列表 
  - `auth_operations`：当前请求的资源所对应的权限模型中 operation 及其依赖的 action 的相关信息
  - `auth_resource`：当前请求的资源所对应的权限模型的相关信息


使用时只需要将 `BkSaaSLabeledDataResourceMixin` 混入相应的 Resource 类中，并在 `Resource.Meta` 中将 `auth_resource` 设置为当前资源对应的权限模型即可：

```python
from tastypie.resources import ModelResource

from auth_backend.plugins.tastypie.resources import BkSaaSLabeledDataResourceMixin

from somewhere import project_resource

class ProjectResource(ModelResource, BkSaaSLabeledDataResourceMixin):
    ...

    class Meta():
        auth_resource = project_resource

    ...

```

**注意，如果你的资源作用域不是固定的，需要在 `Meta` 中混入相应的[作用域探测器](inspect.md)：**

```python
class ProjectResource(ModelResource, BkSaaSLabeledDataResourceMixin):
    ...

    class Meta():
        auth_resource = project_resource
        scope_inspect = my_scope_inspect

    ...

```


### 资源列表示例

```json
{
   "meta":{
      "auth_operations":[
         {
            "actions":[
               {
                  "id":"view",
                  "name":"查看"
               }
            ],
            "actions_id":[
               "view"
            ],
            "operate_id":"view"
         },
         {
            "actions":[
               {
                  "id":"view",
                  "name":"查看"
               },
               {
                  "id":"edit",
                  "name":"编辑"
               }
            ],
            "actions_id":[
               "view",
               "edit"
            ],
            "operate_id":"edit"
         },
         ...
      ],
      "auth_resource":{
         "resource":{
            "resource_type":"flow",
            "resource_type_name":"流程模板"
         },
         "scope_id":"bk_sops",
         "scope_name":"标准运维",
         "scope_type":"system",
         "system_id":"bk_sops",
         "system_name":"标准运维"
      },
      "limit":15,
      "next":null,
      "offset":0,
      "previous":null,
      "total_count":7
   },
   "objects":[
      {
         "auth_actions":[
            "edit",
            "create_task",
            "create_periodic_task",
            "create_mini_app",
            "view",
            "delete"
         ],
         "id": 1,
         ...
      },
      ...
   ]
}
```

### 资源实例示例

```json
{
   "auth_actions":[
      "edit",
      "create_task",
      "create_periodic_task",
      "create_mini_app",
      "view",
      "delete"
   ],
   "auth_operations":[
      {
         "actions":[
            {
               "id":"view",
               "name":"查看"
            }
         ],
         "actions_id":[
            "view"
         ],
         "operate_id":"view"
      },
      {
         "actions":[
            {
               "id":"view",
               "name":"查看"
            },
            {
               "id":"edit",
               "name":"编辑"
            }
         ],
         "actions_id":[
            "view",
            "edit"
         ],
         "operate_id":"edit"
      },
      ...
   ],
   "auth_resource":{
      "resource":{
         "resource_type":"flow",
         "resource_type_name":"流程模板"
      },
      "scope_id":"bk_sops",
      "scope_name":"标准运维",
      "scope_type":"system",
      "system_id":"bk_sops",
      "system_name":"标准运维"
   },
   "id": 1,
   ...
}
```

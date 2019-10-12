# Shortcut plugins

auth backend 提供了一些能够直接使用的便捷函数，方便开发者在某些场景下方便的进行与权限相关的一些操作：

## verify_or_raise_auth_failed

`verify_or_raise_auth_failed` 可以在 django 处理请求的过程中校验某个主体是否拥有**某个资源实例的某些权限**，否则抛出 `AuthFailedException` 异常，其接受以下参数：

- `principal_type`：鉴权主体类型
- `principal_id`：鉴权主体 ID
- `resource`：资源模型
- `actions_ids`：需要鉴权的 action id 列表
- `instance`：资源实例，若操作与实例无关此字段应为 `None`
- `status`（可选）：抛出的 `AuthFailedException` 中 `status` 字段的值，默认为 `499`
- `scope_id`（可选）：资源实例的作用域 ID，若传空则通过传入的资源模型来获取相应的作用域 ID

### 使用示例

下面的示例展示了在一个 view 函数中校验当前用户是否拥有某个模板的 `view` 权限：

```python

from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed

from somewhere import task_template_resource

@require_POST
def collect(request, project_id):

    template = get_template_from_somewhere()

    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=task_template_resource,
                                action_ids=[task_template_resource.actions.view.id],
                                instance=template)

```

## batch_verify_or_raise_auth_failed

`batch_verify_or_raise_auth_failed` 可以在 django 处理请求的过程中校验某个主体是否拥有**某些资源实例的某些权限**，否则抛出 `AuthFailedException` 异常，其接受以下参数：

- `principal_type`：鉴权主体类型
- `principal_id`：鉴权主体 ID
- `perms_tuples`：权限元组列表，元组的格式为 `(resource, action_ids, instance)`
  - `resource`：资源模型
  - `actions_ids`：需要鉴权的 action id 列表
  - `instance`：资源实例，若操作与实例无关此字段应为 `None`
- `status`（可选）：抛出的 `AuthFailedException` 中 `status` 字段的值，默认为 `499`
- `scope_id`（可选）：资源实例的作用域 ID，若传空则通过传入的资源模型来获取相应的作用域 ID

### 使用示例

下面的示例展示了在一个 view 函数中校验当前用户是否拥有一个模板列表中所有实例的 `view` 权限：

```python

from auth_backend.plugins.shortcuts import batch_verify_or_raise_auth_failed

from somewhere import task_template_resource

@require_POST
def collect(request, project_id):
    templates = get_template_list_from_somewhere()
    perms_tuples = [(task_template_resource, [task_template_resource.actions.view.id], t) for t in templates]
    batch_verify_or_raise_auth_failed(principal_type='user',
                                        principal_id=request.user.username,
                                        perms_tuples=perms_tuples)

```

## verify_or_return_insufficient_perms

`verify_or_return_insufficient_perms` 能够校验某个主体是否拥有**某些资源实例的某些权限**，并返回该主体缺少的操作权限的信息，其接受以下参数：

- `principal_type`：鉴权主体类型
- `principal_id`：鉴权主体 ID
- `perms_tuples`：权限元组列表，元组的格式为 `(resource, action_ids, instance)`
  - `resource`：资源模型
  - `actions_ids`：需要鉴权的 action id 列表
  - `instance`：资源实例
- `scope_id`（可选）：资源实例的作用域 ID，若传空则通过传入的资源模型来获取相应的作用域 ID

其返回的数据格式如下：

```python
[
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
      },
      ...
   ]
```

### 使用示例

```python

from auth_backend.plugins.shortcuts import batch_verify_or_raise_auth_failed

templates = get_template_list_from_somewhere()
perms_tuples = [(task_template_resource, [task_template_resource.actions.view.id], t) for t in templates]
permissions = verify_or_return_insufficient_perms(principal_type='user',
                                                  principal_id=request.user.username,
                                                  perms_tuples=perms_tuples)

```

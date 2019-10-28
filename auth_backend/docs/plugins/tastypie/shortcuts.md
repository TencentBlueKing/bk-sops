# Tastypie shortcuts

auth backend 提供了一些在 tastypie 框架下能够直接使用的便捷函数，方便开发者在 tastypie 中的某些场景下方便的进行与权限相关的一些操作：

## verify_or_raise_immediate_response

`verify_or_raise_immediate_response` 可以在 tastypie 处理请求的过程中校验某个主体是否拥有**某个资源实例的某些权限**，否则抛出 `ImmediateHttpResponse` 异常，并返回主体当前缺少的操作权限，其接受以下参数：

- `principal_type`：鉴权主体类型
- `principal_id`：鉴权主体 ID
- `resource`：资源模型
- `actions_ids`：需要鉴权的 action id 列表
- `instance`：资源实例，若操作与实例无关此字段应为 `None`
- `scope_id`（可选）：资源实例的作用域 ID，若传空则通过传入的资源模型来获取相应的作用域 ID

### 使用示例

下面的示例展示了在 tastypie Resource 的 `obj_delete` 方法中校验当前用户是否拥有某个模板的 `edit` 权限：

```python

from auth_backend.plugins.tastypie.shortcuts import verify_or_raise_immediate_response

from somewhere import task_template_resource

class SomeResource():

    def obj_delete(self, bundle, **kwargs):

        template = get_template_instance_from_somewhere()

        # 鉴权通过则继续往下处理，否则立即返回响应
        verify_or_raise_immediate_response(principal_type='user',
                                           principal_id=bundle.request.user.username,
                                           resource=task_template_resource,
                                           action_ids=[task_template_resource.actions.edit.id],
                                           instance=template)
```

## batch_verify_or_raise_immediate_response

`batch_verify_or_raise_immediate_response` 可以在 tastypie 处理请求的过程中校验某个主体是否拥有**某些资源实例的某些权限**，否则抛出 `ImmediateHttpResponse` 异常，并返回主体当前缺少的操作权限，其接受以下参数：

- `principal_type`：鉴权主体类型
- `principal_id`：鉴权主体 ID
- `perms_tuples`：权限元组列表，元组的格式为 `(resource, action_ids, instance)`
  - `resource`：资源模型
  - `actions_ids`：需要鉴权的 action id 列表
  - `instance`：资源实例，若操作与实例无关此字段应为 `None`
- `scope_id`（可选）：资源实例的作用域 ID，若传空则通过传入的资源模型来获取相应的作用域 ID

### 使用示例

下面的示例展示了在 tastypie Resource 的 `obj_create` 方法中校验当前用户是否拥有某个项目的 `use_common_template` 权限及某个模板的 `create_task` 权限：

```python

from auth_backend.plugins.tastypie.shortcuts import batch_verify_or_raise_immediate_response

from somewhere import project_resource, common_template_resource

class SomeResource():

    def obj_create(self, bundle, **kwargs):

            project = get_project_instance_from_somewhere()
            template = get_common_template_instance_from_somewhere()

            # 鉴权通过则继续往下处理，否则立即返回响应
            perms_tuples = [(project_resource, [project_resource.actions.use_common_template.id], project),
                            (common_template_resource, [common_template_resource.actions.create_task.id], template)]
            batch_verify_or_raise_immediate_response(principal_type='user',
                                                     principal_id=bundle.request.user.username,
                                                     perms_tuples=perms_tuples)

```
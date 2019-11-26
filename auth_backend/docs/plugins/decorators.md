# Decorator plugins

## verify_perms

如果系统中存在基于 function 的却需要进行鉴权的 django view，那么 `verify_perms` 可以帮到你，他可以在 view 函数执行前校验当前用户是否有某个资源或者某个资源实例的某些权限，其接受以下参数：

- `auth_resource`：需要进行权限校验的资源模型
- `actions`：需要进行权限校验的 action id 列表
- `resource_get`：传入 `None` 则进行不绑定资源实例的操作权限校验，传入的数据应为 `{'from': '', 'key': ''}` 格式的字典
  - `from`：获取资源实例唯一键的位置，选项有：`args`, `kwargs`，若为其他值，则从 `request` 对象的 `request.method` 字段中获取
  - `key`：存储资源唯一键的字段名
- `scope_id_get`（可选）：应为一个可调用对象，接收当前 `request` 对象，并返回当前请求实例的作用域 ID

### 使用示例

下面的例子展示了如何从当前请求的 `request` 对象的 `GET` 对象的 `instance_id` 字段中获取任务实例的 ID，并校验当前用户是否用该实例的 `view` 权限。

```python

from auth_backend.plugins.decorators import verify_perms

@require_GET
@verify_perms(auth_resource=taskflow_resource,
              resource_get={'from': 'request', 'key': 'instance_id'},
              actions=[taskflow_resource.actions.view])
def status(request, project_id):
    pass
```
# Resource 探测器

在 tastypie 处理请求的上下文中，如果需要对拥有动态作用域的资源进行鉴权，那就需要让 auth backend 能够从当前处理请求的上下文中获取到用户当前操作所属的作用域，此时就需要依赖一个 Resource 探测器。与实例探测器相似，Resource 探测器负责从当前请求上下文中获取作用域以及其他相关信息，只不过 tastypie 下的 Resource 探测器要处理的是 tastypie 中的 bundle 而非实例对象。

作用域探测器需要从 bundle 中获取以下信息：

- 作用域 ID
- 资源实例 ID

## 探测器需要处理的上下文

在 tastypie 中，作用域探测器需要处理以下 tastypie 函数中的 bundle 上下文：

- `dehydrate`
- `alter_detail_data_to_serialize`
- `read_detail`
- `read_list`
- `create_detail`
- `update_list`
- `update_detail`
- `delete_list`
- `delete_detail`

## 示例

下面是一个作用域探测器的示例，该探测器专门用于处理 Task 操作的请求，其负责：

- 将 bundle 所包含的 `obj` 对象中所关联的业务的 ID 作为当前作用域 ID 返回
- 将 bundle 所包含的 `obj` 对象中关联的 `relate_obj` 对象的 ID 作为当前实例的 ID 返回

```python
from auth_backend.plugins.tastypie.inspect import ScopeInspect

class TaskOperationScopeInspect(ScopeInspect):

    def scope_id(self, bundle):
        return bundle.obj.business.id
    
    def resource_id(self, bundle):
        return bundle.obj.relate_obj.id
```
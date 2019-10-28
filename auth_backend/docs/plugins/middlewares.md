# Middleware plugins

## AuthFailedExceptionMiddleware

`AuthFailedExceptionMiddleware` 是 auth backend 提供的 django 中间件，其负责在响应阶段捕获系统中抛出的 `AuthFailedException` 异常，并根据其中记录的缺失权限数据返回 [HttpResponseAuthFailed](http.md##HttpResponseAuthFailed) 响应。

## BackendProtector

`BackendProtector` 是 auth backend 提供的 django 中间件，当需要对 http 进行 server 端鉴权时，使用该中间件，根据如下描述编写规则即可：

中间件可以得到请求对象request，其中可得到`request.url`, `request.method` 和 `request.body`。
所以可以根据它们的特征，编写规则来判断是否要进行权限校验。
可编写多个规则，放入Rules列表中，每一个规则为一个字典，如该示例：

```python
{"url": "^/api/clouds/$",
 "method": "POST",
 "args": {"node_type": "Agent"},
 "permission": (Cloud, "create", None)
}
```

规则体现在url, method和args三个键上：
1. `url`: 为一个正则表达式，对request.url进行匹配。（对业务类的资源，当需求捕获url中的业务id时，可以使用类似(?P<biz_id>\d+)进行匹配并捕获）。
2. `method`: method进行比较
3. `args`参数：使用一个字典，
  -  为空表示不需要检查参数
  -  字典中的键是参数名称
  -  值的写法可以是以下三种方式之一：
      -  为一个值，要求该参数的值与此值相等。大多数情况下此方法即足够确定要鉴别的权限。
      - 为一个元组， 如``("in", ("gse", "timout"))``或 ``(">", 0)``
          1.  第一个元素表示规则，可以是 ``in``, ``>``, ``<`` 等。
          2.  第二个元素，是第一个元素的操作数
      - 一个python表达式的字符串，其中要检查的参数用 ``{}`` 替代。
通过以上三个键值对进行匹配，如果request满足该规则，则此请求需要进行权限校验。要校验的权限写在 `permission` 的值中：
4. `permission`: ``（Resource_type, Action_id, Instance）``
  - `Resource_type` 为使用 auth_backend 声明的 `Resource` 类
  - `Action_id` 为字符串格式的该 `Resource` 中的 `action_id` 属性
  - 当鉴别”不关联实例”的权限时，`Instance` 为 `None`
  - 与实例相关时，`Instance`为需要鉴权的 `Instance`，编写规则与 auth backend 约定规则相同。
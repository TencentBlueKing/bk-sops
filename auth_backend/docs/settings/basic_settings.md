# 基本配置

## BK_IAM_SYSTEM_ID

系统注册到权限中心的系统名。

示例：

```python
BK_IAM_SYSTEM_ID = 'bk_sops'
```

## BK_IAM_SYSTEM_NAME 

系统注册到权限中心的系统名。

示例：

```python
BK_IAM_SYSTEM_NAME = u"标准运维"
```

## BK_IAM_SYSTEM_DESC

系统注册到权限中心的系统描述。

示例：

```python
BK_IAM_SYSTEM_DESC = u"一个神奇的系统"
```

## BK_IAM_QUERY_INTERFACE

权限中心获取资源接口，目前填空即可。


## BK_IAM_RELATED_SCOPE_TYPES

系统关联的作用域类型，多个作用域用 ; 分隔。

示例：

```python
BK_IAM_RELATED_SCOPE_TYPES = 'system'
```

## BK_IAM_SYSTEM_MANAGERS

系统管理员，多个管理员用 ; 分隔。

示例：

```python
BK_IAM_SYSTEM_MANAGERS = 'admin'
```

## BK_IAM_SYSTEM_CREATOR

系统创建者。

示例：

```python
BK_IAM_SYSTEM_CREATOR = 'admin'
```

## BK_IAM_HOST

权限中心的 HOST。

示例：

```python
BK_IAM_HOST = 'http://bkiamhost.consul'
```

## BK_IAM_APP_CODE

权限中心的 APP CODE。

示例：

```python
BK_IAM_BK_IAM_APP_CODEHOST = 'bk_iam_app'
```

## AUTH_BACKEND_CLS

使用的鉴权后端类。

示例：

```python
AUTH_BACKEND_CLS = 'auth_backend.backends.bkiam.BkIAMBackend'
```
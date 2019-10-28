# 权限模板相关配置

## BK_IAM_PERM_TEMPLATES

权限模板的声明路径。

示例：

```python
BK_IAM_PERM_TEMPLATES = 'config.perms.bk_iam_perm_templates'
```

## BK_IAM_SYNC_TEMPLATES

是否需要同步权限模板，该配置为 None 或 False 时不会向权限中心更新权限模板。

示例：

```python
BK_IAM_SYNC_TEMPLATES = True
```
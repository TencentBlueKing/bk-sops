## 1. Introduction

用于支持蓝鲸 SaaS 从 PAAS V2 平滑迁移到 PAAS V3 的应用，功能如下：

- 用户数据迁移
  - bkuser 数据迁移到 user
  - 数据库表外键引用修改
- python 库平滑升级
  - djcelery



## 2. Usage



1. 将 `data_migration` 目录放到工程下
2. 将 `data_migration` 添加到 `INSTALLED_APPS` 中

s
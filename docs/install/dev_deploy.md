# 开发环境后台部署

## 部署蓝鲸社区版
标准运维 SaaS 的登录鉴权依赖于蓝鲸智云PaaS平台，业务信息需要从蓝鲸智云配置平台提供的接口获取，所以你需要部署蓝鲸PaaS平台和蓝鲸配置平台，作为开发联调环境。

1）如果你只需要定制开发标准运维，不需要改动蓝鲸PaaS和蓝鲸配置平台的源码，建议你直接从官方下载蓝鲸智云社区版完整包进行。
- [下载网址](https://bk.tencent.com/download/)
- [部署指南](https://docs.bk.tencent.com/bkce_install_guide/)
- [产品论坛](https://bk.tencent.com/s-mart/community)
- QQ交流群:495299374

2）如果你希望使用蓝鲸所有开源产品，进行定制开发，你可以部署开源的蓝鲸智云PaaS平台和蓝鲸智云配置平台。
- [蓝鲸智云PaaS平台](https://github.com/Tencent/bk-PaaS)  
- [蓝鲸智云配置平台](https://github.com/Tencent/bk-cmdb)  

部署方法请参考各个开源产品的相关文档，在蓝鲸智云PaaS平台部署完成后，你还需要上传部署标准运维SaaS并开通应用免登录态验证白名单。
你可以[点击这里](https://github.com/Tencent/bk-sops/releases)下载标准运维Release版本，然后前往蓝鲸PaaS平台的"开发者中心"->"S-mart应用"上传部署新应用。
你可以参考蓝鲸PaaS平台的"开发者中心"->"API网关"->"使用指南"->"API调用说明"页面中"用户认证"文档，添加默认标准运维APP_ID即bk_sops到应用免登录态验证白名单。


## 准备本地 rabbitmq 资源  
在本地安装 rabbitmq，并启动 rabbitmq-server，服务监听的端口保持默认（5672）。


## 准备本地 redis 资源  
在本地安装 redis，并启动 redis-server，服务监听的端口保持默认（6379）。


## 准备本地 mysql  
在本地安装 mysql，并启动 mysql-server，服务监听的端口保持默认（3306）。


## 安装 python 和依赖库
在本地安装 python3.6.7 和 pip，通过 git 拉取源代码到工程目录后，并进入目录下运行 pip 命令安装 python 包。
```bash
pip install -r requirements.txt
```


## 环境配置及数据库准备

1)

在执行任何 django `manage.py` 命令时，需要保证环境中有以下环境变量

```
export APP_ID = "bk_sops"
export APP_TOKEN = "{你的标准运维应用 TOKEN}"
export BK_PAAS_HOST = "{开发环境 PAAS 域名}"
export RUN_VER = "open"
export DB_NAME = "{你的 DB 名}"
export BKAPP_PYINSTRUMENT_ENABLE = "1"
export BKAPP_BK_IAM_SYSTEM_ID="bk_sops"
export BKAPP_API_JWT_EXEMPT="1"
export BK_IAM_SKIP="True"
export BKAPP_IAM_SKIP="True"
```


2) 在项目根目录下添加本地配置 local_settings.py

```python
# -*- coding: utf-8 -*-
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': '',  # 本地数据库账号
        'PASSWORD': '',  # 本地数据库密码
        'HOST': 'localhost',
        'PORT': '3306',
        'TEST_CHARSET': "utf8",
        'TEST_COLLATION': "utf8_general_ci",
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    },
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT = False
BK_IAM_SYNC_TEMPLATES = False

STATIC_ROOT = 'staticfiles'
```


## 创建并初始化数据库  

1) 在 mysql 中创建名为 bk_sops 的数据库
```sql
CREATE DATABASE `bk_sops` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

2) 在工程目录下执行以下命令初始化数据库
```bash
python manage.py migrate
python manage.py createcachetable django_cache
```


## 打包并收集前端静态资源

1）安装依赖包  
进入 frontend/desktop/，执行以下命令安装
```bash
npm install
```

2）本地打包
在 frontend/desktop/ 目录下，继续执行以下命令打包前端静态资源
```bash
npm run build
```

3）处理静态资源

回到项目根目录，执行以下命令

```bash
cp -r ./frontend/desktop/static ./staticfiles/bk_sops
rm ./gcloud/core/templates/core/base_vue.html
mv ./staticfiles/bk_sops/index.html ./gcloud/core/templates/core/base_vue.html
```

## 配置本地 hosts  

windows: 在 C:\Windows\System32\drivers\etc\host 文件中添加“127.0.0.1 dev.{BK_PAAS_HOST}”。  
mac: 执行 “sudo vim /etc/hosts”，添加“127.0.0.1 dev.{BK_PAAS_HOST}”。


## 启动进程

第一次在本地搭建开发环境需要启动 celery worker 及 beat 同步业务，按照以下启动以下进程

```bash
python manage.py celery worker -l info -B
python manage.py runserver 8000
```


## 访问页面  

使用浏览器开发 http://dev.{BK_PAAS_HOST}:8000/ 访问应用。

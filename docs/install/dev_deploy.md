# 开发环境后台部署

## 准备本地 rabbitmq 资源  
在本地安装 rabbitmq，并启动 rabbitmq-server，服务监听的端口保持默认（5672）。


## 准备本地 redis 资源  
在本地安装 redis，并启动 redis-server，服务监听的端口保持默认（6379）。


## 准备本地 mysql  
在本地安装 mysql，并启动 mysql-server，服务监听的端口保持默认（3306）。


## 本地 python 包安装  
通过 git 拉取源代码到工程目录中，并进入目录下运行 
```bash
pip install -r requirements.txt
```


## 修改本地配置  

1) 修改 conf/default.py，设置APP_ID, APP_TOKEN, BK_PAAS_HOST  

```python
APP_ID = ''
APP_TOKEN = ''
BK_PAAS_HOST = ''
```
BK_PAAS_HOST 为你部署的蓝鲸社区版域名（需要加上 http 前缀；如果是 https 域名，请改为 https 前缀）。APP_ID 设置为你的社区版标准运维应用ID，默认设置为 bk_sops。APP_TOKEN 设置为你的社区版标准运维应用 TOKEN，默认可以访问 http://{BK_PAAS_HOST}/admin/app/app/，找到名为"标准运维"的应用，查看详情获取 Token 字段值。

2) 修改 conf/settings_development.py，设置本地开发用的数据库信息以及 Redis 本地信息

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': APP_ID,       # 数据库名 (默认与APP_ID相同)
        'USER': 'root',       # 你的数据库user
        'PASSWORD': '',       # 你的数据库password
        'HOST': 'localhost',  # 数据库HOST
        'PORT': '3306',       # 默认3306
    },
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
}
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


## 配置本地 hosts  
windows: 在 C:\Windows\System32\drivers\etc\host 文件中添加“127.0.0.1 dev.{BK_PAAS_HOST}”。  
mac: 执行 “sudo vim /etc/hosts”，添加“127.0.0.1 dev.{BK_PAAS_HOST}”。


## 启动进程
```bash
python manage.py celery worker -l info
python manage.py runserver 8000
```


## 访问页面  
使用浏览器开发 http://dev.{BK_PAAS_HOST}:8000/ 访问应用。

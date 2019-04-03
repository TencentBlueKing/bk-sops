### Account 使用说明

blueapps.account 作为开发框架的登录模块，可解决内部版 OA 登录、外部版 ptlogin QQ 登录，自动跳转至 PASS 统一登录平台，完成登录认证，获取用户信息。

#### 申明 USER_MODEL

```
AUTH_USER_MODEL = 'account.User'
```

#### USER_MODEL 字段说明

* [a] username  
    用户唯一标识，在内部版为 RTX，在混合云为 QQ 号，在腾讯云为 openid
* [a] nickname
    用于前端展示的用户名，在内部版为 RTX，在混合云为 QQ 昵称，在腾讯云为 QQ 昵称
* [a] avatar_url
    用户头像 URL
* [m] get_full_name
    用于前端展示的完整用户名，在内部版为 rtx，在混合云为 昵称（QQ），腾讯云为 昵称


#### 添加统一登录中间件（WeixinLoginRequiredMiddleware 可选添加）

```
MIDDLEWARE = (
    # Auth middleware
    'blueapps.account.middlewares.WeixinLoginRequiredMiddleware',
    'blueapps.account.middlewares.LoginRequiredMiddleware',
)
```

#### 添加统一登录认证 Backend（WeixinBackend 可选添加）

```
AUTHENTICATION_BACKENDS = (
    'blueapps.account.backends.WeixinBackend',
    'blueapps.account.backends.UserBackend',
)
```


#### 目前所支持的平台&版本

|   | ieod（内部版）| clouds（混合云） | qcloud（腾讯云）|
| ------------ | ------------ |------------ | ------------ |
| PAAS   |     √        |       √         |       √       |
| WEIXIN |     √        |       ×         |       ×       |



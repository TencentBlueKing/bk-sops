# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

from django.conf import settings

# 是否开启使用
USE_WEIXIN = 'BKAPP_USE_WEIXIN' in os.environ
# 是否企业微信
IS_QY_WEIXIN = 'BKAPP_IS_QY_WEIXIN' in os.environ
# django 配置, 可使用自定义HOST
USE_X_FORWARDED_HOST = USE_WEIXIN
# 解决多级Nginx代理导致原始Host(`X-Forwarded-Host`)失效问题
X_FORWARDED_WEIXIN_HOST = 'HTTP_X_FORWARDED_WEIXIN_HOST'
# 微信公众号的app id和app secret 或企业微信的corpid和app_secret
WEIXIN_APP_ID = os.environ.get('BKAPP_WEIXIN_APP_ID', '')
WEIXIN_APP_SECRET = os.environ.get('BKAPP_WEIXIN_APP_SECRET', '')
# 该蓝鲸应用对外暴露的外网域名，即配置的微信能回调或访问的域名，如：test.bking.com
WEIXIN_APP_EXTERNAL_HOST = os.environ.get('BKAPP_WEIXIN_APP_EXTERNAL_HOST', '')
# 应用授权作用域
# snsapi_base （不弹出授权页面，直接跳转，只能获取用户openid），企业微信则只能选择snsapi_base
# snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
WEIXIN_SCOPE = 'snsapi_base'

# 蓝鲸微信请求URL前缀
WEIXIN_SITE_URL = '%sweixin/' % settings.SITE_URL
# 蓝鲸微信本地静态文件请求URL前缀
WEIXIN_STATIC_URL = '%sweixin/' % settings.STATIC_URL
# 蓝鲸微信登录的URL
WEIXIN_LOGIN_URL = '%sweixin/login/' % settings.SITE_URL

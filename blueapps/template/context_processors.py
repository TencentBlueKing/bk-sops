# coding=utf-8
from __future__ import absolute_import

import json
import logging
import datetime

from django.conf import settings

logger = logging.getLogger('blueapps')


def blue_settings(request):
    try:
        if request.user.is_anonymous:
            username = ''
            nickname = ''
            avatar_url = ''
        else:
            username = request.user.username
            nickname = request.user.nickname
            avatar_url = request.user.avatar_url

        context = {
            # 本地静态文件访问
            'STATIC_URL': settings.STATIC_URL,
            # 当前页面，主要为了login_required做跳转用
            'APP_PATH': request.get_full_path(),
            # 运行模式
            'RUN_MODE': settings.RUN_MODE,
            # 运行版本（内部版、混合云版...）
            'RUN_VER': settings.RUN_VER,
            # 在蓝鲸系统中注册的  "应用编码"
            'APP_CODE': settings.APP_CODE,
            # URL前缀
            'SITE_URL': settings.SITE_URL,
            # 远程静态资源url
            'REMOTE_STATIC_URL': settings.REMOTE_STATIC_URL,
            # 静态资源版本号,用于指示浏览器更新缓存
            'STATIC_VERSION': settings.STATIC_VERSION,
            # 蓝鲸平台URL
            'BK_URL': settings.BK_URL,
            # 蓝鲸开发者页面
            'BK_DEV_URL': settings.BK_DEV_URL,
            # 用户名
            'USERNAME': username,
            # 用户昵称
            'NICKNAME': nickname,
            # 用户头像
            'AVATAR_URL': avatar_url,
            # WEIXIN ROOT URL
            'WEIXIN_SITE_URL': settings.WEIXIN_SITE_URL,
            # WEIXIN 本地静态资源链接
            'WEIXIN_STATIC_URL': settings.WEIXIN_STATIC_URL,
            # WEIXIN 远程静态资源链接
            'WEIXIN_REMOTE_STATIC_URL': settings.WEIXIN_REMOTE_STATIC_URL,
            # 是否调试模式
            'DEBUG': json.dumps(settings.DEBUG),
            # 当前时间
            'NOW': datetime.datetime.now(),
            # 前后端联合开发的静态资源路径, 这个变量可选配置
            'BK_STATIC_URL': getattr(settings, 'BK_STATIC_URL', ''),
        }
    except Exception:
        logger.exception(u"自定义模板上下文异常")
        raise
    return context

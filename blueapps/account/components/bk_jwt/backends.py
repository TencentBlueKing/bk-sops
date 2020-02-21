# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import ugettext_lazy as _
from blueapps.account import get_user_model

bkoauth_jwt_client_exists = True
try:
    from bkoauth.jwt_client import JWTClient
except ImportError:
    bkoauth_jwt_client_exists = False

logger = logging.getLogger('component')


class BkJwtBackend(ModelBackend):

    def authenticate(self, request=None):
        logger.debug(u"进入 BK_JWT 认证 Backend")

        try:
            verify_data = self.verify_bk_jwt_request(request)
        except Exception as e:
            logger.exception(u"[BK_JWT]校验异常: %s" % e)
            return None

        if not verify_data['result'] or not verify_data['data']:
            logger.error(u"BK_JWT 验证失败： %s" % (
                verify_data)
            )
            return None

        user_info = verify_data['data']['user']
        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(
                username=user_info['bk_username'])
            user.nickname = user_info['bk_username']
            user.save()
        except Exception as e:
            logger.exception(u"自动创建 & 更新 User Model 失败: %s" % e)
            return None

        return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

    @staticmethod
    def verify_bk_jwt_request(request):
        """
        验证 BK_JWT 请求
        @param {string} x_bkapi_jwt JWT请求头
        @return {dict}
            {
                'result': True,
                'message': '',
                'data': {
                    'user': {
                        'bk_username': '调用方用户'
                    },
                    'app': {
                        'bk_app_code': '调用方app'
                    }
                }
            }
        """
        ret = {
            'result': False,
            'message': '',
            'data': {}
        }
        # 兼容bkoauth未支持jwt协议情况
        if not bkoauth_jwt_client_exists:
            ret['message'] = _(u'bkoauth暂不支持JWT协议')
            return ret

        jwt = JWTClient(request)
        if not jwt.is_valid:
            ret['message'] = _(u"jwt_invalid: %s") % jwt.error_message
            return ret

        # verify: user && app
        app = jwt.get_app_model()
        if not app['verified']:
            ret['message'] = app.get('valid_error_message', _(u'APP鉴权失败'))
            ret['data']['app'] = app
            return ret

        if not app.get('bk_app_code'):
            app['bk_app_code'] = app['app_code']

        user = jwt.get_user_model()
        # ESB默认需要校验用户信息
        use_esb_white_list = getattr(settings, 'USE_ESB_WHITE_LIST', True)

        if not use_esb_white_list and not user['verified']:
            ret['message'] = user.get('valid_error_message', _(u'用户鉴权失败且不支持ESB白名单'))
            ret['data']['user'] = user
            return ret
        if not user.get('bk_username'):
            user['bk_username'] = user['username']

        if not app['bk_app_code'] or not user['bk_username']:
            ret['message'] = _(u'用户或来源为空')
            return ret

        ret['result'] = True
        ret['data'] = {
            "user": user,
            "app": app
        }
        return ret

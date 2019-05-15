# -*- coding: utf-8 -*-
import abc

import requests

from common.log import logger
import settings as weixin_settings


class API(object):
    __metaclass__ = abc.ABCMeta
    timeout = 10
    ssl_verify = False

    def http_get(self, _http_url, **kwargs):
        """
        http 请求GET方法
        """
        try:
            resp = requests.get(_http_url, params=kwargs, timeout=self.timeout, verify=self.ssl_verify)
            resp = resp.json()
            return resp
        except Exception as error:
            logger.error('requests get url:%s error: %s' % (_http_url, error))
            return {}

    def http_post(self, _http_url, **kwargs):
        """
        http 请求POST方法
        """
        try:
            resp = requests.post(_http_url, json=kwargs, timeout=self.timeout, verify=self.ssl_verify)
            resp = resp.json()
            return resp
        except Exception as error:
            logger.error('requests post url:%s kwargs: %s error %s' % (_http_url, kwargs, error))
            return {}


class WeiXinApi(API):
    # 登录票据CODE验证URL
    WEIXIN_CHECK_CODE_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    # 获取微信信息API
    WEIXIN_GET_USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'

    def __init__(self):
        super(WeiXinApi, self).__init__()
        self.app_id = weixin_settings.WEIXIN_APP_ID
        self.secret = weixin_settings.WEIXIN_APP_SECRET

    def http_get(self, _http_url, **kwargs):
        data = super(WeiXinApi, self).http_get(_http_url, **kwargs)
        if 'errcode' in data:
            logger.error('weixin api (url: %s) return error: %s' % (_http_url, data))
            return {}
        return data

    def http_post(self, _http_url, **kwargs):
        data = super(WeiXinApi, self).http_post(_http_url, **kwargs)
        if 'errcode' in data:
            logger.error('weixin api (url: %s) return error: %s' % (_http_url, data))
            return {}
        return data

    def check_login_code(self, code):
        """
        校验登录回调code
        """
        query_param = {
            'appid': self.app_id,
            'secret': self.secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        data = self.http_get(self.WEIXIN_CHECK_CODE_URL, **query_param)
        access_token = data.get('access_token')
        openid = data.get('openid')
        if access_token is None or openid is None:
            logger.error(u"登录票据CODE接口返回无access_token或openid")
            return False, {}
        return True, {'access_token': access_token, 'openid': openid}

    def get_user_info(self, access_token, openid):
        """
        获取用户授权的用户信息
        """
        query_param = {
            'access_token': access_token,
            'openid': openid
        }
        data = self.http_get(self.WEIXIN_GET_USER_INFO_URL, **query_param)
        return data

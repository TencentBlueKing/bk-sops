# -*- coding: utf-8 -*-
"""
全平台 esb-sdk 封装，依赖于 esb-sdk 包，但不依赖 sdk 的版本。
sdk 中有封装好 cc.get_app_by_user 方法时，可直接按以前 sdk 的习惯调用

from blueapps.utils import client
client.cc.get_app_by_user()

from blueapps.utils import backend_client
b_client = backend_client(access_token="SfgcGlBHmPWttwlGd7nOLAbOP3TAOG")
b_client.cc.get_app_by_user()

当前版本 sdk 中未封装好，但 api 已经有 get_app_by_user 的时候。需要指定请求方法
client.cc.get_app_by_user.get()
"""

import collections

from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string

from blueapps.conf import settings
from blueapps.core.exceptions import AccessForbidden, MethodError
from blueapps.utils.request_provider import get_request

__all__ = [
    'client', 'backend_client', 'get_client_by_user', 'get_client_by_request', 'CustomComponentAPI'
]


# esb api的url path前缀
def get_api_prefix():
    platform_api_prefix_map = {
        # 内部版
        "ieod": "/component/compapi/",
        # 腾讯云
        "qcloud": "/c/qcloud/compapi/",
        # 混合云
        "clouds": "/c/clouds/compapi/",
        # tencet
        "tencent": "/c/ieg/compapi",
        # open
        "open": "/api/c/compapi/"
    }
    return platform_api_prefix_map[settings.RUN_VER]


ESB_API_PREFIX = get_api_prefix()

try:
    ESB_SDK_NAME = settings.ESB_SDK_NAME
    if not ESB_SDK_NAME:
        raise AttributeError
except AttributeError:
    ESB_SDK_NAME = 'blueking.component.{platform}'.format(
        platform=settings.RUN_VER)


class SDKClient(object):
    sdk_package = None

    @property
    def __version__(self):
        return self.sdk_package.__version__

    @property
    def __backend__(self):
        return self.sdk_package.__name__

    def __new__(cls, **kwargs):
        if cls.sdk_package is None:
            try:
                cls.sdk_package = __import__(ESB_SDK_NAME,
                                             fromlist=['shortcuts'])
            except ImportError as e:
                raise ImportError("%s is not installed: %s"
                                  % (ESB_SDK_NAME, e))
        return super(SDKClient, cls).__new__(cls)

    def __init__(self, **kwargs):
        self.mod_name = ""
        self.sdk_mod = None
        for ignored_field in ['app_code', 'app_secret']:
            if ignored_field in kwargs:
                kwargs.pop(ignored_field)
        self.common_args = kwargs

    def __getattr__(self, item):
        if not self.mod_name:
            ret = SDKClient(**self.common_args)
            ret.mod_name = item
            ret.setup_modules()
            if isinstance(ret.sdk_mod, collections.Callable):
                return ret.sdk_mod
            return ret
        else:
            # 真实sdk调用入口
            ret = getattr(self.sdk_mod, item, None)
            if ret is None:
                ret = ComponentAPICollection(self).add_api(item)
        if not isinstance(ret, collections.Callable):
            ret = self
        return ret

    def setup_modules(self):
        self.sdk_mod = getattr(self.sdk_client, self.mod_name, None)
        if self.sdk_mod is None:
            self.sdk_mod = ComponentAPICollection(self)

    @property
    def sdk_client(self):
        try:
            request = get_request()
            # 调用sdk方法获取sdk client
            return self.load_sdk_class(
                "shortcuts", "get_client_by_request")(request)
        except Exception:
            if settings.RUN_MODE != "DEVELOP":
                if self.common_args:
                    return self.load_sdk_class(
                        "client", "ComponentClient"
                    )(
                        app_code=settings.APP_CODE,
                        app_secret=settings.SECRET_KEY,
                        common_args=self.common_args
                    )
                else:
                    raise AccessForbidden(
                        "sdk can only be called through the Web request")
            else:
                # develop mode
                # 根据RUN_VER获得get_component_client_common_args函数
                get_component_client_common_args = import_string(
                    "blueapps.utils.sites.{platform}."
                    "get_component_client_common_args".format(
                        platform=settings.RUN_VER
                    )
                )
                return self.load_sdk_class(
                    "client", "ComponentClient"
                )(
                    app_code=settings.APP_CODE,
                    app_secret=settings.SECRET_KEY,
                    common_args=get_component_client_common_args()
                )

    def load_sdk_class(self, mod, attr_or_class):
        dotted_path = "%s.%s.%s" % (self.__backend__, mod, attr_or_class)
        return import_string(dotted_path)

    def patch_sdk_component_api_class(self):
        def patch_get_item(self, item):
            if item.startswith('__'):
                # make client can be pickled
                raise AttributeError()

            method = item.upper()
            if method not in self.allowed_methods:
                raise MethodError("esb api does not support method: %s" %
                                  method)
            self.method = method
            return self

        api_cls = self.load_sdk_class("base", "ComponentAPI")
        setattr(api_cls, "allowed_methods", CustomComponentAPI.allowed_methods)
        setattr(api_cls, "__getattr__", patch_get_item)


class ComponentAPICollection(object):
    mod_map = dict()

    def __new__(cls, sdk_client, *args, **kwargs):
        if sdk_client.mod_name not in cls.mod_map:
            cls.mod_map[sdk_client.mod_name] = super(
                ComponentAPICollection, cls).__new__(cls)
        return cls.mod_map[sdk_client.mod_name]

    def __init__(self, sdk_client):
        self.client = sdk_client

    def add_api(self, action):
        custom_api = CustomComponentAPI(self, action)
        setattr(self, action, custom_api)
        return custom_api

    def __getattr__(self, item):
        api = self.add_api(item)
        return api


class CustomComponentAPI(object):
    allowed_methods = ["GET", "POST"]

    def __init__(self, collection, action):
        self.collection = collection
        self.action = action

    def __getattr__(self, method):
        method = method.upper()
        if method not in self.allowed_methods:
            raise MethodError("esb api does not support method: %s" % method)
        api_cls = self.collection.client.load_sdk_class("base", "ComponentAPI")
        return api_cls(
            client=SDKClient(**self.collection.client.common_args),
            method=method,
            path='{api_prefix}{collection}/{action}/'.format(
                api_prefix=ESB_API_PREFIX,
                collection=self.collection.client.mod_name,
                action=self.action
            ),
            description='custom api(%s)' % self.action
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(
            'custom api `%s` must specify the request method' % self.action)


client = SDKClient()
backend_client = SDKClient
client.patch_sdk_component_api_class()


def get_client_by_user(user_or_username):
    user_model = get_user_model()
    if isinstance(user_or_username, user_model):
        username = user_or_username.username
    else:
        username = user_or_username
    get_client_by_user = import_string(
        ".".join([ESB_SDK_NAME, 'shortcuts', 'get_client_by_user']))
    return get_client_by_user(username)


def get_client_by_request(request=None):
    return client

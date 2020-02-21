# -*- coding: utf-8 -*-
from django.dispatch import Signal
from django.utils.deprecation import MiddlewareMixin

from blueapps.conf import settings
from blueapps.core.exceptions import AccessForbidden, ServerBlueException

# since each thread has its own greenlet we can just use those as identifiers
# for the context.  If greenlets are not available we fall back to the
# current thread ident depending on where it is.
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class AccessorSignal(Signal):
    allowed_receiver = 'blueapps.utils.request_provider.RequestProvider'

    def __init__(self, providing_args=None):
        Signal.__init__(self, providing_args)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        receiver_name = '.'.join(
            [receiver.__class__.__module__, receiver.__class__.__name__]
        )
        if receiver_name != self.allowed_receiver:
            raise AccessForbidden(
                u"%s is not allowed to connect" % receiver_name)
        Signal.connect(self, receiver, sender, weak, dispatch_uid)


request_accessor = AccessorSignal()


class RequestProvider(MiddlewareMixin):
    """
    @summary: request事件接收者
    """
    _instance = None

    def __new__(cls, get_response):
        if cls._instance is None:
            cls._instance = super(
                RequestProvider, cls).__new__(cls)
        return cls._instance

    def __init__(self, get_response):
        super(RequestProvider, self).__init__(get_response)
        self._request_pool = {}
        request_accessor.connect(self)

    def process_request(self, request):
        request.is_mobile = lambda: bool(settings.RE_MOBILE.search(
            request.META.get('HTTP_USER_AGENT', '')))

        # 是否为合法的RIO请求
        request.is_rio = lambda: bool(
            request.META.get('HTTP_STAFFNAME', '') and settings.RIO_TOKEN and
            settings.RE_WECHAT.search(request.META.get('HTTP_USER_AGENT', ''))
        )

        # 是否为合法 WEIXIN 请求，必须符合两个条件，wx 客户端 & WX PAAS 域名
        request_origin_url = "%s://%s" % (request.scheme, request.get_host())
        request.is_wechat = lambda: (
            bool(settings.RE_WECHAT.search(
                request.META.get('HTTP_USER_AGENT', ''))
            ) and request_origin_url == settings.WEIXIN_BK_URL and
            not request.is_rio()
        )

        # JWT请求
        request.is_bk_jwt = lambda: bool(request.META.get('HTTP_X_BKAPI_JWT', ''))

        self._request_pool[get_ident()] = request
        return None

    def process_response(self, request, response):
        assert request is self._request_pool.pop(get_ident())
        return response

    def __call__(self, *args, **kwargs):
        """
        1）接受 signal 请求响应，
        2）继承 MiddlewareMixin.__call__ 兼容 djagno 1.10 之前中间件
        """
        from_signal = kwargs.get('from_signal', False)
        if from_signal:
            return self.get_request(**kwargs)
        else:
            return super(RequestProvider, self).__call__(args[0])

    def get_request(self, **kwargs):
        sender = kwargs.get("sender")
        if sender is None:
            sender = get_ident()
        if sender not in self._request_pool:
            raise ServerBlueException(
                u"get_request can't be called in a new thread.")
        return self._request_pool[sender]


def get_request():
    return request_accessor.send(get_ident(), from_signal=True)[0][1]


def get_x_request_id():
    x_request_id = ''
    http_request = get_request()
    if hasattr(http_request, 'META'):
        meta = http_request.META
        x_request_id = (meta.get('HTTP_X_REQUEST_ID', '')
                        if isinstance(meta, dict) else '')
    return x_request_id

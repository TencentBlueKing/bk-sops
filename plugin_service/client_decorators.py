import functools
import logging

from . import env
from .conf import PLUGIN_CLIENT_LOGGER
from .utils import handle_plain_message

logger = logging.getLogger(PLUGIN_CLIENT_LOGGER)


def data_parser(func):
    """用于解析插件服务应用标准格式接口返回数据"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            message = f"plugin client request {func.__name__} error: {e}, with params: {args} and kwargs: {kwargs}."
            return False, {"message": message}
        if not result.get("result"):
            logger.error(f"{func.__name__} request error: {result.get('message')}")
            data = {"message": result.get("message")}
            if "trace_id" in result:
                data["trace_id"] = result["trace_id"]
            return False, data
        else:
            data = result.get("data")
            if "trace_id" in result and isinstance(data, dict):
                data["trace_id"] = result["trace_id"]
            return True, data

    return wrapper


def json_response_decoder(func):
    """用于处理json格式接口返回"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code != 200:
            inject_authorization = kwargs.get("inject_authorization") or {}
            for auth_item in inject_authorization:
                inject_authorization[auth_item] = "******"

            message = handle_plain_message(
                f"{func.__name__} gets error status code [{response.status_code}], "
                f"request with params: {args} and kwargs: {kwargs}. "
            )
            logger.error(message + f"response content: {response.content}")
            return {"result": False, "data": None, "message": message}
        return response.json()

    return wrapper


def check_use_plugin_service(func):
    """检查是否启用插件服务"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not env.USE_PLUGIN_SERVICE == "1":
            return {"result": False, "message": "插件服务未启用，请联系管理员进行配置", "data": None}
        return func(*args, **kwargs)

    return wrapper

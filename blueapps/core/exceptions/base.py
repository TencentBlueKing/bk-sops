# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging


class BlueException(Exception):

    ERROR_CODE = "0000000"
    MESSAGE = "APP异常"
    STATUS_CODE = 500
    LOG_LEVEL = logging.ERROR

    def __init__(self, message=None, data=None, *args):
        """
        :param message: 错误消息
        :param data: 其他数据
        :param context: 错误消息 format dict
        :param args: 其他参数
        """
        super(BlueException, self).__init__(*args)
        self.message = self.MESSAGE if message is None else message
        self.data = data

    def render_data(self):
        return self.data

    def response_data(self):
        return {
            "result": False,
            "code": self.ERROR_CODE,
            "message": self.message,
            "data": self.render_data()
        }


class ClientBlueException(BlueException):

    MESSAGE = "客户端请求异常"
    ERROR_CODE = "40000"
    STATUS_CODE = 400


class ServerBlueException(BlueException):

    MESSAGE = "服务端服务异常"
    ERROR_CODE = "50000"
    STATUS_CODE = 500


class ResourceNotFound(ClientBlueException):

    MESSAGE = "找不到请求的资源"
    ERROR_CODE = "40400"
    STATUS_CODE = 404


class ParamValidationError(ClientBlueException):

    MESSAGE = "参数验证失败"
    ERROR_CODE = "40000"
    STATUS_CODE = 400


class ParamRequired(ClientBlueException):

    MESSAGE = "关键参数缺失"
    ERROR_CODE = "40001"
    STATUS_CODE = 400


class AccessForbidden(ClientBlueException):

    MESSAGE = "登陆失败"
    ERROR_CODE = "40301"
    STATUS_CODE = 403


class RequestForbidden(ClientBlueException):

    MESSAGE = "请求拒绝"
    ERROR_CODE = "40320"
    STATUS_CODE = 403


class ResourceLock(ClientBlueException):

    MESSAGE = "请求资源被锁定"
    ERROR_CODE = "40330"
    STATUS_CODE = 403


class MethodError(ClientBlueException):

    MESSAGE = "请求方法不支持"
    ERROR_CODE = "40501"
    STATUS_CODE = 405


class RioVerifyError(ClientBlueException):

    MESSAGE = "登陆请求经智能网关检测失败"
    ERROR_CODE = "40502"
    STATUS_CODE = 405


class BkJwtVerifyError(ClientBlueException):

    MESSAGE = "登陆请求经JWT检测失败"
    ERROR_CODE = "40503"
    STATUS_CODE = 401


class DatabaseError(ServerBlueException):

    MESSAGE = "数据库异常"
    ERROR_CODE = "50110"


class ApiNetworkError(ServerBlueException):

    MESSAGE = "网络异常导致远程服务失效"
    ERROR_CODE = "50301"
    STATUS_CODE = 503


class ApiResultError(ServerBlueException):

    MESSAGE = "远程服务请求结果异常"
    ERROR_CODE = "50302"
    STATUS_CODE = 503


class ApiNotAcceptable(ServerBlueException):

    MESSAGE = "远程服务返回结果格式异常"
    ERROR_CODE = "50303"
    STATUS_CODE = 503

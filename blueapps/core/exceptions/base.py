# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import unicode_literals


class BlueException(Exception):

    MESSAGE = "app异常"
    ERROR_CODE = 500

    def __init__(self, message=None, error_code=None, *args):
        super(BlueException, self).__init__(*args)
        self.error_code = self.ERROR_CODE if error_code is None else error_code
        self.message = self.MESSAGE if message is None else message


class ClientBlueException(BlueException):

    MESSAGE = "客户端请求异常"
    ERROR_CODE = 40000


class ServerBlueException(BlueException):

    MESSAGE = "服务端服务异常"
    ERROR_CODE = 50000


class ResourceNotFound(ClientBlueException):

    MESSAGE = "找不到请求的资源"
    ERROR_CODE = 40400


class ParamValidationError(ClientBlueException):

    MESSAGE = "参数验证失败"
    ERROR_CODE = 40000


class ParamRequired(ClientBlueException):

    MESSAGE = "关键参数缺失"
    ERROR_CODE = 40001


class AccessForbidden(ClientBlueException):

    MESSAGE = "登陆失败"
    ERROR_CODE = 40301


class RequestForbidden(ClientBlueException):

    MESSAGE = "请求拒绝"
    ERROR_CODE = 40320


class ResourceLock(ClientBlueException):

    MESSAGE = "请求资源被锁定"
    ERROR_CODE = 40330


class MethodError(ClientBlueException):

    MESSAGE = "请求方法不支持"
    ERROR_CODE = 40501


class RioVerifyError(ClientBlueException):

    MESSAGE = "登陆请求经智能网关检测失败"
    ERROR_CODE = 40502


class DatabaseError(ServerBlueException):

    MESSAGE = "数据库异常"
    ERROR_CODE = 50110


class ApiNetworkError(ServerBlueException):

    MESSAGE = "网络异常导致远程服务失效"
    ERROR_CODE = 50301


class ApiResultError(ServerBlueException):

    MESSAGE = "远程服务请求结果异常"
    ERROR_CODE = 50302


class ApiNotAcceptable(ServerBlueException):

    MESSAGE = "远程服务返回结果格式异常"
    ERROR_CODE = 50303

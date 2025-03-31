# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # 获取当前环境支持的通知渠道类型列表
    v1_channels_list = bind_property(
        Operation,
        name="v1_channels_list",
        method="GET",
        path="/v1/channels/",
    )

    # 发送邮件
    v1_send_mail = bind_property(
        Operation,
        name="v1_send_mail",
        method="POST",
        path="/v1/send_mail/",
    )

    # 发送短信
    v1_send_sms = bind_property(
        Operation,
        name="v1_send_sms",
        method="POST",
        path="/v1/send_sms/",
    )

    # 发送语音
    v1_send_voice = bind_property(
        Operation,
        name="v1_send_voice",
        method="POST",
        path="/v1/send_voice/",
    )

    # 发送微信
    v1_send_weixin = bind_property(
        Operation,
        name="v1_send_weixin",
        method="POST",
        path="/v1/send_weixin/",
    )

    # 通用消息发送接口
    send_msg = bind_property(
        Operation,
        name="send_msg",
        method="POST",
        path="/v1/send_msg/",
    )


class Client(APIGatewayClient):
    """Bkapi bk-cmsi client"""

    _api_name = "bk-cmsi"

    api = bind_property(Group, name="api")

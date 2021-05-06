# -*- coding: utf-8 -*-


from django.test import TestCase
from mock import MagicMock

from pipeline.component_framework.test import (
    ComponentTestMixin,
    ComponentTestCase,
    ExecuteAssertion,
    ScheduleAssertion,
    Patcher,
)

from pipeline_plugins.components.collections.sites.ieod.fworks.client.package_send_mail.v1_0 import (
    ClientPackageSendMailComponent,
)


class ClientPackageSendMailComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [SEND_MSG_SUCCESS, SEND_MSG_ERROR, GET_NOTIFY_RECEIVERS_ERROR, SEND_MSG_ERROR_BY_JSON]

    def component_cls(self):
        return ClientPackageSendMailComponent


GET_CLIENT_BY_USER = (
    "pipeline_plugins.components.collections.sites.ieod.fworks.client.package_send_mail.v1_0.get_client_by_user"
)
GET_NOTIFY_RECEIVERS = (
    "pipeline_plugins.components.collections.sites.ieod.fworks.client.package_send_mail.v1_0.get_notify_receivers"
)


class MockClient(object):
    def __init__(self, send_msg_return=None):
        self.cmsi = MagicMock()
        self.cmsi.send_msg = MagicMock(return_value=send_msg_return)


# mock client
SEND_MSG_SUCCESS_RETURN_VALUE = MockClient(
    send_msg_return={
        "message": "邮件发送成功。",
        "code": 0,
        "data": None,
        "result": True,
        "request_id": "7911789df9a649e4bf26123212724b40",
    }
)
SEND_MSG_ERROR_RETURN_VALUE = MockClient(
    send_msg_return={
        "message": "邮件发送失败。",
        "code": 10000,
        "data": None,
        "result": False,
        "request_id": "7911789df9a649e4bf26123212724b40",
    }
)

GET_NOTIFY_RECEIVERS_SUCCESS_RETURN_VALUE = {"result": True, "message": "success", "data": "admin"}

GET_NOTIFY_RECEIVERS_ERROR_RETURN_VALUE = {"result": False, "message": "error", "data": ""}

# 任务创建成功
SEND_MSG_SUCCESS = ComponentTestCase(
    name="send msg success",
    inputs={
        "client_watcher": "admin",
        "client_notify_title": "这是一个测试标题",
        "client_notify_content": "{PACKAGE_FILE_LIST}",
        "client_file_content": '[{"filename":"D:\\\\home\\\\make_client\\\\setup\\\\'
        "hello\\\\package\\\\T\\\\patch\\\\world\\\\"
        'sign\\\\20201234\\\\1245.exe",'
        '"md5":"caf20502f3e75ef4196374ecdf514b11",'
        '"size":1080328}]',
        "client_cdn_download_link": "http://down.qq.com/d2/Autopatch/4.3.0.950/1245.exe",
        "_loop": 1,
    },
    parent_data={"executor": "admin", "biz_cc_id": "123"},
    execute_assertion=ExecuteAssertion(success=True, outputs={}),
    schedule_assertion=ScheduleAssertion(success=True, schedule_finished=True, outputs={}),
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_MSG_SUCCESS_RETURN_VALUE),
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS_RETURN_VALUE),
    ],
)

# 任务创建失败
SEND_MSG_ERROR = ComponentTestCase(
    name="send msg error",
    inputs={
        "client_watcher": "admin",
        "client_notify_title": "这是一个测试标题",
        "client_notify_content": "{PACKAGE_FILE_LIST}",
        "client_file_content": '[{"filename":"D:\\\\home\\\\make_client\\\\setup\\\\'
        "hello\\\\package\\\\T\\\\patch\\\\world\\\\"
        'sign\\\\20201234\\\\1245.exe",'
        '"md5":"caf20502f3e75ef4196374ecdf514b11",'
        '"size":1080328}]',
        "client_cdn_download_link": "http://down.qq.com/d2/Autopatch/4.3.0.950/1245.exe",
        "_loop": 1,
    },
    parent_data={"executor": "admin", "biz_cc_id": "123"},
    execute_assertion=ExecuteAssertion(
        success=False,
        outputs={
            "ex_data": '调用蓝鲸服务(BK)接口cmsi.send_msg返回失败, params={"receiver__username":"admin",'
            '"title":"\\u8fd9\\u662f\\u4e00\\u4e2a\\u6d4b\\u8bd5\\u6807\\u9898","content":"|pre||table '
            "class='table table-bordered'||thead||tr||th style='width: 40%; text-align: "
            "left;'|\\u6587\\u4ef6\\u540d|\\/th||th style='width:40%; text-align: "
            "left;'|\\u4e0b\\u8f7d\\u5730\\u5740|\\/th||th style='width:5%; text-align: "
            "left;'|\\u5927\\u5c0f|\\/th||th style='width:15%; text-align: "
            "left;'|MD5|\\/th||\\/tr||\\/thead| "
            "|tbody||tr||td|1245.exe|\\/td||td||a "
            "href='http:\\/\\/down.qq.com\\/d2\\/Autopatch\\/4.3.0.950\\/1245.exe"
            "'|http:\\/\\/down.qq.com\\/d2\\/Autopatch\\/4.3.0.950\\/1245.exe"
            "|\\/a||\\/td||td|1080328|\\/td||td|caf20502f3e75ef4196374ecdf514b11|\\/td||\\/tr||\\/tbody"
            '||\\/table|\\n\\n|\\/pre|","msg_type":"mail"}, error=邮件发送失败。, request_id=7911789df9a649e4bf2612'
            "3212724b40;"
        },
    ),
    schedule_assertion=ScheduleAssertion(
        success=False,
        schedule_finished=False,
        outputs={},
    ),
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_MSG_ERROR_RETURN_VALUE),
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_SUCCESS_RETURN_VALUE),
    ],
)

# 任务创建失败
GET_NOTIFY_RECEIVERS_ERROR = ComponentTestCase(
    name="get nodify success",
    inputs={
        "client_watcher": "admin",
        "client_notify_title": "这是一个测试标题",
        "client_notify_content": "{PACKAGE_FILE_LIST}",
        "client_file_content": '[{"filename":"D:\\\\home\\\\make_client\\\\setup\\\\'
        "hello\\\\package\\\\T\\\\patch\\\\world\\\\"
        'sign\\\\20201234\\\\1245.exe",'
        '"md5":"caf20502f3e75ef4196374ecdf514b11",'
        '"size":1080328}]',
        "client_cdn_download_link": "http://down.qq.com/d2/Autopatch/4.3.0.950/1245.exe",
        "_loop": 1,
    },
    parent_data={"executor": "admin", "biz_cc_id": "123"},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "error"}),
    schedule_assertion=ScheduleAssertion(
        success=False,
        schedule_finished=False,
        outputs={},
    ),
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_MSG_SUCCESS_RETURN_VALUE),
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_ERROR_RETURN_VALUE),
    ],
)

# 任务创建失败
SEND_MSG_ERROR_BY_JSON = ComponentTestCase(
    name="get nodify success",
    inputs={
        "client_watcher": "admin",
        "client_notify_title": "这是一个测试标题",
        "client_notify_content": "{PACKAGE_FILE_LIST}",
        "client_file_content": "f4196374ecdf514b11",
        "client_cdn_download_link": "http://down.qq.com/d2/Autopatch/4.3.0.950/1245.exe",
        "_loop": 1,
    },
    parent_data={"executor": "admin", "biz_cc_id": "123"},
    execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "发送失败，文件内容非json格式"}),
    schedule_assertion=ScheduleAssertion(
        success=False,
        schedule_finished=False,
        outputs={},
    ),
    # add patch
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=SEND_MSG_SUCCESS_RETURN_VALUE),
        Patcher(target=GET_NOTIFY_RECEIVERS, return_value=GET_NOTIFY_RECEIVERS_ERROR_RETURN_VALUE),
    ],
)

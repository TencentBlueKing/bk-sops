# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import mock
import contextlib
from mock import MagicMock

from gcloud import err_code
from gcloud.common_template.models import CommonTemplate
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "2"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "2"
TEST_TEMPLATE_ID = "2"
TEST_USERNAME = "tester"


class ModifyTemplateNotifyTmpAPITest(APITest):
    """
    modify_template_notify 接口单元测试
    覆盖场景：
      1. 正常修改接口数据（对齐 postman 示例请求/响应）
      2. receiver_group 传合法自定义组 ID 时成功
      3. notify_type / notify_receivers 顶层类型错误时受控失败（非 500）
      4. 更新后 editor/edit_time、signal 和审计链路符合现有模板更新语义
      5. 非法 JSON 请求体受控失败
    """

    def url(self):
        return "/apigw/modify_template_notify/{template_id}/{project_id}/"

    def setUp(self):
        super().setUp()

        # Mock ESB 客户端获取通知类型（覆盖 postman 用例中出现的全部类型）
        self.mock_esb_client = MagicMock()
        self.mock_esb_client.cmsi.get_msg_type.return_value = {
            "result": True,
            "data": [
                {"type": "weixin"},
                {"type": "mail"},
                {"type": "sms"},
                {"type": "voice"},
                {"type": "rtx"},
                {"type": "bkchat"},
            ],
        }
        self.mock_get_client_by_user = MagicMock(return_value=self.mock_esb_client)

        # Mock 自定义用户组 QuerySet（供 StaffGroupSet.objects.filter 返回）
        self.mock_staff_group_qs = MagicMock()
        self.mock_staff_group_qs.filter.return_value = self.mock_staff_group_qs

        # Mock StaffGroupSetSerializer 序列化后返回的 data（含两个自定义组 ID：100 / 101）
        self.mock_staff_group_serializer_data = [
            {"id": 100, "name": "自定义组1"},
            {"id": 101, "name": "自定义组2"},
        ]
        self.mock_staff_group_serializer = MagicMock()
        self.mock_staff_group_serializer.data = self.mock_staff_group_serializer_data

        # Mock TemplateManager.update_pipeline 返回值
        self.mock_update_pipeline_result = {"result": True, "message": "success"}

    # -------------------- 公共 patch 构造 --------------------
    def _common_patches(
        self,
        post_save=None,
        operate_record=None,
        audit=None,
        update_pipeline=None,
    ):
        """
        构造本类所有用例共享的 patcher 列表，供 ExitStack 统一进入/退出。
        将每个 mock.patch 独立成一行，避免 flake8 的 E123/E501 警告。
        """
        if update_pipeline is None:
            update_pipeline = MagicMock(return_value=self.mock_update_pipeline_result)
        view_module = "gcloud.apigw.views.modify_template_notify"
        tm_module = "gcloud.template_base.domains.template_manager.TemplateManager"
        patchers = [
            mock.patch(
                "{}.get_client_by_user".format(view_module),
                self.mock_get_client_by_user,
            ),
            mock.patch(
                "gcloud.core.models.StaffGroupSet.objects.filter",
                MagicMock(return_value=self.mock_staff_group_qs),
            ),
            mock.patch(
                "{}.StaffGroupSetSerializer".format(view_module),
                MagicMock(return_value=self.mock_staff_group_serializer),
            ),
            mock.patch(
                "{}.update_pipeline".format(tm_module),
                update_pipeline,
            ),
            mock.patch(
                "{}.post_template_save_commit.send".format(view_module),
                post_save if post_save is not None else MagicMock(),
            ),
            mock.patch(
                "{}.operate_record_signal.send".format(view_module),
                operate_record if operate_record is not None else MagicMock(),
            ),
            mock.patch(
                "{}.bk_audit_add_event".format(view_module),
                audit if audit is not None else MagicMock(),
            ),
        ]
        return patchers

    # -------------------- 通用辅助 --------------------
    def _build_project(self):
        return MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

    def _build_task_template(self, project, editor="old_editor", edit_time="2020-01-01 00:00:00"):
        template = MockTaskTemplate(
            id=TEST_TEMPLATE_ID,
            project=project,
            pipeline_template=MagicMock(),
        )
        # 视图中 post_template_save_commit 需要的字段
        template.project_id = TEST_PROJECT_ID
        template.is_deleted = False
        # 序列化器会读取/写入的字段
        template.notify_type = "{}"
        template.notify_receivers = "{}"
        template.editor = editor
        template.edit_time = edit_time
        template.save = MagicMock()
        return template

    def _build_common_template(self):
        template = MockCommonTemplate(
            id=TEST_TEMPLATE_ID,
            pipeline_template=MagicMock(),
        )
        template.is_deleted = False
        template.notify_type = "{}"
        template.notify_receivers = "{}"
        template.save = MagicMock()
        return template

    def _post(self, body, content_type="application/json"):
        """统一的 POST 发送入口"""
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        return self.client.post(
            path=self.url().format(
                template_id=TEST_TEMPLATE_ID,
                project_id=TEST_PROJECT_ID,
            ),
            data=body,
            content_type=content_type,
            HTTP_BK_USERNAME=TEST_USERNAME,
        )

    # -------------------- 1. 正常修改接口数据（对齐 postman 示例） --------------------
    def test_modify_template_notify__success_matches_postman_example(self):
        """
        正常修改接口数据：请求体与响应体对齐 postman 示例
        """
        proj = self._build_project()
        template = self._build_task_template(proj)

        notify_type = {
            "success": ["bkchat", "rtx"],
            "fail": ["weixin", "voice", "mail", "sms"],
        }
        notify_receivers = {
            "receiver_group": ["Maintainers", "Developer", 100, 101],
            "more_receiver": "",
            "extra_info": {
                "bkchat": {
                    "success": "111",
                    "fail": "334211122",
                }
            },
        }

        mock_post_save = MagicMock()
        mock_operate_record = MagicMock()
        mock_audit = MagicMock()

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch(PROJECT_GET, MagicMock(return_value=proj)))
            stack.enter_context(mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)))
            for patcher in self._common_patches(
                post_save=mock_post_save,
                operate_record=mock_operate_record,
                audit=mock_audit,
            ):
                stack.enter_context(patcher)
            response = self._post({
                "notify_type": notify_type,
                "notify_receivers": notify_receivers,
                "common": False,
            })

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(data["data"]["notify_type"], notify_type)
        self.assertEqual(data["data"]["notify_receivers"], notify_receivers)
        self.assertEqual(data["data"]["template_id"], int(TEST_TEMPLATE_ID))

        # 持久化字段被序列化为 JSON 字符串写回
        self.assertEqual(json.loads(template.notify_type), notify_type)
        self.assertEqual(json.loads(template.notify_receivers), notify_receivers)
        template.save.assert_called_once()

        # 对应 TaskTemplate 链路的信号/审计应被触发
        mock_post_save.assert_called_once()
        mock_operate_record.assert_called_once()
        mock_audit.assert_called_once()

    # -------------------- 2. receiver_group 传合法自定义组 ID 时成功 --------------------
    def test_modify_template_notify__receiver_group_with_custom_group_id_success(self):
        """
        receiver_group 同时包含内置组和自定义组 ID（100 / 101）应校验通过
        """
        proj = self._build_project()
        template = self._build_task_template(proj)

        notify_type = {"success": ["weixin"], "fail": ["mail"]}
        notify_receivers = {
            "receiver_group": ["Maintainers", 100, 101],
            "more_receiver": "",
        }

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch(PROJECT_GET, MagicMock(return_value=proj)))
            stack.enter_context(mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)))
            for patcher in self._common_patches():
                stack.enter_context(patcher)
            response = self._post({
                "notify_type": notify_type,
                "notify_receivers": notify_receivers,
                "common": False,
            })

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"]["notify_receivers"]["receiver_group"],
                         ["Maintainers", 100, 101])

    # # -------------------- 3. notify_type / notify_receivers 顶层类型错误受控失败 --------------------
    def test_modify_template_notify__notify_type_top_level_type_error_controlled_fail(self):
        """
        notify_type 传字符串（非字典）时应受控失败：
            - HTTP 200（JsonResponse 默认 200，不得 500）
            - result=False
            - code == REQUEST_PARAM_INVALID
            - message 提示 notify_type
        """
        proj = self._build_project()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            response = self._post({
                "notify_type": "invalid_string",  # 类型错误
                "notify_receivers": {},
                "common": False,
            })

        # 不得是 5xx
        self.assertLess(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("notify_type", data["message"])

    def test_modify_template_notify__notify_receivers_top_level_type_error_controlled_fail(self):
        """
        notify_receivers 传字符串（非字典）时应受控失败
        """
        proj = self._build_project()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            response = self._post({
                "notify_type": {},
                "notify_receivers": "invalid_string",  # 类型错误
                "common": False,
            })

        self.assertLess(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("notify_receivers", data["message"])

    # # -------------------- 4. editor/edit_time、signal 和审计链路与现有模板更新语义一致 --------------------
    def test_modify_template_notify__update_signals_and_audit_chain_consistent(self):
        """
        校验 TaskTemplate 更新链路：
            - update_pipeline 被调用（editor 即当前请求用户，推动 pipeline_template.editor/edit_time 的更新）
            - post_template_save_commit.send 被正确参数触发（sender=TaskTemplate）
            - operate_record_signal.send 被调用
            - bk_audit_add_event 被调用（FLOW_EDIT_ACTION / FLOW_RESOURCE）
            - instance.save 被调用
        """
        proj = self._build_project()
        template = self._build_task_template(proj)

        notify_type = {"success": ["weixin"]}
        notify_receivers = {"receiver_group": ["Maintainers"]}

        mock_post_save = MagicMock()
        mock_operate_record = MagicMock()
        mock_audit = MagicMock()
        mock_update_pipeline = MagicMock(return_value=self.mock_update_pipeline_result)

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch(PROJECT_GET, MagicMock(return_value=proj)))
            stack.enter_context(mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)))
            for patcher in self._common_patches(
                post_save=mock_post_save,
                operate_record=mock_operate_record,
                audit=mock_audit,
                update_pipeline=mock_update_pipeline,
            ):
                stack.enter_context(patcher)
            response = self._post({
                "notify_type": notify_type,
                "notify_receivers": notify_receivers,
                "common": False,
            })

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)

        # update_pipeline 以当前请求用户作为 editor 被调用（即 edit_time / editor 更新由其负责）
        self.assertEqual(mock_update_pipeline.call_count, 1)
        _, update_kwargs = mock_update_pipeline.call_args
        self.assertEqual(update_kwargs.get("editor"), TEST_USERNAME)
        self.assertIs(update_kwargs.get("pipeline_template"), template.pipeline_template)

        # instance.save() 被调用（触发模型持久化，edit_time 等由模型层保存）
        template.save.assert_called_once()

        # post_template_save_commit 以 TaskTemplate 作为 sender 被触发
        mock_post_save.assert_called_once()
        _, post_save_kwargs = mock_post_save.call_args
        self.assertEqual(post_save_kwargs.get("sender"), TaskTemplate)
        self.assertEqual(post_save_kwargs.get("project_id"), template.project_id)
        self.assertEqual(post_save_kwargs.get("template_id"), template.id)
        self.assertEqual(post_save_kwargs.get("is_deleted"), template.is_deleted)

        # 操作流水 signal 与审计事件各触发一次
        mock_operate_record.assert_called_once()
        _, op_kwargs = mock_operate_record.call_args
        self.assertEqual(op_kwargs.get("operator"), TEST_USERNAME)

        mock_audit.assert_called_once()
        _, audit_kwargs = mock_audit.call_args
        self.assertEqual(audit_kwargs.get("username"), TEST_USERNAME)
        self.assertIs(audit_kwargs.get("instance"), template)

    # # -------------------- 5. 非法 JSON 请求体受控失败 --------------------
    def test_modify_template_notify__invalid_json_body_controlled_fail(self):
        """
        非法 JSON 请求体：
            - 不得 500
            - result=False
            - code == REQUEST_PARAM_INVALID
            - message 提示 invalid param format
            这个直接走 @project_inject 这个装饰器的逻辑了
        """
        proj = self._build_project()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            response = self._post("not a valid json {{{")

        self.assertLess(response.status_code, 500)
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("invalid param format", data["message"])

    # # -------------------- 附加：公共模板链路（CommonTemplate 语义对齐） --------------------
    def test_modify_template_notify__common_template_success(self):
        """
        common=True 时，应走 CommonTemplate 链路：
            - post_template_save_commit.send 以 CommonTemplate 为 sender
            - 不包含 project_id
        """
        proj = self._build_project()
        template = self._build_common_template()

        notify_type = {"success": ["weixin"]}
        notify_receivers = {"receiver_group": ["Maintainers"]}

        mock_post_save = MagicMock()
        mock_operate_record = MagicMock()
        mock_audit = MagicMock()

        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch(PROJECT_GET, MagicMock(return_value=proj)))
            stack.enter_context(mock.patch(COMMONTEMPLATE_GET, MagicMock(return_value=template)))
            for patcher in self._common_patches(
                post_save=mock_post_save,
                operate_record=mock_operate_record,
                audit=mock_audit,
            ):
                stack.enter_context(patcher)
            response = self._post({
                "notify_type": notify_type,
                "notify_receivers": notify_receivers,
                "common": True,
            })

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)

        mock_post_save.assert_called_once()
        _, post_save_kwargs = mock_post_save.call_args
        self.assertEqual(post_save_kwargs.get("sender"), CommonTemplate)
        self.assertEqual(post_save_kwargs.get("template_id"), template.id)
        # CommonTemplate 链路不应携带 project_id
        self.assertNotIn("project_id", post_save_kwargs)

        mock_operate_record.assert_called_once()
        mock_audit.assert_called_once()

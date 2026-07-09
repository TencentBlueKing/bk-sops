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

import ujson as json

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"
TEST_TEMPLATE_ID = "3"
TEST_USERNAME = "tester"

VIEW_PATH = "gcloud.apigw.views.modify_template_executor_proxy"
MANAGER_PATH = VIEW_PATH + ".manager"
POST_SAVE_SIGNAL_PATH = VIEW_PATH + ".post_template_save_commit"
OPERATE_RECORD_SIGNAL_PATH = VIEW_PATH + ".operate_record_signal"
BK_AUDIT_ADD_EVENT_PATH = VIEW_PATH + ".bk_audit_add_event"
TRANSACTION_ATOMIC_PATH = VIEW_PATH + ".transaction.atomic"


def _build_mock_template(executor_proxy="old_proxy"):
    """构造一个带有所需字段的 MockTaskTemplate 实例。"""
    template = MockTaskTemplate(id=int(TEST_TEMPLATE_ID))
    # 补齐视图里会访问/赋值的字段
    template.project_id = int(TEST_PROJECT_ID)
    template.is_deleted = False
    template.executor_proxy = executor_proxy
    template.save = MagicMock()
    return template


class ModifyTemplateExecutorProxyAPITest(APITest):
    def url(self):
        return "/apigw/modify_template_executor_proxy/{template_id}/{project_id}/"

    # ------------------------------------------------------------------
    # 1. 正常请求
    # ------------------------------------------------------------------
    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_modify_template_executor_proxy__success(self):
        template = _build_mock_template(executor_proxy="old_proxy")

        with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)), \
                mock.patch(MANAGER_PATH) as mock_manager, \
                mock.patch(POST_SAVE_SIGNAL_PATH) as mock_post_save_signal, \
                mock.patch(OPERATE_RECORD_SIGNAL_PATH) as mock_operate_record_signal, \
                mock.patch(BK_AUDIT_ADD_EVENT_PATH) as mock_audit:
            mock_manager.update_pipeline.return_value = {"result": True, "data": None, "message": "success"}

            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"executor_proxy": TEST_USERNAME}),
                content_type="application/json",
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["data"]["template_id"], template.id)
        self.assertEqual(data["data"]["executor_proxy"], TEST_USERNAME)

        # 校验字段被正确写入 + 仅更新 executor_proxy 字段
        self.assertEqual(template.executor_proxy, TEST_USERNAME)
        template.save.assert_called_once_with(update_fields=["executor_proxy"])

        # update_pipeline 走正常链路
        mock_manager.update_pipeline.assert_called_once()
        _, update_kwargs = mock_manager.update_pipeline.call_args
        self.assertEqual(update_kwargs.get("pipeline_template"), template.pipeline_template)
        self.assertEqual(update_kwargs.get("editor"), TEST_USERNAME)

        # 信号与审计链路符合预期
        mock_post_save_signal.send.assert_called_once_with(
            sender=TaskTemplate,
            project_id=template.project_id,
            template_id=template.id,
            is_deleted=template.is_deleted,
        )
        mock_operate_record_signal.send.assert_called_once()
        _, operate_kwargs = mock_operate_record_signal.send.call_args
        self.assertEqual(operate_kwargs.get("operator"), TEST_USERNAME)
        self.assertEqual(operate_kwargs.get("instance_id"), template.id)
        self.assertEqual(operate_kwargs.get("project_id"), template.project_id)

        mock_audit.assert_called_once()
        _, audit_kwargs = mock_audit.call_args
        self.assertEqual(audit_kwargs.get("username"), TEST_USERNAME)
        self.assertEqual(audit_kwargs.get("instance"), template)

    # ------------------------------------------------------------------
    # 2. 缺少 executor_proxy 字段：必须返回失败且不清空原值
    # ------------------------------------------------------------------
    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_modify_template_executor_proxy__missing_field_should_not_clear(self):
        original_proxy = "original_owner"
        template = _build_mock_template(executor_proxy=original_proxy)

        with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)), \
                mock.patch(MANAGER_PATH) as mock_manager, \
                mock.patch(POST_SAVE_SIGNAL_PATH) as mock_post_save_signal, \
                mock.patch(OPERATE_RECORD_SIGNAL_PATH) as mock_operate_record_signal, \
                mock.patch(BK_AUDIT_ADD_EVENT_PATH) as mock_audit:
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({}),  # 不携带 executor_proxy 字段
                content_type="application/json",
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertIn("executor_proxy", data["message"])

        # 关键断言：原值不能被误清空，也不应触发任何更新 / 审计 / 信号
        self.assertEqual(template.executor_proxy, original_proxy)
        template.save.assert_not_called()
        mock_manager.update_pipeline.assert_not_called()
        mock_post_save_signal.send.assert_not_called()
        mock_operate_record_signal.send.assert_not_called()
        mock_audit.assert_not_called()

    # ------------------------------------------------------------------
    # 3. 非法值（null / [] / false）：返回 4xx 业务失败，不得 500
    # ------------------------------------------------------------------
    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_modify_template_executor_proxy__invalid_value_types(self):
        illegal_payloads = [
            {"executor_proxy": None},
            {"executor_proxy": []},
            {"executor_proxy": False},
        ]

        for payload in illegal_payloads:
            template = _build_mock_template(executor_proxy="original_owner")

            with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)), \
                    mock.patch(MANAGER_PATH) as mock_manager, \
                    mock.patch(POST_SAVE_SIGNAL_PATH) as mock_post_save_signal, \
                    mock.patch(OPERATE_RECORD_SIGNAL_PATH) as mock_operate_record_signal, \
                    mock.patch(BK_AUDIT_ADD_EVENT_PATH) as mock_audit:
                response = self.client.post(
                    path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps(payload),
                    content_type="application/json",
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

            # 明确不能是 500
            self.assertLess(response.status_code, 500, msg=f"payload={payload} got 5xx")
            data = json.loads(response.content)
            self.assertFalse(data["result"], msg=f"payload={payload} unexpectedly succeeded: {data}")
            # 未被写入、未触发任何 side effect
            self.assertEqual(template.executor_proxy, "original_owner")
            template.save.assert_not_called()
            mock_manager.update_pipeline.assert_not_called()
            mock_post_save_signal.send.assert_not_called()
            mock_operate_record_signal.send.assert_not_called()
            mock_audit.assert_not_called()

    # ------------------------------------------------------------------
    # 4. 成功路径下 editor / 审计 / 操作记录 链路细节
    # ------------------------------------------------------------------
    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_modify_template_executor_proxy__editor_and_side_effects(self):
        template = _build_mock_template(executor_proxy="")
        old_edit_time = template.pipeline_template.edit_time
        old_editor = template.pipeline_template.editor

        # 模拟 update_pipeline 真实副作用：更新 pipeline_template 的 editor/edit_time
        def _update_pipeline_side_effect(pipeline_template, editor, **kwargs):
            pipeline_template.editor = editor
            pipeline_template.edit_time = "new_edit_time"
            return {"result": True, "data": pipeline_template, "message": "success"}

        with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)), \
                mock.patch(MANAGER_PATH) as mock_manager, \
                mock.patch(POST_SAVE_SIGNAL_PATH) as mock_post_save_signal, \
                mock.patch(OPERATE_RECORD_SIGNAL_PATH) as mock_operate_record_signal, \
                mock.patch(BK_AUDIT_ADD_EVENT_PATH) as mock_audit:
            mock_manager.update_pipeline.side_effect = _update_pipeline_side_effect

            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"executor_proxy": TEST_USERNAME}),
                content_type="application/json",
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)

        # editor / edit_time 应被更新
        self.assertEqual(template.pipeline_template.editor, TEST_USERNAME)
        self.assertNotEqual(template.pipeline_template.editor, old_editor)
        self.assertEqual(template.pipeline_template.edit_time, "new_edit_time")
        self.assertNotEqual(template.pipeline_template.edit_time, old_edit_time)

        # 审计事件：动作 / 资源 与视图中传参保持一致
        from gcloud.iam_auth import IAMMeta

        mock_audit.assert_called_once()
        _, audit_kwargs = mock_audit.call_args
        self.assertEqual(audit_kwargs.get("username"), TEST_USERNAME)
        self.assertEqual(audit_kwargs.get("action_id"), IAMMeta.FLOW_EDIT_ACTION)
        self.assertEqual(audit_kwargs.get("resource_id"), IAMMeta.FLOW_RESOURCE)
        self.assertEqual(audit_kwargs.get("instance"), template)

        # 操作流水：type / source / operator / instance_id / project_id
        from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType

        mock_operate_record_signal.send.assert_called_once()
        _, operate_kwargs = mock_operate_record_signal.send.call_args
        self.assertEqual(operate_kwargs.get("sender"), RecordType.template.name)
        self.assertEqual(operate_kwargs.get("operate_type"), OperateType.update.name)
        self.assertEqual(operate_kwargs.get("operate_source"), OperateSource.api.name)
        self.assertEqual(operate_kwargs.get("operator"), TEST_USERNAME)
        self.assertEqual(operate_kwargs.get("instance_id"), template.id)
        self.assertEqual(operate_kwargs.get("project_id"), template.project_id)

        # 模板保存信号被触发
        mock_post_save_signal.send.assert_called_once()

    # ------------------------------------------------------------------
    # 5. 模板不存在时返回失败
    # ------------------------------------------------------------------
    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_modify_template_executor_proxy__template_does_not_exist(self):
        with mock.patch(TASKTEMPLATE_GET, MagicMock(side_effect=TaskTemplate.DoesNotExist)), \
                mock.patch(MANAGER_PATH) as mock_manager, \
                mock.patch(POST_SAVE_SIGNAL_PATH) as mock_post_save_signal, \
                mock.patch(OPERATE_RECORD_SIGNAL_PATH) as mock_operate_record_signal, \
                mock.patch(BK_AUDIT_ADD_EVENT_PATH) as mock_audit:
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"executor_proxy": TEST_USERNAME}),
                content_type="application/json",
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertIn("does not exist", data["message"])
        mock_manager.update_pipeline.assert_not_called()
        mock_post_save_signal.send.assert_not_called()
        mock_operate_record_signal.send.assert_not_called()
        mock_audit.assert_not_called()

    # ------------------------------------------------------------------
    # 6. 代理人非本人时 serializer 应拒绝
    # ------------------------------------------------------------------
    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID,
                name=TEST_PROJECT_NAME,
                bk_biz_id=TEST_BIZ_CC_ID,
                from_cmdb=True,
            )
        ),
    )
    def test_modify_template_executor_proxy__proxy_must_be_self(self):
        template = _build_mock_template(executor_proxy="original_owner")

        with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)), \
                mock.patch(MANAGER_PATH) as mock_manager:
            response = self.client.post(
                path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                data=json.dumps({"executor_proxy": "someone_else"}),
                content_type="application/json",
                HTTP_BK_USERNAME=TEST_USERNAME,
            )

        data = json.loads(response.content)
        self.assertFalse(data["result"], msg=data)
        self.assertIn("agent may only be designated", data["message"])
        template.save.assert_not_called()
        mock_manager.update_pipeline.assert_not_called()

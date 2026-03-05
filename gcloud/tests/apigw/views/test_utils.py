# -*- coding: utf-8 -*-
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Stub out Django ORM imports that utils.py requires at module level so that
# these tests can run without a fully configured Django environment.
for _mod in [
    "pipeline.variable_framework",
    "pipeline.variable_framework.models",
    "gcloud.tasktmpl3.domains",
    "gcloud.tasktmpl3.domains.varschema",
    "gcloud.tasktmpl3.domains.constants",
    "gcloud.template_base.utils",
    "gcloud.utils.dates",
    "pipeline_web.preview_base",
]:
    sys.modules.setdefault(_mod, MagicMock())

REPLACE_TEMPLATE_ID = "gcloud.apigw.views.utils.replace_template_id"


class ReplaceTemplateIdRecursiveTest(TestCase):
    def test_no_subprocess_activities(self):
        """无子流程时，只调用一次顶层 replace_template_id"""
        from gcloud.apigw.views.utils import replace_template_id_recursive

        template_model = MagicMock()
        pipeline_data = {
            "activities": {
                "node1": {"type": "ServiceActivity"},
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace:
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            mock_replace.assert_called_once_with(template_model, pipeline_data, reverse=True)

    def test_subprocess_without_pipeline_key(self):
        """SubProcess 节点没有 pipeline 字段时，不递归"""
        from gcloud.apigw.views.utils import replace_template_id_recursive

        template_model = MagicMock()
        pipeline_data = {
            "activities": {
                "node1": {"type": "SubProcess", "template_id": "123"},
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace:
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            mock_replace.assert_called_once_with(template_model, pipeline_data, reverse=True)

    def test_subprocess_with_pipeline_key_recursion(self):
        """SubProcess 有 pipeline 字段时，递归处理子流程"""
        from gcloud.apigw.views.utils import replace_template_id_recursive

        template_model = MagicMock()
        sub_pipeline = {"activities": {}}
        pipeline_data = {
            "activities": {
                "node1": {
                    "type": "SubProcess",
                    "template_source": "business",
                    "pipeline": sub_pipeline,
                },
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace:
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            assert mock_replace.call_count == 2
            mock_replace.assert_any_call(template_model, pipeline_data, reverse=True)
            mock_replace.assert_any_call(template_model, sub_pipeline, reverse=True)

    def test_common_subprocess_uses_common_template_model(self):
        """template_source=common 的子流程使用 CommonTemplate model"""
        from gcloud.apigw.views.utils import replace_template_id_recursive

        template_model = MagicMock()
        mock_common_model = MagicMock()
        sub_pipeline = {"activities": {}}
        pipeline_data = {
            "activities": {
                "node1": {
                    "type": "SubProcess",
                    "template_source": "common",
                    "pipeline": sub_pipeline,
                },
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace, patch(
            "gcloud.apigw.views.utils.apps.get_model", return_value=mock_common_model
        ):
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            mock_replace.assert_any_call(mock_common_model, sub_pipeline, reverse=True)

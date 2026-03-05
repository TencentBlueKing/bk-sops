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
    "pipeline_web.wrapper",
]:
    sys.modules.setdefault(_mod, MagicMock())

# patch() navigates via getattr; set the stub as an attribute on the real package
import pipeline_web as _pipeline_web  # noqa: E402

_pipeline_web.wrapper = sys.modules["pipeline_web.wrapper"]

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


FORMAT_TEMPLATE_DATA_UNFOLD = "pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess"
FORMAT_TEMPLATE_DATA_REPLACE_RECURSIVE = "gcloud.apigw.views.utils.replace_template_id_recursive"
FORMAT_TEMPLATE_DATA_REPLACE = "gcloud.apigw.views.utils.replace_template_id"


class FormatTemplateDataUnfoldSubprocessTest(TestCase):
    def _make_template(self, with_subprocess=False):
        """构造一个包含子流程活动的 mock template"""
        activities = {}
        if with_subprocess:
            activities["node_sub"] = {
                "type": "SubProcess",
                "template_id": "999",
                "template_source": "business",
            }
        pipeline_tree = {
            "line": [],
            "location": [],
            "activities": activities,
            "constants": {},
            "gateways": {},
            "flows": {},
            "start_event": {},
            "end_event": {},
        }
        mock_pt = MagicMock()
        mock_pt.name = "tmpl_name"
        mock_pt.creator = "admin"
        mock_pt.create_time = None
        mock_pt.editor = "admin"
        mock_pt.edit_time = None
        mock_pt.description = ""
        tmpl = MagicMock()
        tmpl.id = 1
        tmpl.category = "Other"
        tmpl.pipeline_template = mock_pt
        tmpl.pipeline_tree = pipeline_tree
        return tmpl, pipeline_tree

    def test_unfold_subprocess_false_does_not_call_unfold(self):
        """unfold_subprocess=False 时不调用 PipelineTemplateWebWrapper.unfold_subprocess"""
        from gcloud.apigw.views.utils import format_template_data

        tmpl, _ = self._make_template()
        with patch(FORMAT_TEMPLATE_DATA_UNFOLD) as mock_unfold, patch("gcloud.apigw.views.utils.varschema"):
            format_template_data(tmpl, unfold_subprocess=False)
            mock_unfold.assert_not_called()

    def test_unfold_subprocess_true_calls_unfold_and_recursive_replace(self):
        """unfold_subprocess=True 时调用 unfold 和 replace_template_id_recursive"""
        from gcloud.apigw.views.utils import format_template_data

        tmpl, pipeline_tree = self._make_template(with_subprocess=True)
        with patch(FORMAT_TEMPLATE_DATA_UNFOLD) as mock_unfold, patch(
            FORMAT_TEMPLATE_DATA_REPLACE
        ) as mock_replace, patch(FORMAT_TEMPLATE_DATA_REPLACE_RECURSIVE) as mock_replace_recursive, patch(
            "gcloud.apigw.views.utils.varschema"
        ):
            result = format_template_data(tmpl, unfold_subprocess=True)
            # replace_template_id 先调用（user-facing → internal UUID）
            mock_replace.assert_called_once_with(tmpl.__class__, pipeline_tree)
            # unfold_subprocess 调用
            mock_unfold.assert_called_once_with(pipeline_tree, tmpl.__class__)
            # replace_template_id_recursive 最后调用（internal UUID → user-facing）
            mock_replace_recursive.assert_called_once_with(tmpl.__class__, pipeline_tree, reverse=True)
            # line/location 已 pop
            assert "line" not in result["pipeline_tree"]
            assert "location" not in result["pipeline_tree"]

    def test_unfold_subprocess_true_exception_propagates(self):
        """unfold_subprocess 内部异常向上冒泡"""
        from pipeline.exceptions import PipelineException

        from gcloud.apigw.views.utils import format_template_data

        tmpl, _ = self._make_template(with_subprocess=True)
        with patch(FORMAT_TEMPLATE_DATA_UNFOLD, side_effect=PipelineException("recursion limit")), patch(
            FORMAT_TEMPLATE_DATA_REPLACE
        ), patch("gcloud.apigw.views.utils.varschema"):
            with self.assertRaises(PipelineException):
                format_template_data(tmpl, unfold_subprocess=True)

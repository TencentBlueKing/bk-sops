import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


review = load("ai_review")
report = load("ai_review_report")


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.meta = {
            "repo": "owner/repo",
            "number": 1,
            "head": "a" * 40,
            "merge_base": "b" * 40,
            "omitted": [],
            "previous": [],
            "history_note": "",
        }
        self.finding = {
            "path": "src/a file.py",
            "line": 3,
            "side": "LEFT",
            "priority": "P1",
            "title": "缺少校验",
            "body": "完整触发条件与调用链。",
        }

    def history(self, status):
        self.meta["previous"] = [
            {**self.finding, "id": "F-123456789abc", "reported_head": "c" * 40, "reported_base": "d" * 40}
        ]
        return {
            "id": "F-123456789abc",
            "status": status,
            "body": "原因" * 260 + "保留末尾证据",
            "evidence": None if status == "unknown" else {"path": "src/new.py", "line": 5, "quote": "x > 0"},
        }

    def test_open_and_unknown_history_are_visible_when_no_new_findings(self):
        for status in ("open", "unknown"):
            value = {"findings": [], "limitations": "外部服务尚未验证", "followups": [self.history(status)]}
            body = review.render_review(value, self.meta)
            self.assertIn("有 1 项问题需要处理或确认", body)
            self.assertIn("### 🚩 待处理问题", body)
            self.assertIn("保留末尾证据", body)
            self.assertNotIn("**✅ 本次未发现", body)
            self.assertIn("外部服务尚未验证", body)

    def test_resolved_disclosure_keeps_full_response_and_both_commit_links(self):
        body = review.render_followups({"followups": [self.history("resolved")]}, self.meta)
        self.assertTrue(body.startswith("<details>\n<summary>✅ 已修复（静态代码确认）"))
        self.assertIn("保留末尾证据", body)
        self.assertIn("/blob/" + "d" * 40 + "/src/a%20file.py#L3", body)
        self.assertIn("/blob/" + "a" * 40 + "/src/new.py#L5", body)
        self.assertIn("x &gt; 0", body)

    def test_resolved_summary_uses_literal_html_text_not_markdown_escapes(self):
        outcome = self.history("resolved")
        self.meta["previous"][0]["title"] = 'list_tasks <img src="bad"> @user'
        body = review.render_followups({"followups": [outcome]}, self.meta)
        self.assertIn("list_tasks &lt;img", body)
        self.assertNotIn("list\\_tasks", body)
        self.assertNotIn('<img src="bad">', body)
        self.assertNotIn("@user", body)

    def test_overview_counts_match_new_and_followup_outcomes(self):
        outcome = self.history("open")
        self.meta["previous"] *= 3
        self.meta["previous"] = [{**old, "id": f"F-{i:012x}"} for i, old in enumerate(self.meta["previous"])]
        followups = [
            {**outcome, "id": old["id"], "status": status}
            for old, status in zip(self.meta["previous"], ("open", "resolved", "unknown"))
        ]
        body = review.render_review({"findings": [self.finding], "followups": followups, "limitations": ""}, self.meta)
        self.assertIn("| **1** | **1** | **1** | **1** |", body)
        self.assertIn("有 3 项问题需要处理或确认", body)
        self.assertIn("/blob/" + "b" * 40 + "/src/a%20file.py#L3", body)

    def test_explicit_sections_are_escaped_and_unlabeled_body_is_preserved(self):
        original = "影响：金额异常 | @user\n第二行\n原因：<details>bad</details>\n修复建议：[link](https://bad.test)"
        body = review.render_explanation(original)
        self.assertIn("💥 影响", body)
        self.assertIn("🛠️ 修复", body)
        self.assertIn("\\| ＠user<br>第二行", body)
        self.assertNotIn("<details>bad", body)
        self.assertNotIn("[link]", body)
        fallback = "先验条件不可省略。\n\n这里是完整的旧版问题正文。"
        self.assertEqual(review.render_explanation(fallback), review.safe_text(fallback))

    def test_history_gap_stays_visible_even_with_zero_findings(self):
        self.meta["history_note"] = "历史记录已过期，不能确认旧问题已修复。"
        body = review.render_review({"findings": [], "followups": [], "limitations": ""}, self.meta)
        self.assertIn("### ⚠️ 历史复核边界\n\n历史记录", body)
        self.assertNotIn("全部通过", body)

    def test_timeout_and_invalid_outputs_report_fixed_codes_without_transcripts(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "source").mkdir()
            (work / "metadata.json").write_text(json.dumps({**self.meta, "anchors": {}}))
            (work / "diff.txt").write_text("diff")
            output = work / "output"
            for kind in ("timeout", "empty_output", "invalid_output", "client_exit"):

                def fail(*args, **kwargs):
                    if kind == "timeout":
                        raise subprocess.TimeoutExpired(["PRIVATE_TRANSCRIPT"], 900)
                    if kind == "invalid_output":
                        kwargs["stdout"].write("PRIVATE_TRANSCRIPT")
                    return subprocess.CompletedProcess([], 1 if kind == "client_exit" else 0)

                output.write_text("")
                with self.subTest(kind=kind), patch.dict(
                    os.environ,
                    {
                        "CODEBUDDY_API_KEY": "dummy-test-key",
                        "AI_REVIEW_MODEL": "test-model",
                        "GITHUB_OUTPUT": str(output),
                    },
                ), patch.object(review.subprocess, "run", side_effect=fail):
                    with self.assertRaises(ValueError) as caught:
                        review.run_review(work, "fake-codebuddy")
                    self.assertNotIn("PRIVATE_TRANSCRIPT", str(caught.exception))
                    self.assertEqual(output.read_text(), f"failure_reason={kind}\n")
                    self.assertFalse((work / "review.json").exists())

    def test_validate_reports_real_mixed_results_and_keeps_failure_exit(self):
        class Cases(unittest.TestCase):
            def test_pass(self):
                pass

            def test_fail(self):
                self.assertEqual(2, 1)

            def test_error(self):
                raise ValueError("example")

            @unittest.skip("example")
            def test_skip(self):
                pass

        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=report.Result).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Cases)
        )
        body, code = report.render(result, 0.1)
        self.assertEqual(code, 1)
        self.assertIn("| **1** | **1** | **1** | **1** |", body)
        self.assertIn("test_fail", body.replace("\\", ""))
        self.assertIn("2 != 1", body.replace("\\", ""))

    def test_subtest_failures_are_not_counted_as_passing_cases(self):
        class Cases(unittest.TestCase):
            def test_subtests(self):
                for value in (1, 2):
                    with self.subTest(value=value):
                        self.assertEqual(value, 0)

        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=report.Result).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Cases)
        )
        body, code = report.render(result, 1)
        self.assertEqual(code, 1)
        self.assertIn("| **0** | **2** | **0** | **0** |", body)

    def test_no_tests_and_interruption_never_report_success(self):
        empty = report.Result(io.StringIO(), True, 2)
        for result, interrupted in ((None, True), (empty, False)):
            body, code = report.render(result, 0, interrupted)
            self.assertEqual(code, 1)
            self.assertIn("自测未完成", body)
            self.assertNotIn("✅ 自测通过", body)

    def test_report_redacts_known_credentials_and_untrusted_markup(self):
        with patch.dict(os.environ, {"TEST_API_KEY": "sensitive-value"}):
            body = report.text("sensitive-value @user <img> [link](https://bad.test) Bearer abc123456")
        self.assertNotIn("sensitive-value", body)
        self.assertNotIn("abc123456", body)
        self.assertNotIn("@user", body)
        self.assertNotIn("<img>", body)

    def test_all_skipped_suite_has_no_effective_validation_result(self):
        class Cases(unittest.TestCase):
            @unittest.skip("unavailable")
            def test_skip(self):
                pass

        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=report.Result).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Cases)
        )
        body, code = report.render(result, 0)
        self.assertEqual(code, 1)
        self.assertIn("自测未完成", body)
        self.assertIn("| **0** | **0** | **0** | **1** |", body)

    def test_validate_cli_empty_suite_fails_and_writes_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            summary = work / "summary.md"
            completed = subprocess.run(
                [sys.executable, "-I", str(Path(report.__file__)), "--start-dir", directory, "--summary", str(summary)],
                capture_output=True,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("自测未完成", summary.read_text())

    def test_workflow_status_explains_failure_skip_and_publication(self):
        workflow = Path(__file__).parents[1] / "workflows/code_review.yml"
        if not workflow.exists():
            workflow = Path(__file__).with_name("code_review.yml")
        source = workflow.read_text().split("python3 -I - <<'PY'\n", 1)[1].rsplit("          PY", 1)[0]
        source = textwrap.dedent(source)
        common = {
            "EVENT_NAME": "pull_request_target",
            "IS_DRAFT": "false",
            "VALIDATE_RESULT": "skipped",
            "REVIEW_RESULT": "success",
            "PUBLISH_RESULT": "skipped",
            "INSTALLED": "true",
            "READY": "",
            "SKIP_REASON": "",
            "FAILURE_REASON": "",
            "INSTALLATION_RESULT": "success",
            "PREPARE_RESULT": "success",
            "INSTALL_RESULT": "skipped",
            "MODEL_RESULT": "skipped",
        }
        scenarios = [
            ({"EVENT_NAME": "pull_request"}, "本次运行审查工具自测"),
            ({"INSTALLED": "false"}, "当前目标分支尚未接入"),
            ({"SKIP_REASON": "permission"}, "没有仓库写权限"),
            ({"REVIEW_RESULT": "failure", "MODEL_RESULT": "failure", "FAILURE_REASON": "timeout"}, "900 秒"),
            ({"REVIEW_RESULT": "failure", "FAILURE_REASON": "unexpected"}, "具体原因尚未确认"),
            ({"READY": "true", "PUBLISH_RESULT": "failure"}, "尚未完成发布"),
            ({"READY": "true", "PUBLISH_RESULT": "success"}, "结果已发布"),
        ]
        for changes, expected in scenarios:
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory:
                summary = Path(directory) / "summary.md"
                env = {**os.environ, **common, **changes, "GITHUB_STEP_SUMMARY": str(summary)}
                subprocess.run([sys.executable, "-I", "-"], input=source, text=True, env=env, check=True)
                body = summary.read_text()
                self.assertIn(expected, body)
                self.assertIn("| :--- | :--- | :--- |\n| validate", body)

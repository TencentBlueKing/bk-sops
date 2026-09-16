"""Credential-free unittest entry point and GitHub Actions summary renderer."""

import argparse
import html
import io
import os
import re
import time
import unittest
from pathlib import Path


def redact(value):
    """Keep known credentials out of both step logs and report text."""
    for name, secret in os.environ.items():
        if len(secret) >= 8 and any(word in name.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")):
            value = value.replace(secret, "[REDACTED]")
    return re.sub(r"(?i)(bearer\s+)[\w./+=-]+", r"\1[REDACTED]", value)


def text(value):
    """Render diagnostic text without links, mentions, HTML or known credentials."""
    value = redact(value)
    return re.sub(r"([\\`*{}_\[\]()#+.!|>~-])", r"\\\1", html.escape(value).replace("@", "＠"))


class Result(unittest.TextTestResult):
    """Count successful test cases directly, including subtest outcomes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed += 1


def render(result, elapsed, interrupted=False):
    completed = result is not None and (result.passed or result.failures or result.errors or result.unexpectedSuccesses)
    valid = bool(completed and result.testsRun > 0 and not interrupted)
    success = valid and result.wasSuccessful()
    lines = ["## 🧪 审查工具自测", "⚙️ validate · 🔒 无模型凭据"]
    if not valid:
        lines += ["> [!WARNING]\n> **⛔ 自测未完成**\n>\n> 测试未启动、被中断或没有有效检查结果，不能按通过处理。"]
    elif success:
        lines += [f"> [!NOTE]\n> **✅ 自测通过**\n>\n> 已执行 {result.testsRun} 项测试，耗时 {elapsed:.1f} 秒。"]
    else:
        lines += ["> [!CAUTION]\n> **❌ 自测失败**\n>\n> 请修复失败项后重跑 validate。"]
    if result is not None:
        failures = len(result.failures) + len(result.unexpectedSuccesses)
        skipped = len(result.skipped) + len(result.expectedFailures)
        lines += [
            "| ✅ 通过用例 | ❌ 失败记录 | 💥 错误记录 | ⏭️ 跳过 / 预期失败 |\n"
            "| :---: | :---: | :---: | :---: |\n"
            f"| **{result.passed}** | **{failures}** | **{len(result.errors)}** | **{skipped}** |"
        ]
        if failures or result.errors:
            lines.append("### 🚩 失败项")
            records = [(case, detail, "失败") for case, detail in result.failures]
            records += [(case, detail, "错误") for case, detail in result.errors]
            records += [(case, "标记为预期失败的测试意外成功，请检查测试预期。", "预期不符") for case in result.unexpectedSuccesses]
            for case, detail, label in records[:20]:
                lines.append(f"#### ❌ {text(case.id())}\n\n**{label}**")
                # Keep full details in the step log; summaries have a bounded excerpt.
                excerpt = detail[-4000:]
                if len(detail) > len(excerpt):
                    excerpt = "（仅展示末尾诊断，完整信息见运行步骤）\n" + excerpt
                lines.append(
                    "<details>\n<summary>📋 脱敏诊断信息</summary>\n\n<pre>"
                    + html.escape(redact(excerpt)).replace("@", "＠")
                    + "</pre>\n\n</details>"
                )
            if len(records) > 20:
                lines.append(f"另有 {len(records) - 20} 条失败记录，请查看运行步骤。")
        if skipped:
            lines.append("⏭️ 跳过或预期失败的用例不计入通过数，明细见运行步骤。")
    lines += [
        "### 📋 验证范围\n\n| 检查内容 | 范围 |\n| :--- | :--- |\n"
        "| 审查执行器与报告工具 | 本任务自测 |\n"
        "| AI 代码审查 | 查看独立的 review 任务 |\n"
        "| 业务测试 | 本任务未执行 |",
        "---\n💡 工具自测通过 ≠ AI 审查通过 ≠ 业务测试通过。",
    ]
    return "\n\n".join(lines), 0 if success else 1


def run(start_dir, summary):
    started = time.monotonic()
    stream = io.StringIO()
    result = None
    interrupted = False
    try:
        suite = unittest.TestLoader().discover(str(start_dir), pattern="test_ai_review*.py")
        runner = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result)
        result = runner.run(suite)
    except (Exception, KeyboardInterrupt):
        interrupted = True
        # Do not copy arbitrary exception text from test discovery into the summary.
        stream.write("Test discovery or execution was interrupted; no successful result.\n")
    body, code = render(result, time.monotonic() - started, interrupted)
    print(redact(stream.getvalue()))
    if summary:
        with open(summary, "a", encoding="utf-8") as output:
            output.write(body + "\n")
    return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-dir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY"))
    args = parser.parse_args()
    raise SystemExit(run(args.start_dir.resolve(), args.summary))

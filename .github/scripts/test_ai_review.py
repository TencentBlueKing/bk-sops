import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("ai_review", Path(__file__).with_name("ai_review.py"))
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.anchors = {"src/app.py": {"LEFT": [3], "RIGHT": [3, 4]}}
        self.value = {
            "findings": [
                {
                    "path": "src/app.py",
                    "line": 3,
                    "side": "RIGHT",
                    "priority": "P1",
                    "title": "丢失租户过滤",
                    "body": "跨租户查询会返回其他租户数据。",
                }
            ],
            "limitations": "未执行测试",
        }

    def test_diff_anchors_exclude_context_and_handle_deleted_file(self):
        self.assertEqual(
            review.changed_lines("--- a/f\n+++ b/f\n@@ -2,3 +2,4 @@\n keep\n-old\n+new\n+extra\n keep"),
            {"LEFT": [3], "RIGHT": [3, 4]},
        )
        self.assertEqual(review.changed_lines("@@ -1,2 +0,0 @@\n-a\n-b\n"), {"LEFT": [1, 2], "RIGHT": []})

    def test_literal_git_paths_do_not_match_other_files(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                subprocess.run(["git", "init", "-q"], check=True)
                for name in ("[id].py", "i.py", ":(glob)**.py"):
                    Path(name).write_text("old\n")
                review.git("add", ".")
                review.git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "base")
                for name in ("[id].py", "i.py", ":(glob)**.py"):
                    Path(name).write_text("new\n")
                for name in ("[id].py", ":(glob)**.py"):
                    result = review.git("diff", "--", name).decode()
                    self.assertEqual(result.count("diff --git"), 1)
                    self.assertIn(name, result)
            finally:
                os.chdir(previous)

    def test_refuse_off_diff_paths_and_lines(self):
        for field, value in (
            ("path", "../../secret"),
            ("line", 2),
            ("line", True),
            ("priority", "P0"),
            ("side", "UNKNOWN"),
        ):
            candidate = json.loads(json.dumps(self.value))
            candidate["findings"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                review.validate_findings(candidate, self.anchors)

    def test_refuse_failed_truncated_or_malformed_model_responses(self):
        for response in (
            [],
            [{"type": "result", "subtype": "error_max_turns", "is_error": True}],
            [{"type": "result", "subtype": "success", "result": "not JSON"}],
            [{"type": "result", "subtype": "success", "structured_output": {"findings": []}}],
        ):
            with self.subTest(response=response), self.assertRaises(ValueError):
                review.parse_result(json.dumps(response), self.anchors)

    def test_parse_structured_and_plain_json_success(self):
        for key, value in (("structured_output", self.value), ("result", json.dumps(self.value))):
            response = [{"type": "result", "subtype": "success", "is_error": False, key: value}]
            self.assertEqual(review.parse_result(json.dumps(response), self.anchors), self.value)

    def test_output_tool_schema_constrains_exact_changed_locations(self):
        schema = json.loads(review.output_schema(self.anchors))
        locations = schema["properties"]["findings"]["items"]["allOf"][0]["oneOf"]
        self.assertEqual(locations[0]["properties"]["path"], {"const": "src/app.py"})
        self.assertEqual(locations[0]["properties"]["side"], {"const": "LEFT"})
        self.assertEqual(locations[0]["properties"]["line"], {"enum": [3]})
        self.assertEqual(locations[1]["properties"]["line"], {"enum": [3, 4]})
        self.assertEqual(json.loads(review.output_schema({}))["properties"]["findings"]["maxItems"], 0)

    def test_refuse_duplicates_and_large_output(self):
        self.value["findings"] *= 2
        with self.assertRaises(ValueError):
            review.validate_findings(self.value, self.anchors)
        self.value["findings"] = []
        self.value["limitations"] = "x" * 1601
        with self.assertRaises(ValueError):
            review.validate_findings(self.value, self.anchors)

    def test_model_process_has_no_github_credentials_or_external_tool_permissions(self):
        metadata = {"number": 1, "merge_base": "b", "head": "a", "omitted": [], "anchors": self.anchors}
        result = [{"type": "result", "subtype": "success", "structured_output": self.value}]
        inherited = {
            "PATH": "/usr/bin:/bin",
            "HOME": "/test-home",
            "CODEBUDDY_API_KEY": "test-model-key",
            "AI_REVIEW_MODEL": "example-review-model",
            "GH_TOKEN": "test-github-token",
            "GITHUB_TOKEN": "test-github-token",
            "GITHUB_ENV": "/runner/environment",
            "GITHUB_OUTPUT": "/runner/output",
            "GITHUB_PATH": "/runner/path",
            "GITHUB_STEP_SUMMARY": "/runner/summary",
            "CODEBUDDY_CONFIG_DIR": "/untrusted-config",
        }
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "source").mkdir()
            (work / "metadata.json").write_text(json.dumps(metadata))
            (work / "diff.txt").write_text("+changed line\n")

            def complete_review(*args, **kwargs):
                kwargs["stdout"].write(json.dumps(result))
                return subprocess.CompletedProcess([], 0)

            with patch.dict(os.environ, inherited, clear=True), patch.object(
                review.subprocess, "run", side_effect=complete_review
            ) as run:
                review.run_review(work, "codebuddy")
            command = run.call_args.args[0]
            options = run.call_args.kwargs
            self.assertEqual(command[command.index("--model") + 1], "example-review-model")
            self.assertEqual(options["cwd"], work / "source")
            self.assertEqual(
                options["env"],
                {
                    "PATH": inherited["PATH"],
                    "HOME": inherited["HOME"],
                    "CODEBUDDY_API_KEY": "test-model-key",
                    "CODEBUDDY_INTERNET_ENVIRONMENT": "iOA",
                    "CODEBUDDY_CONFIG_DIR": str(work / "config"),
                    "CI": "true",
                    "CLIENT_INFO_PRODUCT_VERSION": "2.147.0",
                },
            )
            self.assertEqual(command[command.index("--tools") + 1], "Read,Glob,Grep,StructuredOutput")
            # Bare Read/Glob/Grep in allowedTools would bypass the snapshot's default read boundary.
            self.assertEqual(command[command.index("--allowedTools") + 1], "StructuredOutput")
            self.assertEqual(command[command.index("--permission-mode") + 1], "dontAsk")
            self.assertEqual(command[command.index("--mcp-config") + 1], '{"mcpServers":{}}')
            self.assertIn("--strict-mcp-config", command)
            self.assertEqual(command[command.index("--setting-sources") + 1], "none")
            self.assertEqual(json.loads((work / "review.json").read_text()), self.value)

    def test_large_cli_json_survives_immediate_process_exit(self):
        metadata = {"number": 1, "merge_base": "b", "head": "a", "omitted": [], "anchors": self.anchors}
        # Reproduce a CLI that exits before pending asynchronous pipe writes drain.
        messages = [
            {"type": "assistant", "text": "x" * 1_048_576},
            {"type": "result", "subtype": "success", "structured_output": self.value},
        ]
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "source").mkdir()
            (work / "metadata.json").write_text(json.dumps(metadata))
            (work / "diff.txt").write_text("+changed line\n")
            executable = work / "fake-codebuddy"
            executable.write_text(
                "#!" + sys.executable + "\nimport os, sys\n"
                "sys.stdin.read()\nos.set_blocking(1, False)\n"
                "os.write(1, " + repr(json.dumps(messages).encode()) + ")\nos._exit(0)\n"
            )
            executable.chmod(0o700)
            with patch.dict(
                os.environ, {"CODEBUDDY_API_KEY": "test-model-key", "AI_REVIEW_MODEL": "example-review-model"}
            ):
                review.run_review(work, str(executable))
            self.assertEqual(json.loads((work / "review.json").read_text()), self.value)

    def test_model_configuration_is_required_and_invalid_values_never_start_cli(self):
        metadata = {"number": 1, "merge_base": "b", "head": "a", "omitted": [], "anchors": self.anchors}
        result = [{"type": "result", "subtype": "success", "structured_output": self.value}]
        for model in ("", "--unsafe-option", "model\nother", "x" * 129):
            with self.subTest(model=model), tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                (work / "source").mkdir()
                (work / "metadata.json").write_text(json.dumps(metadata))
                (work / "diff.txt").write_text("+changed line\n")

                def complete_review(*args, **kwargs):
                    kwargs["stdout"].write(json.dumps(result))
                    return subprocess.CompletedProcess([], 0)

                with patch.dict(
                    os.environ, {"CODEBUDDY_API_KEY": "test-model-key", "AI_REVIEW_MODEL": model}, clear=True
                ), patch.object(review.subprocess, "run", side_effect=complete_review) as run:
                    with self.assertRaisesRegex(ValueError, "AI_REVIEW_MODEL"):
                        review.run_review(work, "codebuddy")
                    run.assert_not_called()

    def test_review_title_is_independent_of_the_model(self):
        metadata = {"head": "a" * 40, "merge_base": "b" * 40, "repo": "owner/repo", "omitted": []}
        body = review.render_review(self.value, metadata)
        self.assertEqual(body.splitlines()[2], "### AI 代码审查 · `aaaaaaaaaaaa`")
        self.assertTrue(body.startswith("<!-- blueking-ai-review -->"))

    @contextmanager
    def snapshot_repository(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                subprocess.run(["git", "init", "-q"], check=True)
                yield Path(directory)
            finally:
                os.chdir(previous)

    def commit_snapshot(self):
        review.git("add", ".")
        review.git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "snapshot")

    def test_snapshot_uses_raw_blobs_despite_export_attributes(self):
        with self.snapshot_repository() as repository, tempfile.TemporaryDirectory() as directory:
            (repository / ".gitattributes").write_text("app.py export-ignore\nversion.py export-subst\n")
            (repository / "app.py").write_text("def authorization():\n    return False\n")
            (repository / "version.py").write_text('version = "$Format:%H$"\n')
            (repository / "nested").mkdir()
            (repository / "nested" / "tab\tand\nnewline.py").write_text("value = 1\n")
            self.commit_snapshot()
            destination = Path(directory)
            self.assertEqual(review.extract_snapshot("HEAD", destination), [])
            for path in ("app.py", "version.py", "nested/tab\tand\nnewline.py"):
                self.assertEqual((destination / path).read_bytes(), (repository / path).read_bytes())

    def test_snapshot_drops_links_and_agent_control_files(self):
        with self.snapshot_repository() as repository, tempfile.TemporaryDirectory() as directory:
            for name in ("a.py", ".codebuddy/settings.json", "sub/AGENTS.md"):
                path = repository / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("sample\n")
            (repository / "a.py").chmod(0o755)
            (repository / "link").symlink_to("/etc/passwd")
            (repository / "large.py").write_bytes(b"x" * 250_001)
            (repository / "limit.py").write_bytes(b"x" * 250_000)
            self.commit_snapshot()
            head = review.git("rev-parse", "HEAD").decode().strip()
            review.git("update-index", "--add", "--cacheinfo", "160000," + head + ",vendor")
            review.git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "submodule")
            omitted = review.extract_snapshot("HEAD", Path(directory))
            self.assertEqual((Path(directory) / "a.py").read_text(), "sample\n")
            self.assertEqual((Path(directory) / "limit.py").stat().st_size, 250_000)
            self.assertEqual(set(omitted), {"link", ".codebuddy/settings.json", "sub/AGENTS.md", "large.py", "vendor"})
            for name in omitted:
                self.assertFalse((Path(directory) / name).exists())
                self.assertFalse((Path(directory) / name).is_symlink())

    def test_snapshot_refuses_path_traversal(self):
        for name in ("../outside", "/absolute", "safe/../../outside", "."):
            tree = ("100644 blob " + "a" * 40 + " 1\t" + name + "\0").encode()
            with tempfile.TemporaryDirectory() as directory, patch.object(review, "git", return_value=tree):
                with self.subTest(path=name), self.assertRaisesRegex(ValueError, "Unsafe snapshot path"):
                    review.extract_snapshot("HEAD", Path(directory))

    def test_snapshot_refuses_nonempty_destination_with_external_symlink(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external:
            (Path(directory) / "linked").symlink_to(external, target_is_directory=True)
            with self.assertRaises(ValueError):
                review.extract_snapshot("HEAD", Path(directory))
            self.assertEqual(list(Path(external).iterdir()), [])

    def test_snapshot_total_limit_is_checked_before_fetching_blobs(self):
        tree = b"".join(("100644 blob " + "a" * 40 + " 250000\tfile%d.py\0" % i).encode() for i in range(241))
        with tempfile.TemporaryDirectory() as directory, patch.object(review, "git", return_value=tree):
            with patch.object(review.subprocess, "run") as fetch, self.assertRaisesRegex(ValueError, "60 MB"):
                review.extract_snapshot("HEAD", Path(directory))
            fetch.assert_not_called()

    def test_model_text_cannot_create_mentions_links_or_images(self):
        text = review.safe_text("@team ![x](https://evil.test) <img> <!--hidden-->")
        self.assertNotIn("@team", text)
        self.assertNotIn("![", text)
        self.assertNotIn("<img>", text)
        self.assertNotIn("<!--", text)

    def test_stale_or_closed_pr_is_not_current(self):
        expected = {"head": {"sha": "a"}, "base": {"sha": "b"}}
        live = {**expected, "state": "open", "draft": False}
        with patch.object(review, "api", return_value=live):
            self.assertTrue(review.current_pr("owner/repo", 1, expected))
            live["head"] = {"sha": "new"}
            self.assertFalse(review.current_pr("owner/repo", 1, expected))
            live["head"] = expected["head"]
            live["state"] = "closed"
            self.assertFalse(review.current_pr("owner/repo", 1, expected))

    def test_prepare_rejects_untrusted_author_or_sender_before_preparing_model_input(self):
        pr = {"user": {"login": "author"}, "author_association": "OWNER"}
        event = {"sender": {"login": "sender"}}
        for untrusted in ("author", "sender"):
            for permission in ("none", "read", "triage", "unexpected"):
                permissions = {"author": "admin", "sender": "admin", untrusted: permission}
                with self.subTest(
                    untrusted=untrusted, permission=permission
                ), tempfile.TemporaryDirectory() as directory:
                    work = Path(directory) / "review"
                    output = Path(directory) / "output"

                    def collaborator_permission(path):
                        login = path.split("/")[-2]
                        return {"permission": permissions[login]}

                    with patch.object(review, "event_context", return_value=(event, "owner/repo", pr, 1)), patch.object(
                        review, "api", side_effect=collaborator_permission
                    ), patch.object(review, "current_pr") as current, patch.object(review, "git") as git, patch.dict(
                        os.environ, {"GITHUB_OUTPUT": str(output)}
                    ):
                        review.prepare(work)
                    current.assert_not_called()
                    git.assert_not_called()
                    self.assertFalse(work.exists())
                    self.assertFalse(output.exists())

    def test_prepare_checks_both_current_permissions_before_checking_pr_state(self):
        pr = {"user": {"login": "author"}, "author_association": "NONE"}
        event = {"sender": {"login": "sender"}}
        for author_permission in ("write", "maintain", "admin"):
            for sender_permission in ("write", "maintain", "admin"):
                permissions = {"author": author_permission, "sender": sender_permission}
                with self.subTest(permissions=permissions), tempfile.TemporaryDirectory() as directory:
                    checked = set()

                    def collaborator_permission(path):
                        login = path.split("/")[-2]
                        checked.add(login)
                        return {"permission": permissions[login]}

                    def changed_pr(*args):
                        self.assertEqual(checked, {"author", "sender"})
                        return False

                    with patch.object(review, "event_context", return_value=(event, "owner/repo", pr, 1)), patch.object(
                        review, "api", side_effect=collaborator_permission
                    ), patch.object(review, "current_pr", side_effect=changed_pr) as current, patch.object(
                        review, "git"
                    ) as git:
                        review.prepare(Path(directory) / "review")
                    current.assert_called_once_with("owner/repo", 1, pr)
                    git.assert_not_called()

    def test_publish_updates_only_own_marker_and_checks_event(self):
        metadata = {
            "repo": "owner/repo",
            "number": 1,
            "head": "a",
            "base": "b",
            "merge_base": "b",
            "anchors": self.anchors,
            "omitted": [],
        }
        pr = {"head": {"sha": "a"}, "base": {"sha": "b"}}
        comments = [
            {"id": 10, "user": {"login": "human"}, "body": review.MARKER},
            {"id": 20, "user": {"login": "github-actions[bot]"}, "body": review.MARKER},
        ]
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "metadata.json").write_text(json.dumps(metadata))
            (work / "review.json").write_text(json.dumps(self.value))
            with patch.object(review, "event_context", return_value=({}, "owner/repo", pr, 1)), patch.object(
                review, "current_pr", return_value=True
            ), patch.object(review, "api", side_effect=[comments, {}]) as api:
                review.publish(work)
                self.assertEqual(api.call_args.args[:2], ("repos/owner/repo/issues/comments/20", "PATCH"))
            metadata["head"] = "different"
            (work / "metadata.json").write_text(json.dumps(metadata))
            with patch.object(review, "event_context", return_value=({}, "owner/repo", pr, 1)), patch.object(
                review, "api"
            ) as api, self.assertRaises(ValueError):
                review.publish(work)
            api.assert_not_called()

    def test_publish_migrates_legacy_comment_without_creating_a_duplicate(self):
        metadata = {
            "repo": "owner/repo",
            "number": 1,
            "head": "a",
            "base": "b",
            "merge_base": "b",
            "anchors": self.anchors,
            "omitted": [],
        }
        pr = {"head": {"sha": "a"}, "base": {"sha": "b"}}
        for marker in ("<!-- blueking-ai-review -->", "<!-- blueking-glm53-review -->"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                (work / "metadata.json").write_text(json.dumps(metadata))
                (work / "review.json").write_text(json.dumps(self.value))
                comments = [
                    {"id": 10, "user": {"login": "human"}, "body": marker},
                    {"id": 20, "user": {"login": "github-actions[bot]"}, "body": marker},
                ]
                with patch.object(review, "event_context", return_value=({}, "owner/repo", pr, 1)), patch.object(
                    review, "current_pr", return_value=True
                ), patch.object(review, "api", side_effect=[comments, {}]) as api:
                    review.publish(work)
                self.assertEqual(api.call_args.args[:2], ("repos/owner/repo/issues/comments/20", "PATCH"))
                self.assertTrue(api.call_args.args[2]["body"].startswith("<!-- blueking-ai-review -->"))


if __name__ == "__main__":
    unittest.main()

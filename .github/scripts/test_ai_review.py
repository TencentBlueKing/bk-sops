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
        env = patch.dict(os.environ, {"GITHUB_RUN_ID": "101", "GITHUB_RUN_ATTEMPT": "1"})
        env.start()
        self.addCleanup(env.stop)
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
            "followups": [],
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
        metadata = {"head": "a" * 40, "merge_base": "b" * 40, "repo": "owner/repo", "number": 1, "omitted": []}
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
            "head": "a" * 40,
            "base": "b" * 40,
            "base_ref": "main",
            "merge_base": "b" * 40,
            "anchors": self.anchors,
            "omitted": [],
        }
        pr = {"head": {"sha": "a" * 40}, "base": {"sha": "b" * 40, "ref": "main"}}
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
                review.stage_publication(work)
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
            "head": "a" * 40,
            "base": "b" * 40,
            "base_ref": "main",
            "merge_base": "b" * 40,
            "anchors": self.anchors,
            "omitted": [],
        }
        pr = {"head": {"sha": "a" * 40}, "base": {"sha": "b" * 40, "ref": "main"}}
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
                    review.stage_publication(work)
                    review.publish(work)
                self.assertEqual(api.call_args.args[:2], ("repos/owner/repo/issues/comments/20", "PATCH"))
                self.assertTrue(api.call_args.args[2]["body"].startswith("<!-- blueking-ai-review -->"))


class FollowupTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "id": "F-123456789abc",
            "path": "src/app.py",
            "line": 3,
            "side": "RIGHT",
            "priority": "P1",
            "title": "缺少租户过滤",
            "body": "必须限制当前租户。",
            "reported_head": "a" * 40,
            "reported_base": "b" * 40,
            "status": "open",
        }
        self.meta = {
            "repo": "owner/repo",
            "number": 1,
            "head": "c" * 40,
            "base": "b" * 40,
            "base_ref": "main",
            "merge_base": "b" * 40,
            "anchors": {},
            "omitted": [],
            "previous": [self.item],
            "history_note": "",
            "history_pointer": None,
            "source_lines": {"src/app.py": 4},
        }
        self.followup = {
            "id": self.item["id"],
            "status": "resolved",
            "body": "查询已按当前租户过滤。",
            "evidence": {"path": "src/app.py", "line": 3, "quote": "return rows.filter(tenant_id=tenant_id)"},
        }

    def test_each_previous_issue_requires_an_explicit_result(self):
        value = {"findings": [], "limitations": "", "followups": []}
        with self.assertRaisesRegex(ValueError, "previous"):
            review.validate_review(value, self.meta)

    def test_duplicate_unknown_or_missing_followup_ids_are_rejected(self):
        for items in ([self.followup, self.followup], [{**self.followup, "id": "F-000000000000"}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                review.validate_review({"findings": [], "limitations": "", "followups": items}, self.meta)

    def test_resolved_requires_matching_current_source_evidence(self):
        value = {"findings": [], "limitations": "", "followups": [self.followup]}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "src").mkdir()
            (source / "src/app.py").write_text("def f():\n    pass\nreturn rows.all()\n")
            with self.assertRaisesRegex(ValueError, "evidence"):
                review.validate_review(value, self.meta, source)
            (source / "src/app.py").write_text("def f():\n    pass\nreturn rows.filter(tenant_id=tenant_id)\n")
            self.assertEqual(review.validate_review(value, self.meta, source)["followups"][0]["status"], "resolved")
            for bad in (
                None,
                {"path": "../secret", "line": 1, "quote": "secret"},
                {"path": "src/app.py", "line": True, "quote": "x"},
            ):
                candidate = {**value, "followups": [{**self.followup, "evidence": bad}]}
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    review.validate_review(candidate, self.meta, source)

    def test_unknown_is_preserved_without_claiming_a_fix(self):
        value = {
            "findings": [],
            "limitations": "",
            "followups": [{**self.followup, "status": "unknown", "evidence": None}],
        }
        self.assertEqual(review.validate_review(value, self.meta)["followups"][0]["status"], "unknown")
        with patch.dict(os.environ, {"GITHUB_RUN_ID": "101", "GITHUB_RUN_ATTEMPT": "1"}):
            state = review.build_state(value, self.meta)
        self.assertEqual(state["items"][0]["id"], "F-123456789abc")
        self.assertEqual(state["items"][0]["status"], "unknown")
        body = review.render_followups(value, self.meta)
        self.assertIn("无法确认", body)
        self.assertNotIn("已修复", body)

    def test_followup_schema_cannot_omit_or_invent_previous_issues(self):
        schema = json.loads(review.output_schema({}, self.meta["previous"]))
        field = schema["properties"]["followups"]
        self.assertEqual(field["minItems"], 1)
        self.assertEqual(field["maxItems"], 1)
        self.assertEqual(field["items"]["properties"]["id"], {"enum": ["F-123456789abc"]})

    def test_zip_history_rejects_extra_files_traversal_and_large_members(self):
        import io
        import zipfile

        for members in ({"../state.json": "{}"}, {"state.json": "{}", "extra": "x"}, {"state.json": "x" * 300001}):
            payload = io.BytesIO()
            with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, content in members.items():
                    archive.writestr(name, content)
            with self.subTest(members=list(members)), self.assertRaises(ValueError):
                review.decode_history(payload.getvalue())

    def test_foreign_workflow_and_pull_request_artifacts_are_rejected(self):
        run = {
            "id": 101,
            "run_attempt": 1,
            "workflow_id": 9,
            "path": ".github/workflows/code_review.yml",
            "event": "pull_request_target",
            "status": "completed",
            "conclusion": "success",
            "repository": {"full_name": "owner/repo"},
        }
        for field, bad in (
            ("workflow_id", 10),
            ("event", "pull_request"),
            ("path", ".github/workflows/evil.yml"),
            ("repository", {"full_name": "other/repo"}),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                review.validate_history_run({**run, field: bad}, "owner/repo", {"run_id": 101, "run_attempt": 1}, 9)
        self.assertTrue(review.validate_history_run(run, "owner/repo", {"run_id": 101, "run_attempt": 1}, 9))
        self.assertFalse(
            review.validate_history_run(
                {**run, "conclusion": "cancelled"}, "owner/repo", {"run_id": 101, "run_attempt": 1}, 9
            )
        )

    def test_history_state_cannot_move_to_another_pr_or_target(self):
        with patch.dict(os.environ, {"GITHUB_RUN_ID": "101", "GITHUB_RUN_ATTEMPT": "1"}):
            state = review.build_state({"findings": [], "limitations": "", "followups": [self.followup]}, self.meta)
        pointer = {"run_id": 101, "run_attempt": 1}
        for field, bad in (("number", 2), ("repo", "owner/other"), ("base_ref", "other"), ("run_attempt", 2)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                review.validate_state({**state, field: bad}, "owner/repo", 1, "main", pointer)
        self.assertEqual(
            review.validate_state(state, "owner/repo", 1, "main", pointer)["items"][0]["id"], "F-123456789abc"
        )

    def test_three_round_publication_preserves_ids_and_replies_once_per_commit(self):
        """A disappeared finding is unknown, not resolved; re-runs update the same reply."""
        import io
        import zipfile

        comments, states, runs, artifacts = [], {}, {}, {}
        live = {"state": "open", "draft": False}
        writes = []

        def transport(path, method="GET", data=None):
            if path == "repos/owner/repo/pulls/1":
                return live
            if path.startswith("repos/owner/repo/issues/1/comments") and method == "GET":
                return comments
            if path == "repos/owner/repo/issues/1/comments" and method == "POST":
                comment = {"id": len(comments) + 20, "user": {"login": "github-actions[bot]"}, "body": data["body"]}
                comments.append(comment)
                writes.append((method, path))
                return comment
            if path.startswith("repos/owner/repo/issues/comments/") and method == "PATCH":
                comment = next(c for c in comments if c["id"] == int(path.rsplit("/", 1)[1]))
                comment.update(data)
                writes.append((method, path))
                return comment
            if path == "repos/owner/repo/actions/workflows/code_review.yml":
                return {"id": 9}
            match = review.re.fullmatch(r"repos/owner/repo/actions/runs/(\d+)/attempts/1", path)
            if match:
                return runs[int(match[1])]
            match = review.re.fullmatch(
                r"repos/owner/repo/actions/runs/(\d+)/artifacts\?name=ai-review-state-1-1&per_page=100", path
            )
            if match:
                return {"artifacts": [artifacts[int(match[1])]]}
            self.fail("Unexpected GitHub request: " + path)

        def artifact_download(repo, artifact):
            return review.decode_history(states[artifact["id"]])

        with tempfile.TemporaryDirectory() as directory, patch.object(
            review, "api", side_effect=transport
        ), patch.object(review, "download_history", side_effect=artifact_download):
            root = Path(directory)
            first_ids = None
            for round_number in (1, 2, 3):
                head = str(round_number) * 40
                work = root / str(round_number)
                (work / "source/src").mkdir(parents=True)
                (work / "source/src/app.py").write_text(
                    "one\ntwo\nreturn rows.filter(tenant_id=tenant_id)\nreturn balance - amount\n"
                )
                history = review.load_history("owner/repo", 1, "main")
                meta = {**self.meta, **history, "head": head, "anchors": {"src/app.py": {"LEFT": [], "RIGHT": [3, 4]}}}
                if round_number == 1:
                    value = {
                        "findings": [
                            {
                                "path": "src/app.py",
                                "line": 3,
                                "side": "RIGHT",
                                "priority": "P1",
                                "title": "租户过滤",
                                "body": "查询未限制租户。",
                            },
                            {
                                "path": "src/app.py",
                                "line": 4,
                                "side": "RIGHT",
                                "priority": "P2",
                                "title": "负数扣款",
                                "body": "负数金额增加余额。",
                            },
                        ],
                        "limitations": "",
                        "followups": [],
                    }
                else:
                    self.assertEqual([x["id"] for x in history["previous"]], first_ids)
                    value = {
                        "findings": [],
                        "limitations": "",
                        "followups": [
                            {**self.followup, "id": first_ids[0]},
                            {
                                "id": first_ids[1],
                                "status": "open" if round_number == 2 else "unknown",
                                "body": (
                                    "负数仍增加余额。"
                                    if round_number == 2
                                    else "处理已委托外部实现，当前快照不足以确认。"
                                ),
                                "evidence": (
                                    {"path": "src/app.py", "line": 4, "quote": "return balance - amount"}
                                    if round_number == 2
                                    else None
                                ),
                            },
                        ],
                    }
                review.validate_review(value, meta, work / "source")
                pr = {"head": {"sha": head}, "base": {"sha": meta["base"], "ref": "main"}}
                live.update(pr)
                (work / "metadata.json").write_text(json.dumps(meta))
                (work / "review.json").write_text(json.dumps(value))
                with patch.object(review, "event_context", return_value=({}, "owner/repo", pr, 1)), patch.dict(
                    os.environ, {"GITHUB_RUN_ID": str(round_number), "GITHUB_RUN_ATTEMPT": "1"}
                ):
                    review.stage_publication(work)
                    payload = io.BytesIO()
                    with zipfile.ZipFile(payload, "w") as archive:
                        archive.writestr("state.json", (work / "state.json").read_bytes())
                    states[round_number] = payload.getvalue()
                    artifacts[round_number] = {
                        "id": round_number,
                        "name": "ai-review-state-1-1",
                        "expired": False,
                        "workflow_run": {"id": round_number},
                    }
                    runs[round_number] = {
                        "id": round_number,
                        "run_attempt": 1,
                        "workflow_id": 9,
                        "path": ".github/workflows/code_review.yml",
                        "event": "pull_request_target",
                        "repository": {"full_name": "owner/repo"},
                        "status": "completed",
                        "conclusion": "success",
                    }
                    review.publish(work)
                    review.publish(work)
                state = json.loads((work / "state.json").read_text())
                if first_ids is None:
                    first_ids = [x["id"] for x in state["items"]]
                    for issue_id in first_ids:
                        self.assertIn(issue_id, comments[0]["body"])
                self.assertEqual([x["id"] for x in state["items"]], first_ids)
                self.assertEqual(len(comments), round_number)
            final = review.load_history("owner/repo", 1, "main")
            self.assertEqual([x["status"] for x in final["previous"]], ["resolved", "unknown"])
            self.assertIn("无法确认", comments[-1]["body"])
            self.assertIn("#issuecomment-20", comments[-1]["body"])
            # A cancelled newest run falls back to the successful state, never an empty review.
            runs[3]["conclusion"] = "cancelled"
            restored = review.load_history("owner/repo", 1, "main")
            self.assertEqual(restored["history_pointer"], {"run_id": 2, "run_attempt": 1})
            self.assertEqual([x["status"] for x in restored["previous"]], ["resolved", "open"])
            self.assertIn("最近一轮", restored["history_note"])
            # A PR retarget must not reuse conclusions from another target.
            retargeted = review.load_history("owner/repo", 1, "lts")
            self.assertEqual(retargeted["previous"], [])
            self.assertIn("目标分支", retargeted["history_note"])
            artifacts[2]["expired"] = True
            unavailable = review.load_history("owner/repo", 1, "main")
            self.assertEqual(unavailable["previous"], [])
            self.assertIn("不能确认", unavailable["history_note"])
            count = len(writes)
            live["head"] = {"sha": "f" * 40}
            with patch.object(review, "event_context", return_value=({}, "owner/repo", pr, 1)), patch.dict(
                os.environ, {"GITHUB_RUN_ID": "3", "GITHUB_RUN_ATTEMPT": "1"}
            ), self.assertRaisesRegex(ValueError, "stale"):
                review.publish(work)
            self.assertEqual(len(writes), count)

    def test_human_comments_cannot_supply_history_pointers(self):
        comment = {
            "id": 5,
            "user": {"login": "outsider"},
            "body": review.MARKER + "\n" + review.HISTORY_MARKER + '[{"run_id":999,"run_attempt":1}] -->',
        }
        with patch.object(review, "api", return_value=[comment]) as api:
            value = review.load_history("owner/repo", 1, "main")
        self.assertEqual(value["previous"], [])
        self.assertEqual(api.call_count, 1)

    def test_artifact_redirect_does_not_forward_github_bearer(self):
        import hashlib
        import io
        import zipfile
        from email.message import Message

        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("state.json", '{"version":1}')
        content = payload.getvalue()
        calls = []
        headers = Message()
        headers["Location"] = "https://example.blob.core.windows.net/signed?sig=example"

        class Opener:
            def open(self, request, timeout):
                calls.append(request)
                if len(calls) == 1:
                    raise review.urllib.error.HTTPError(request.full_url, 302, "Found", headers, io.BytesIO())
                return io.BytesIO(content)

        artifact = {"id": 10, "size_in_bytes": len(content), "digest": "sha256:" + hashlib.sha256(content).hexdigest()}
        with patch.dict(os.environ, {"GH_TOKEN": "unit-test-github-secret"}), patch.object(
            review.urllib.request, "build_opener", return_value=Opener()
        ):
            self.assertEqual(review.download_history("owner/repo", artifact), {"version": 1})
        self.assertEqual(calls[0].get_header("Authorization"), "Bearer unit-test-github-secret")
        self.assertIsNone(calls[1].get_header("Authorization"))
        calls.clear()
        artifact["digest"] = "sha256:" + "0" * 64
        with patch.dict(os.environ, {"GH_TOKEN": "unit-test-github-secret"}), patch.object(
            review.urllib.request, "build_opener", return_value=Opener()
        ), self.assertRaisesRegex(ValueError, "digest"):
            review.download_history("owner/repo", artifact)

    def test_history_capacity_failure_does_not_silently_drop_unresolved_items(self):
        previous = [{**self.item, "id": "F-%012x" % i} for i in range(40)]
        value = {
            "findings": [
                {
                    "path": "src/app.py",
                    "line": 3,
                    "side": "RIGHT",
                    "priority": "P1",
                    "title": "新问题",
                    "body": "有效依据",
                }
            ],
            "limitations": "",
            "followups": [
                {"id": x["id"], "status": "unknown", "body": "缺少上下文", "evidence": None} for x in previous
            ],
        }
        metadata = {**self.meta, "previous": previous, "anchors": {"src/app.py": {"RIGHT": [3], "LEFT": []}}}
        with self.assertRaisesRegex(ValueError, "40"):
            review.validate_review(value, metadata)

    def test_stage_cli_writes_state_before_any_publication(self):
        import io
        import runpy

        pr = {
            "head": {"sha": self.meta["head"]},
            "base": {"sha": self.meta["base"], "ref": "main", "repo": {"full_name": "owner/repo"}},
        }
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            (work / "metadata.json").write_text(json.dumps(self.meta))
            (work / "review.json").write_text(
                json.dumps({"findings": [], "limitations": "", "followups": [self.followup]})
            )
            event = work / "event.json"
            event.write_text(json.dumps({"number": 1, "pull_request": pr}))
            requests = []

            def respond(request, timeout):
                requests.append(request)
                return io.BytesIO(json.dumps({**pr, "state": "open", "draft": False}).encode())

            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_PATH": str(event),
                    "GITHUB_REPOSITORY": "owner/repo",
                    "GH_TOKEN": "unit-test-token",
                    "GITHUB_RUN_ID": "101",
                    "GITHUB_RUN_ATTEMPT": "1",
                },
            ), patch("sys.argv", [str(Path(review.__file__)), "stage", "--work-dir", str(work)]), patch(
                "urllib.request.urlopen", side_effect=respond
            ):
                runpy.run_path(str(Path(review.__file__)), run_name="__main__")
            self.assertTrue((work / "state.json").is_file())
            self.assertEqual([r.get_method() for r in requests], ["GET"])

    def test_resolved_history_can_be_archived_without_blocking_new_findings(self):
        previous = [{**self.item, "id": "F-%012x" % i} for i in range(40)]
        value = {
            "findings": [
                {
                    "path": "src/app.py",
                    "line": 3,
                    "side": "RIGHT",
                    "priority": "P1",
                    "title": "新问题",
                    "body": "新问题依据",
                }
            ],
            "limitations": "",
            "followups": [{**self.followup, "id": x["id"]} for x in previous],
        }
        metadata = {**self.meta, "previous": previous, "anchors": {"src/app.py": {"RIGHT": [3], "LEFT": []}}}
        review.validate_review(value, metadata)
        with patch.dict(os.environ, {"GITHUB_RUN_ID": "101", "GITHUB_RUN_ATTEMPT": "1"}):
            state = review.build_state(value, metadata)
        self.assertEqual(len(state["items"]), 40)
        self.assertEqual(sum(x["status"] == "open" for x in state["items"]), 1)
        self.assertIn("已归档 1 个已修复问题", review.render_review(value, metadata))
        # Every old result remains explicitly visible in this round, even if retired from future tracking.
        for old in previous:
            self.assertIn(old["id"], review.render_followups(value, metadata))

    def test_history_gap_survives_later_successful_rounds(self):
        value = {"findings": [], "limitations": "", "followups": [self.followup]}
        metadata = {**self.meta, "history_note": "中间轮次的问题未确认。"}
        with patch.dict(os.environ, {"GITHUB_RUN_ID": "101", "GITHUB_RUN_ATTEMPT": "1"}):
            state = review.build_state(value, metadata)
        self.assertEqual(state.get("history_note"), "中间轮次的问题未确认。")


if __name__ == "__main__":
    unittest.main()

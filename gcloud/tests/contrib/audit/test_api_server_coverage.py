# -*- coding: utf-8 -*-
import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]

AUDITED_API_FILES = {
    "create_task.py": "bk_audit_add_event_on_commit",
    "create_and_start_task.py": "bk_audit_add_event_on_commit",
    "fast_create_task.py": "bk_audit_add_event_on_commit",
    "start_task.py": "bk_audit_add_event_on_commit",
    "operate_task.py": "bk_audit_add_event_on_commit",
    "operate_node.py": "bk_audit_add_event_on_commit",
    "node_callback.py": "bk_audit_add_event_on_commit",
    "modify_constants_for_task.py": "bk_audit_add_event_on_commit",
    "create_periodic_task.py": "bk_audit_add_event_on_commit",
    "set_periodic_task_enabled.py": "bk_audit_add_event_on_commit",
    "modify_cron_for_periodic_task.py": "bk_audit_add_event_on_commit",
    "modify_constants_for_periodic_task.py": "bk_audit_add_event_on_commit",
    "create_clocked_task.py": "bk_audit_add_event_on_commit",
    "create_template.py": "bk_audit_add_event_on_commit",
    "import_project_template.py": "audit_imported_templates",
    "import_common_template.py": "audit_imported_templates",
    "copy_template_across_project.py": "audit_imported_templates",
    "register_project.py": "bk_audit_add_event_on_commit",
    "claim_functionalization_task.py": "bk_audit_add_event_on_commit",
    "apply_webhook_configs.py": "bk_audit_add_event_on_commit",
    "modify_project_executor_proxy.py": "bk_audit_add_event_on_commit",
    "modify_template_notify.py": "bk_audit_add_event_on_commit",
    "modify_template_executor_proxy.py": "bk_audit_add_event_on_commit",
}

AUDITED_PAGE_FILES = {
    "gcloud/clocked_task/viewset.py": "bk_audit_add_event_on_commit",
    "gcloud/periodictask/api.py": "bk_audit_add_event_on_commit",
    "gcloud/contrib/function/api.py": "bk_audit_add_event_on_commit",
    "gcloud/core/apis/drf/viewsets/appmaker.py": "bk_audit_add_event_on_commit",
    "gcloud/core/apis/drf/viewsets/periodic_task.py": "bk_audit_add_event_on_commit",
    "gcloud/core/apis/drf/viewsets/project.py": "bk_audit_add_event_on_commit",
    "gcloud/core/apis/drf/viewsets/project_config.py": "bk_audit_add_event_on_commit",
    "gcloud/core/apis/drf/viewsets/taskflow.py": "bk_audit_add_event_on_commit",
    "gcloud/taskflow3/apis/django/api.py": "bk_audit_add_event_on_commit",
    "gcloud/taskflow3/apis/django/v4/node_action.py": "bk_audit_add_event_on_commit",
    "gcloud/taskflow3/apis/drf/viewsets/update_task_constants.py": "bk_audit_add_event_on_commit",
    "gcloud/template_base/apis/django/api.py": "audit_imported_templates",
    "gcloud/template_base/apis/drf/viewsets/template.py": "audit_deleted_templates",
}


def _called_names(path):
    tree = ast.parse(path.read_text())
    return {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}


@pytest.mark.parametrize("filename,expected_call", sorted(AUDITED_API_FILES.items()))
def test_api_server_write_endpoint_registers_audit_event(filename, expected_call):
    path = REPO_ROOT / "gcloud" / "apigw" / "views" / filename
    assert expected_call in _called_names(path), "{} does not call {}".format(filename, expected_call)


@pytest.mark.parametrize("relative_path,expected_call", sorted(AUDITED_PAGE_FILES.items()))
def test_page_write_endpoint_registers_audit_event(relative_path, expected_call):
    path = REPO_ROOT / relative_path
    assert expected_call in _called_names(path), "{} does not call {}".format(relative_path, expected_call)


@pytest.mark.parametrize(
    "relative_path",
    [
        "gcloud/apigw/views/plugin_gateway.py",
        "gcloud/core/apis/drf/viewsets/package_source.py",
        "gcloud/core/apis/drf/viewsets/sync_task.py",
    ],
)
def test_deferred_endpoints_do_not_report_audit_events(relative_path):
    path = REPO_ROOT / relative_path
    if path.exists():
        assert "bk_audit_add_event" not in path.read_text()

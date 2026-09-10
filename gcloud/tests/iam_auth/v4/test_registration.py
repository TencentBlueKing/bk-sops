import copy
import importlib
from unittest import mock

from django.conf import settings
from django.core.management.base import CommandError
from django.db import migrations
from django.test import SimpleTestCase, override_settings

from gcloud.iam_auth.api_v4.resources import (
    BatchCreateActionResource,
    BatchCreateResourceTypeResource,
    BatchCreateRoleResource,
    CreateSystemResource,
    ListActionResource,
    ListResourceTypeResource,
    ListRoleResource,
    RetrieveSystemResource,
    UpdateRoleResource,
)
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES
from gcloud.iam_auth.exceptions import IAMV4ProtocolError, IAMV4Unavailable
from gcloud.iam_auth.management.commands import register_iam_v4_model as model_command
from gcloud.iam_auth.management.commands import register_iam_v4_roles as role_command
from gcloud.iam_auth.model_registration import register_base_model, validate_created_ids
from gcloud.iam_auth.model_validation import load_models, validate_models


@override_settings(BK_IAM_RESOURCE_API_HOST="https://sops.example.test")
class BaseModelRegistrationContractTest(SimpleTestCase):
    def setUp(self):
        self.model, self.roles = load_models()

    def test_gateway_model_contains_only_v4_contract_objects(self):
        self.assertEqual(set(self.model), {"system", "resource_types", "actions"})
        self.assertEqual(len(self.model["resource_types"]), 7)
        self.assertEqual(len(self.model["actions"]), 42)
        serialized = repr(self.model)
        for v3_field in (
            "operations",
            "instance_selection",
            "action_group",
            "provider_config",
            "related_resource_types",
        ):
            self.assertNotIn(v3_field, serialized)

    @override_settings(BK_IAM_RESOURCE_API_HOST="https://sops.example.test/base/")
    def test_system_and_callback_contract_match_current_application(self):
        model, _ = load_models()
        system = model["system"]
        self.assertEqual(system["id"], settings.BK_IAM_SYSTEM_ID)
        self.assertIn(settings.APP_CODE, system["clients"])
        self.assertEqual(system["callback_url"], "https://sops.example.test/base/iam/resource/api/v4/")

    def test_resource_ancestors_and_action_bindings_are_exact(self):
        resources = {item["id"]: item for item in self.model["resource_types"]}
        expected = {
            "project": [],
            "flow": ["project"],
            "task": ["project"],
            "common_flow": [],
            "mini_app": ["project"],
            "periodic_task": ["project"],
            "clocked_task": ["project"],
        }
        self.assertEqual({key: value["ancestors"] for key, value in resources.items()}, expected)
        actions = {item["id"]: item for item in self.model["actions"]}
        self.assertEqual(set(actions), set(ACTION_RESOURCE_TYPES))
        for action_id, resource_type in ACTION_RESOURCE_TYPES.items():
            self.assertEqual(actions[action_id]["resource_type_id"], resource_type or "")

    def test_model_validation_rejects_v3_only_fields(self):
        broken = copy.deepcopy(self.model)
        broken["resource_types"][0]["provider_config"] = {"path": "/iam/resource/api/v4/"}
        with self.assertRaisesRegex(IAMV4ProtocolError, "outside the IAM V4 gateway contract"):
            validate_models(broken, self.roles)

    @mock.patch("gcloud.iam_auth.model_registration._api_request")
    def test_registration_calls_gateway_in_dependency_order(self, api_request):
        def response(resource, payload, *args, **kwargs):
            if isinstance(resource, RetrieveSystemResource):
                return None
            if isinstance(resource, CreateSystemResource):
                return {"id": settings.BK_IAM_SYSTEM_ID}
            if isinstance(resource, (ListResourceTypeResource, ListActionResource, ListRoleResource)):
                return {"count": 0, "results": []}
            if isinstance(resource, BatchCreateResourceTypeResource):
                key = "resource_types"
            elif isinstance(resource, BatchCreateActionResource):
                key = "actions"
            else:
                key = "roles"
            return [item["id"] for item in reversed(payload[key])]

        api_request.side_effect = response
        self.assertEqual(
            register_base_model("tenant-a"),
            {"systems": 1, "system_status": "created", "resources": 7, "actions": 42, "roles": 9},
        )
        self.assertEqual(
            [type(call.args[0]) for call in api_request.call_args_list],
            [
                RetrieveSystemResource,
                CreateSystemResource,
                ListResourceTypeResource,
                BatchCreateResourceTypeResource,
                ListActionResource,
                BatchCreateActionResource,
                ListRoleResource,
                BatchCreateRoleResource,
            ],
        )
        for call in api_request.call_args_list:
            self.assertEqual(call.args[1]["tenant_id"], "tenant-a")

    def test_created_id_validation_rejects_invalid_results(self):
        for value in (["one"], ["one", "one"], [{"id": "one"}]):
            with self.subTest(value=value), self.assertRaises(IAMV4ProtocolError):
                validate_created_ids(value, ["one", "two"], "action")

    @mock.patch("gcloud.iam_auth.model_registration._api_request")
    def test_registration_is_a_read_only_noop_when_remote_model_matches(self, api_request):
        api_request.side_effect = [
            self.model["system"],
            {"count": 7, "results": self.model["resource_types"]},
            {"count": 42, "results": self.model["actions"]},
            {"count": 9, "results": self.roles},
        ]
        result = register_base_model("tenant-a")
        self.assertEqual(result["system_status"], "unchanged")
        self.assertEqual(api_request.call_count, 4)
        self.assertTrue(all(call.args[0].method == "GET" for call in api_request.call_args_list))

    @mock.patch("gcloud.iam_auth.model_registration._api_request")
    def test_registration_creates_only_missing_roles_and_updates_role_metadata(self, api_request):
        remote_roles = copy.deepcopy(self.roles[:-1])
        remote_roles[0]["name"] = "old name"
        api_request.side_effect = [
            self.model["system"],
            {"count": 7, "results": self.model["resource_types"]},
            {"count": 42, "results": self.model["actions"]},
            {"count": len(remote_roles), "results": remote_roles},
            [self.roles[-1]["id"]],
            None,
        ]

        register_base_model("tenant-a")

        create_resource, create_payload = api_request.call_args_list[4].args
        self.assertIsInstance(create_resource, BatchCreateRoleResource)
        self.assertEqual(create_payload["roles"], [self.roles[-1]])
        update_resource, update_payload = api_request.call_args_list[5].args
        self.assertIsInstance(update_resource, UpdateRoleResource)
        self.assertEqual(update_payload["role_id"], self.roles[0]["id"])
        self.assertEqual(update_payload["name"], self.roles[0]["name"])

    @mock.patch("gcloud.iam_auth.model_registration._api_request")
    def test_registration_rejects_existing_role_action_drift(self, api_request):
        remote_roles = copy.deepcopy(self.roles)
        remote_roles[0]["actions"] = remote_roles[0]["actions"][1:]
        api_request.side_effect = [
            self.model["system"],
            {"count": 7, "results": self.model["resource_types"]},
            {"count": 42, "results": self.model["actions"]},
            {"count": 9, "results": remote_roles},
        ]
        with self.assertRaisesRegex(IAMV4ProtocolError, "role actions cannot be updated"):
            register_base_model("tenant-a")

    @mock.patch("gcloud.iam_auth.model_registration._api_request")
    def test_registration_rejects_existing_action_binding_drift(self, api_request):
        remote_actions = copy.deepcopy(self.model["actions"])
        remote_actions[0]["resource_type_id"] = "project"
        api_request.side_effect = [
            self.model["system"],
            {"count": 7, "results": self.model["resource_types"]},
            {"count": 42, "results": remote_actions},
        ]
        with self.assertRaisesRegex(IAMV4ProtocolError, "resource_type_id cannot be updated"):
            register_base_model("tenant-a")


@override_settings(BK_IAM_RESOURCE_API_HOST="https://sops.example.test")
class MigrationAndRegistrationCommandTest(SimpleTestCase):
    def test_legacy_v3_migrations_are_noops_without_sdk_imports(self):
        migration_names = [
            "0001_initial",
            "0002_bk_sops_202007091136",
            "0003_bk_sops_202007221549",
            "0004_bk_sops_202008051941",
            "0005_bk_sops_202012081507",
            "0006_bk_sops_202106171007",
            "0007_bk_sops_202109011700",
            "0008_bk_sops_202109261155",
            "0009_bk_sops_202109261155",
            "0010_bk_sops_202109261155",
            "0011_bk_sops_202109261155",
            "0012_bk_sops_202111251154",
            "0013_bk_sops_202203010917",
            "0014_bk_sops_202209211105",
            "0015_bk_sops_202212122120",
        ]
        for migration_name in migration_names:
            with self.subTest(migration=migration_name):
                migration = importlib.import_module("bksops_iam_migrations.migrations.{}".format(migration_name))
                self.assertFalse(hasattr(migration, "IAMMigrator"))
                self.assertIs(migration.Migration.operations[0].code, migrations.RunPython.noop)

    def test_migration_0016_uses_gateway_registrar_instead_of_iam_sdk(self):
        migration = importlib.import_module("bksops_iam_migrations.migrations.0016_bk_sops_iam_v4_model")
        with override_settings(IAM_V4_MODEL_REGISTRATION_TENANT_ID="tenant-a", BK_IAM_SKIP=False), mock.patch.object(
            migration, "register_base_model"
        ) as registrar:
            migration.forward_func(None, None)
        registrar.assert_called_once_with("tenant-a")
        self.assertFalse(hasattr(migration, "IAMMigrator"))

    def test_migration_honors_existing_iam_skip_switch(self):
        migration = importlib.import_module("bksops_iam_migrations.migrations.0016_bk_sops_iam_v4_model")
        with override_settings(BK_IAM_SKIP=True), mock.patch.object(migration, "register_base_model") as registrar:
            migration.forward_func(None, None)
        registrar.assert_not_called()

    def test_migration_does_not_treat_false_string_as_skip(self):
        migration = importlib.import_module("bksops_iam_migrations.migrations.0016_bk_sops_iam_v4_model")
        with override_settings(IAM_V4_MODEL_REGISTRATION_TENANT_ID="tenant-a", BK_IAM_SKIP="False"), mock.patch.object(
            migration, "register_base_model"
        ) as registrar:
            migration.forward_func(None, None)
        registrar.assert_called_once_with("tenant-a")

    def test_corrective_migration_retries_registration_after_0016(self):
        migration = importlib.import_module("bksops_iam_migrations.migrations.0017_retry_bk_sops_iam_v4_model")
        with override_settings(IAM_V4_MODEL_REGISTRATION_TENANT_ID="tenant-a", BK_IAM_SKIP=False), mock.patch.object(
            migration, "register_base_model"
        ) as registrar:
            migration.forward_func(None, None)
        registrar.assert_called_once_with("tenant-a")

    def test_migration_0018_synchronizes_roles_without_rewriting_base_model(self):
        migration = importlib.import_module("bksops_iam_migrations.migrations.0018_sync_bk_sops_iam_v4_roles")
        with override_settings(IAM_V4_MODEL_REGISTRATION_TENANT_ID="tenant-a", BK_IAM_SKIP=False), mock.patch.object(
            migration, "register_roles"
        ) as registrar:
            migration.forward_func(None, None)
        registrar.assert_called_once_with("tenant-a")

    @mock.patch.object(model_command, "register_base_model")
    def test_model_dry_run_validates_without_writing_iam(self, registrar):
        model_command.Command().handle(tenant_id="system", dry_run=True)
        registrar.assert_not_called()

    @mock.patch.object(role_command, "register_roles")
    def test_role_dry_run_validates_without_writing_iam(self, registrar):
        role_command.Command().handle(tenant_id="system", dry_run=True)
        registrar.assert_not_called()

    @mock.patch.object(role_command, "register_roles")
    def test_role_registration_uses_idempotent_role_synchronizer(self, registrar):
        role_command.Command().handle(tenant_id="tenant-a", dry_run=False)
        registrar.assert_called_once_with("tenant-a")

    @mock.patch.object(role_command, "register_roles", side_effect=IAMV4Unavailable())
    def test_role_registration_maps_iam_unavailable_to_command_error(self, unused):
        with self.assertRaises(CommandError):
            role_command.Command().handle(tenant_id="tenant-a", dry_run=False)

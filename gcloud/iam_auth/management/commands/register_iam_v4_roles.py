from django.core.management.base import BaseCommand, CommandError

from gcloud.iam_auth.exceptions import IAMV4Error, IAMV4ProtocolError
from gcloud.iam_auth.model_registration import register_roles
from gcloud.iam_auth.model_validation import load_models, validate_models


def validate_registration_response(data, role_ids):
    if not isinstance(data, list):
        raise IAMV4ProtocolError("role API data must be a list")
    if any(not isinstance(role_id, str) for role_id in data):
        raise IAMV4ProtocolError("role API data must contain role ids")
    if len(data) != len(set(data)) or set(data) != set(role_ids):
        raise IAMV4ProtocolError("role API response is incomplete")


class Command(BaseCommand):
    help = "Register bk-sops IAM V4 roles"

    def add_arguments(self, parser):
        parser.add_argument("--tenant-id", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        model, roles = load_models()
        try:
            validate_models(model, roles)
        except IAMV4ProtocolError as error:
            raise CommandError(str(error)) from error
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("IAM V4 role model validation passed (dry-run)"))
            return
        try:
            register_roles(options["tenant_id"])
        except IAMV4Error as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS("IAM V4 roles synchronized"))

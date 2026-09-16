from django.core.management.base import BaseCommand, CommandError

from gcloud.iam_auth.exceptions import IAMV4Error
from gcloud.iam_auth.model_registration import register_base_model
from gcloud.iam_auth.model_validation import validate_local_models


class Command(BaseCommand):
    help = "Register the bk-sops base model through the IAM V4 API gateway"

    def add_arguments(self, parser):
        parser.add_argument("--tenant-id", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        if options["dry_run"]:
            validate_local_models()
            self.stdout.write(self.style.SUCCESS("IAM V4 gateway model validation passed (dry-run)"))
            return
        try:
            result = register_base_model(options["tenant_id"])
        except IAMV4Error as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "IAM V4 gateway model registered: 1 system, {} resource types, {} actions, {} roles".format(
                    result["resources"], result["actions"], result["roles"]
                )
            )
        )

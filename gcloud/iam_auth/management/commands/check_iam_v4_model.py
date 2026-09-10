from django.core.management.base import BaseCommand, CommandError

from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.model_validation import validate_local_models


class Command(BaseCommand):
    help = "Validate the local bk-sops IAM V4 model and roles"

    def handle(self, *args, **options):
        try:
            counts = validate_local_models()
        except IAMV4ProtocolError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "IAM V4 model validation passed: 1 system / {resources} resources / "
                "{actions} actions / {roles} roles".format(**counts)
            )
        )

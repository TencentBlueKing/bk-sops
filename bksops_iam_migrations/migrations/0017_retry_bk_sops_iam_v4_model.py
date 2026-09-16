from django.conf import settings
from django.db import migrations

from gcloud.iam_auth.model_registration import register_base_model


def forward_func(apps, schema_editor):
    skip_registration = getattr(settings, "BK_IAM_SKIP", False)
    if isinstance(skip_registration, str):
        skip_registration = skip_registration.strip().lower() in {"1", "true", "yes", "on"}
    if skip_registration:
        return
    register_base_model(settings.IAM_V4_MODEL_REGISTRATION_TENANT_ID)


class Migration(migrations.Migration):
    dependencies = [("bksops_iam_migrations", "0016_bk_sops_iam_v4_model")]
    operations = [migrations.RunPython(forward_func)]

from django.conf import settings


def build_iam_v4_api_url():
    override = getattr(settings, "BK_IAM_V4_API_URL", "")
    if override:
        return override.rstrip("/")

    template = getattr(settings, "BK_API_URL_TMPL", "")
    if not template:
        return ""
    endpoint = template.format(api_name=settings.BKIAM_APIGW_NAME).rstrip("/")
    stage_name = getattr(settings, "BK_APIGW_STAGE_NAME", "stage")
    return "{}/{}".format(endpoint, stage_name.strip("/"))
